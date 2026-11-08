"""Run synthetic, manually calculated cases against a real HTTP deployment.

Only reference/fixed-recipe modes are allowed; this never calls an AI provider.
The report records the target URL without claiming that it is hosted on Vultr.
"""
import argparse
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit

import httpx

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from prooflane.analysis import canonical, contract_output, digest
from prooflane.receipts import check_receipt

CORPUS = ROOT / "examples" / "evaluation"
HEADERS = {"X-Prooflane-Request": "1"}


def load_cases():
    return json.loads((CORPUS / "cases.json").read_text(encoding="utf-8"))["cases"]


def check_run(run, receipt, case, csv_text, mode):
    """Compare both artifacts to manual expectations, not just to each other."""
    def require(condition, message):
        if not condition:
            raise ValueError(message)

    require(run.get("status") == "verified", "Run was not verified")
    require(run.get("mode") == mode, "Unexpected run mode")
    require(canonical(contract_output(run["summary"])) == canonical(case["expected"]),
            "Run differs from manually calculated expected result")
    require(receipt["run_id"] == run["id"], "Receipt belongs to another run")
    require(receipt["input_csv"] == csv_text, "Receipt input differs from submitted CSV")
    require(canonical(receipt["output"]) == canonical(case["expected"]),
            "Receipt output differs from manually calculated expected result")
    require(receipt["receipt_sha256"] == run["receipt_hash"], "Run/receipt hash differs")
    require(receipt["provenance"]["mode"] == mode, "Unexpected receipt mode")
    require(receipt["provenance"]["model_calls"] == 0, "Unexpected model call")
    require(check_receipt(receipt)["passed"], "Receipt verification failed")
    expected_runtime = "docker" if mode == "sandbox" else "trusted-reference"
    for execution in (run["execution"], receipt["execution"]):
        require(execution.get("runtime") == expected_runtime, "Unexpected runtime")
        if mode == "sandbox":
            require(execution.get("cleanup") is True, "Docker cleanup was not confirmed")
            require(execution.get("exit_code") == 0, "Docker execution failed")


def evaluate_case(client, stranger, case, mode, receipt_dir):
    started = time.perf_counter()
    csv_text = (CORPUS / (case["id"] + ".csv")).read_text(encoding="utf-8")
    record = {"case": case["id"], "mode": mode, "passed": False,
              "input_sha256": digest(csv_text), "expected_status": case["expected_status"]}
    try:
        response = client.post("/api/runs", headers=HEADERS,
                               json={"csv": csv_text, "filename": case["id"] + ".csv", "mode": mode})
        record["http_status"] = response.status_code
        if response.status_code != case["expected_status"]:
            raise ValueError(f"Expected HTTP {case['expected_status']}, received {response.status_code}")
        payload = response.json()
        if case["expected_status"] == 422:
            if case["error_contains"] not in str(payload.get("detail", "")):
                raise ValueError("Validation did not report the expected input error")
            record["rejection"] = payload["detail"]
        else:
            if payload.get("status") != "verified":
                raise ValueError("Run failed: " + str(payload.get("error", "unknown failure"))[:300])
            run_id = payload["id"]
            receipt_response = client.get(f"/api/runs/{run_id}/receipt")
            receipt_response.raise_for_status()
            receipt = receipt_response.json()
            # Retain the actual receipt even if a later expectation check fails.
            receipt_path = receipt_dir / f"{mode}-{case['id']}.json"
            receipt_path.write_text(json.dumps(receipt, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
            record["receipt"] = str(receipt_path)
            check_run(payload, receipt, case, csv_text, mode)
            for suffix in ("", "/receipt"):
                if stranger.get(f"/api/runs/{run_id}{suffix}").status_code != 404:
                    raise ValueError("Another session can access the run or receipt")
            record.update({"result": receipt["output"], "receipt_sha256": receipt["receipt_sha256"],
                           "runtime": payload["execution"]["runtime"],
                           "cleanup": payload["execution"].get("cleanup"), "model_calls": 0,
                           "session_isolation": True})
        record["passed"] = True
    except (httpx.HTTPError, ValueError, KeyError, TypeError) as exc:
        record["error"] = str(exc)[:600]
    record["elapsed_ms"] = round((time.perf_counter() - started) * 1000, 2)
    return record


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default="http://127.0.0.1:8765")
    parser.add_argument("--mode", choices=("reference", "sandbox", "both"), default="both")
    parser.add_argument("--output", type=Path, default=ROOT / "artifacts" / "evaluation-local.json")
    args = parser.parse_args(argv)
    target = urlsplit(args.base_url)
    if (target.scheme not in ("http", "https") or not target.hostname or target.username
            or target.password or target.query or target.fragment or target.path not in ("", "/")):
        parser.error("Use an HTTP(S) origin without credentials, query, fragment or path")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    receipt_dir = args.output.parent / (args.output.stem + "-receipts")
    receipt_dir.mkdir(exist_ok=True)
    modes = ("reference", "sandbox") if args.mode == "both" else (args.mode,)
    report = {"scope": "HTTP acceptance with synthetic CSV; no live AI; hosting location not attested",
              "at": datetime.now(timezone.utc).isoformat(), "target": args.base_url,
              "expected_values": "manually calculated examples/evaluation/cases.json",
              "cases": [], "live_model": "NOT_RUN", "passed": False}
    with httpx.Client(base_url=args.base_url, timeout=60, trust_env=False) as client, \
            httpx.Client(base_url=args.base_url, timeout=15, trust_env=False) as stranger:
        for mode in modes:
            for case in load_cases():
                record = evaluate_case(client, stranger, case, mode, receipt_dir)
                report["cases"].append(record)
                print(f"{'PASS' if record['passed'] else 'FAIL'} {mode}/{case['id']}", flush=True)
    report["passed"] = bool(report["cases"]) and all(case["passed"] for case in report["cases"])
    report["passed_count"] = sum(case["passed"] for case in report["cases"])
    report["total_count"] = len(report["cases"])
    args.output.write_text(json.dumps(report, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
    print(f"{report['passed_count']}/{report['total_count']} passed; report: {args.output}")
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
