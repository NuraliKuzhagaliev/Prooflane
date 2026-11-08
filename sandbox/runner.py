"""Trusted container entry point. This file must run only inside the sandbox image."""
import json
import sys

MAX_PAYLOAD = 1024 * 1024  # JSON escaping can expand bounded code + CSV.
payload_bytes = sys.stdin.buffer.read(MAX_PAYLOAD + 1)
if len(payload_bytes) > MAX_PAYLOAD:
    raise ValueError("Input envelope is too large")
payload = json.loads(payload_bytes)
code = payload["code"]
csv_text = payload["csv"]
if not isinstance(code, str) or len(code.encode("utf-8")) > 32768:
    raise ValueError("Invalid code size")
if not isinstance(csv_text, str) or len(csv_text.encode("utf-8")) > 131072:
    raise ValueError("Invalid CSV size")
with open("/tmp/input.csv", "w", encoding="utf-8", newline="") as stream:
    stream.write(csv_text)
# Docker is the security boundary; this is deliberately NOT a Python-language sandbox.
namespace = {"__name__": "__main__", "__file__": "/tmp/analysis.py"}
exec(compile(code, "/tmp/analysis.py", "exec"), namespace, namespace)
