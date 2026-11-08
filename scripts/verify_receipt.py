"""Offline verification: python scripts/verify_receipt.py receipt.json"""
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from prooflane.receipts import check_receipt
from prooflane.comparison import check_bundle
from prooflane.case_evidence import MAX_PACKET_BYTES, check_case_packet
from prooflane.strict_json import load_evidence_json

if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python scripts/verify_receipt.py RECEIPT.json")
    try:
        path = Path(sys.argv[1])
        if path.stat().st_size > MAX_PACKET_BYTES:
            raise ValueError("Artifact exceeds the 8 MiB verification limit")
        artifact = load_evidence_json(path.read_text(encoding="utf-8"))
        schema = artifact.get("schema") if isinstance(artifact, dict) else None
        checker = check_case_packet if schema == "prooflane.case.v1" else check_bundle if schema == "prooflane.comparison.v1" else check_receipt
        print(json.dumps(checker(artifact), indent=2))
    except (ValueError, KeyError, TypeError, OSError, RecursionError, AttributeError) as exc:
        raise SystemExit("FAIL: " + str(exc))
