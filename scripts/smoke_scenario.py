"""Exercise immutable scenarios through real HTTP; never calls an AI provider."""
import argparse
import copy
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from prooflane.analysis import canonical, digest
from prooflane.comparison import check_bundle


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default="http://127.0.0.1:8765")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "artifacts" / "optimization")
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    report = {"scope": "REAL_HTTP_REFERENCE_AND_FIXED_DOCKER_NOT_VULTR",
              "at": datetime.now(timezone.utc).isoformat(), "base_url": args.base_url,
              "model_calls": 0, "checks": [], "runs": [], "passed": False}

    def check(name, passed):
        report["checks"].append({"name": name, "passed": bool(passed)})
        if not passed:
            raise AssertionError(name)

    headers = {"X-Prooflane-Request": "1"}
    try:
        with httpx.Client(base_url=args.base_url, timeout=60, trust_env=False) as client, \
                httpx.Client(base_url=args.base_url, timeout=60, trust_env=False) as stranger:
            sample = client.get("/api/sample").json()
            for mode in ("reference", "sandbox"):
                response = client.post("/api/runs", headers=headers,
                                       json={"csv": sample["csv"], "mode": mode})
                check(mode + ": baseline HTTP", response.status_code == 200)
                baseline = response.json()
                check(mode + ": baseline verified", baseline["status"] == "verified")
                original = client.get(f"/api/runs/{baseline['id']}/receipt").json()
                source = client.get(f"/api/runs/{baseline['id']}/source").json()
                check(mode + ": source record", source["rows"][1]["contract_price"] == "72.00")
                payload = {"baseline_receipt_sha256": original["receipt_sha256"],
                           "row": 3, "field": "contract_price", "value": "80.00"}
                response = client.post(f"/api/runs/{baseline['id']}/scenario", headers=headers, json=payload)
                check(mode + ": scenario HTTP", response.status_code == 200)
                scenario = response.json()
                check(mode + ": scenario verified", scenario["status"] == "verified")
                comparison = scenario["comparison"]
                check(mode + ": manual expected totals", comparison["baseline"]["total_variance"] == "1480.00"
                      and comparison["scenario"]["total_variance"] == "1160.00"
                      and comparison["delta"]["total_variance"] == "-320.00"
                      and comparison["delta"]["total_billed"] == "0.00"
                      and comparison["change"]["before_variance"] == "520.00"
                      and comparison["change"]["after_variance"] == "200.00"
                      and comparison["unchanged_records"] == 23)
                check(mode + ": baseline immutable", original == client.get(f"/api/runs/{baseline['id']}/receipt").json())
                result = client.get(f"/api/runs/{scenario['id']}/comparison")
                check(mode + ": packet download", result.status_code == 200 and "attachment" in result.headers["content-disposition"])
                bundle = result.json()
                packet_path = args.output_dir / (mode + "-comparison.json")
                packet_path.write_text(json.dumps(bundle, indent=2) + "\n", encoding="utf-8")
                check(mode + ": independent bundle verification", check_bundle(bundle)["passed"])
                cli = subprocess.run([sys.executable, str(ROOT / "scripts" / "verify_receipt.py"), str(packet_path)],
                                     capture_output=True, text=True, timeout=20)
                check(mode + ": offline CLI", cli.returncode == 0 and json.loads(cli.stdout)["passed"])
                for receipt in (bundle["baseline"], bundle["scenario"]):
                    execution = receipt["execution"]
                    check(mode + ": honest runtime " + receipt["run_id"],
                          receipt["provenance"]["model_calls"] == 0
                          and receipt["provenance"]["mode"] == mode
                          and execution["runtime"] == ("docker" if mode == "sandbox" else "trusted-reference")
                          and (mode != "sandbox" or execution["cleanup"] is True))
                for run_id, suffix in ((baseline["id"], "/source"), (scenario["id"], "/comparison"),
                                       (scenario["id"], "/receipt")):
                    check(mode + ": foreign session denied " + suffix,
                          stranger.get(f"/api/runs/{run_id}{suffix}").status_code == 404)
                check(mode + ": stale baseline rejected", client.post(f"/api/runs/{baseline['id']}/scenario", headers=headers,
                      json={**payload, "baseline_receipt_sha256": "0" * 64}).status_code == 409)
                check(mode + ": recursive scenario rejected", client.post(f"/api/runs/{scenario['id']}/scenario", headers=headers,
                      json={**payload, "baseline_receipt_sha256": scenario["receipt_hash"]}).status_code == 422)
                tampered = copy.deepcopy(bundle)
                tampered["comparison"]["delta"]["total_variance"] = "-999.00"
                tampered["bundle_sha256"] = digest(canonical({k: v for k, v in tampered.items() if k != "bundle_sha256"}))
                try:
                    check_bundle(tampered)
                except ValueError:
                    rejected = True
                else:
                    rejected = False
                check(mode + ": rehashed false delta rejected", rejected)
                report["runs"].append({"mode": mode, "baseline_id": baseline["id"], "scenario_id": scenario["id"],
                                       "packet": str(packet_path), "comparison": comparison,
                                       "execution": scenario["execution"]})
            report["passed"] = True
    except (AssertionError, ValueError, KeyError, httpx.HTTPError, subprocess.SubprocessError) as exc:
        report["error"] = str(exc)
    (args.output_dir / "scenario-smoke.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"passed": report["passed"], "checks": len(report["checks"]),
                      "report": str(args.output_dir / "scenario-smoke.json"), "error": report.get("error")}))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
