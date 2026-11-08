"""Run one synthetic case through the deployed, authorized Vultr agent."""
import argparse
import getpass
import json
import os
import sys
from pathlib import Path
from urllib.parse import urlsplit

import httpx

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from prooflane.case_evidence import check_case_packet


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", required=True, help="HTTPS origin of your Prooflane deployment")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "artifacts" / "vultr-release")
    args = parser.parse_args()
    origin = args.base_url.rstrip("/")
    url = urlsplit(origin)
    if url.scheme != "https" or not url.hostname or url.path or url.query or url.fragment or url.username:
        parser.error("Use the HTTPS origin of your own Prooflane deployment, without a path or credentials.")

    with httpx.Client(base_url=origin, timeout=190, trust_env=False, follow_redirects=False) as client:
        response = client.get("/api/health")
        response.raise_for_status()
        health = response.json()
        if not (health["inference"]["configured"] and health["inference"]["enabled"] and health["docker"]["available"]):
            raise SystemExit("Vultr agent is not ready. Configure the server and check Docker health first.")
        token = os.environ.get("PROOFLANE_OPERATOR_TOKEN") or getpass.getpass("Prooflane operator token: ")
        if not token:
            raise SystemExit("No operator token supplied.")
        sample = client.get("/api/cases/sample")
        sample.raise_for_status()
        source = sample.json()
        headers = {"X-Prooflane-Request": "1", "Origin": origin}
        response = client.post("/api/cases", headers=headers, json={
            "name": "Vultr agent verification · synthetic",
            "mode": "vultr", "operator_token": token,
            "invoices_csv": source["invoices_csv"], "contracts_csv": source["contracts_csv"],
            "selections": {"5": "C2R"}, "exclusions": {"7": "No active contract in the supplied fixture."},
        })
        if response.status_code != 200:
            raise SystemExit(f"Case creation returned HTTP {response.status_code}: {response.json().get('detail', 'No detail')}")
        case = response.json()["case"]
        export = client.get(f"/api/cases/{case['id']}/packet")
        export.raise_for_status()
        packet = export.json()

    verified = check_case_packet(packet)
    baseline = packet["baseline"]
    provenance = baseline["provenance"]
    execution = baseline["execution"]
    trace = baseline.get("explanation_trace", {})
    generation_ids = [attempt.get("request_id") for attempt in baseline.get("attempts", [])]
    passed = (verified["passed"] is True and baseline["summary"]["total_variance"] == "768.00"
              and baseline["summary"]["row_count"] == 7 and provenance["mode"] == "vultr"
              and provenance["model_calls"] in (2, 3) and bool(generation_ids and generation_ids[-1])
              and execution["runtime"] == "docker" and execution["cleanup"] is True
              and trace.get("status") == "checked" and bool(trace.get("request_id")))
    report = {"passed": passed, "case_id": case["id"], "model": provenance.get("model"),
              "model_calls": provenance["model_calls"], "generation_request_ids": generation_ids,
              "explanation_request_id": trace.get("request_id"), "verification": verified}
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "live-case-packet.json").write_bytes(export.content)
    (args.output_dir / "live-evidence.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
