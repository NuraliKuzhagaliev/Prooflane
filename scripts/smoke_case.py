"""Real HTTP source-to-case-to-packet flow, with actual Docker and no model calls."""
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


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default="http://127.0.0.1:8765")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "artifacts" / "transformation")
    args = parser.parse_args()
    base_url = args.base_url.rstrip("/")
    out = args.output_dir.resolve()
    out.mkdir(parents=True, exist_ok=True)
    report = {"at": datetime.now(timezone.utc).isoformat(), "scope": "REAL_HTTP_REFERENCE_AND_FIXED_DOCKER_NO_VULTR",
              "base_url": base_url, "model_calls": 0, "passed": False, "checks": [], "cases": []}
    headers = {"X-Prooflane-Request": "1", "Origin": base_url}

    def check(name, passed):
        report["checks"].append({"name": name, "passed": bool(passed)})
        if not passed:
            raise AssertionError(name)

    try:
        with httpx.Client(base_url=base_url, timeout=60, trust_env=False) as client, \
                httpx.Client(base_url=base_url, timeout=60, trust_env=False) as stranger:
            sample = client.get("/api/cases/sample").json()
            sources = {k: sample[k] for k in ("invoices_csv", "contracts_csv")}
            unresolved = client.post("/api/cases/match", headers=headers, json=sources).json()
            check("Two sources expose overlap and missing contract", unresolved["counts"]["unresolved"] == 2 and not unresolved["ready"])
            decisions = {"selections": {"5": "C2R"}, "exclusions": {"7": "No active supplied contract; excluded from this review"}}
            resolved = client.post("/api/cases/match", headers=headers, json={**sources, **decisions}).json()
            check("Explicit scope 7 of 8", resolved["ready"] and resolved["counts"] == {"total": 8, "matched": 6, "selected": 1, "unresolved": 0, "excluded": 1})
            for mode in ("reference", "sandbox"):
                response = client.post("/api/cases", headers=headers, json={"name": mode + " supplier case", "mode": mode, **sources, **decisions})
                check(mode + " case HTTP", response.status_code == 200)
                case = response.json()["case"]
                path = "/api/cases/" + case["id"]
                check(mode + " manual baseline", case["baseline"]["summary"]["total_variance"] == "768.00" and case["baseline"]["summary"]["total_billed"] == "7110.00")
                boundary = case["priority_switch"]["transitions"][0]
                check(mode + " priority boundary and exact tie", boundary["at"]["price"] == "82.60"
                      and [row["row"] for row in boundary["at"]["leaders"]] == [2, 4]
                      and boundary["beyond"]["leaders"][0]["row"] == 4)
                original = client.get(f"/api/runs/{case['baseline']['id']}/receipt").json()
                changed = client.post(path + "/variants", headers=headers, json={"revision": case["revision"], "name": "Shared price 80", "changes": [{"target": "contract:C1", "value": "80.00"}]})
                check(mode + " shared alternative HTTP", changed.status_code == 200)
                case = changed.json()["case"]
                first = case["variants"][0]
                check(mode + " all bound records changed", first["changed_rows"] == [2, 3, 8] and first["run"]["summary"]["total_variance"] == "368.00" and first["delta"]["total_variance"] == "-400.00")
                changed = client.post(path + "/variants", headers=headers, json={"revision": case["revision"], "name": "Price and volume", "changes": [{"target": "contract:C1", "value": "80.00"}, {"target": "row:2:quantity", "value": "80"}]})
                check(mode + " joint alternative HTTP", changed.status_code == 200)
                case = changed.json()["case"]
                check(mode + " joint recomputation manual oracle", case["variants"][1]["run"]["summary"]["total_variance"] == "568.00" and case["variants"][1]["delta"]["total_billed"] == "3400.00")
                changed = client.post(path + "/bounds", headers=headers, json={"revision": case["revision"], "bounds": [{"target": "contract:C1", "low": "65.00", "high": "85.00"}]})
                check(mode + " bounds HTTP", changed.status_code == 200)
                case = changed.json()["case"]
                info = case["intelligence"]
                check(mode + " exact uncertainty and evidence priority", (info["low"], info["high"], info["width"]) == ("148.00", "1193.00", "1045.00") and info["review_queue"][0]["guaranteed_width_reduction"] == "1045.00")
                check(mode + " stale revision conflict", client.post(path + "/bounds", headers=headers, json={"revision": 1, "bounds": []}).status_code == 409)
                check(mode + " original immutable", original == client.get(f"/api/runs/{case['baseline']['id']}/receipt").json())
                response = client.get(path + "/packet")
                check(mode + " downloadable packet", response.status_code == 200 and "attachment" in response.headers["content-disposition"])
                packet = response.json()
                packet_path = out / (mode + "-case.json")
                packet_path.write_bytes(response.content)
                cli = subprocess.run([sys.executable, str(ROOT / "scripts/verify_receipt.py"), str(packet_path)], capture_output=True, text=True, timeout=30)
                check(mode + " independent offline CLI", cli.returncode == 0 and json.loads(cli.stdout)["passed"])
                check(mode + " browser verification API", client.post("/api/verify-packet", headers=headers, json=packet).json()["passed"])
                forged_boundary = copy.deepcopy(packet)
                forged_boundary["priority_switch"]["transitions"][0]["at"]["price"] = "82.61"
                forged_boundary["case_sha256"] = digest(canonical({k: v for k, v in forged_boundary.items() if k != "case_sha256"}))
                check(mode + " rehashed false boundary rejected", client.post("/api/verify-packet", headers=headers, json=forged_boundary).json()["passed"] is False)
                forged = copy.deepcopy(packet)
                forged["intelligence"]["review_queue"][0]["guaranteed_width_reduction"] = "99999.00"
                forged["case_sha256"] = digest(canonical({k: v for k, v in forged.items() if k != "case_sha256"}))
                check(mode + " rehashed false priority rejected", client.post("/api/verify-packet", headers=headers, json=forged).json()["passed"] is False)
                for suffix in ("", "/packet"):
                    check(mode + " private case " + suffix, stranger.get(path + suffix).status_code == 404)
                check(mode + " child cannot become original", client.post("/api/cases", headers=headers, json={"name": "Invalid child", "baseline_run_id": first["id"]}).status_code == 422)
                response = client.post(path + "/bounds", headers=headers, json={"revision": case["revision"], "bounds": [
                    {"target": "contract:C1", "low": "65.00", "high": "85.00"},
                    {"target": "row:2:quantity", "low": "20", "high": "80"}]})
                check(mode + " two-range HTTP", response.status_code == 200)
                multi = response.json()["case"]["intelligence"]
                check(mode + " two joint unknowns", (multi["low"], multi["high"], multi["width"]) == ("148.00", "1993.00", "1845.00"))
                priority = {q["target"]: q for q in multi["review_queue"]}
                check(mode + " guaranteed versus possible information value", priority["contract:C1"]["guaranteed_width_reduction"] == "645.00"
                      and priority["contract:C1"]["possible_width_reduction"] == "1845.00"
                      and priority["row:2:quantity"]["guaranteed_width_reduction"] == "0.00"
                      and priority["row:2:quantity"]["possible_width_reduction"] == "1200.00")
                multi_download = client.get(path + "/packet")
                check(mode + " multi-range download", multi_download.status_code == 200)
                multi_path = out / (mode + "-multi-range-case.json")
                multi_path.write_bytes(multi_download.content)
                multi_cli = subprocess.run([sys.executable, str(ROOT / "scripts/verify_receipt.py"), str(multi_path)], capture_output=True, text=True, timeout=30)
                check(mode + " multi-range offline CLI", multi_cli.returncode == 0 and json.loads(multi_cli.stdout)["passed"])
                for receipt in [packet["baseline"], *[v["receipt"] for v in packet["alternatives"]]]:
                    execution = receipt["execution"]
                    check(mode + " actual runtime " + receipt["run_id"], receipt["provenance"]["model_calls"] == 0
                          and execution["runtime"] == ("docker" if mode == "sandbox" else "trusted-reference")
                          and (mode != "sandbox" or execution["cleanup"] is True))
                report["cases"].append({"id": case["id"], "mode": mode, "packet": str(packet_path), "baseline": "768.00", "alternatives": ["368.00", "568.00"], "range": [info["low"], info["high"]],
                                        "multi_range_packet": str(multi_path), "multi_range": {k: multi[k] for k in ("low", "high", "width", "review_queue")}})
            containment = client.post("/api/containment", headers=headers, json={}).json()
            check("Live containment probes pass with verified cleanup", containment.get("passed") is True and containment.get("execution", {}).get("cleanup") is True)
            report["containment"] = containment
            report["passed"] = True
    except (AssertionError, ValueError, KeyError, httpx.HTTPError, subprocess.SubprocessError) as exc:
        report["error"] = str(exc)
    (out / "case-http-smoke.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({"passed": report["passed"], "checks": len(report["checks"]), "error": report.get("error"), "report": str(out / "case-http-smoke.json")}, indent=2))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
