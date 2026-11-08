"""Synthetic read-only source audit; writes only this review directory.

No real provider or Docker call. These probes check orchestration/parser behavior,
not containment or model quality. Run with PYTHONDONTWRITEBYTECODE=1.
"""
import importlib.util
import json
import os
from pathlib import Path
import sys
import uuid
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
SESSION = OUT / ("probe-data-" + uuid.uuid4().hex)
SESSION.mkdir()
sys.path.insert(0, str(ROOT))
os.environ["PROOFLANE_DATA_DIR"] = str(SESSION / "unused-default")
os.environ["PROOFLANE_PUBLIC_ORIGIN"] = "http://testserver"
os.environ["PROOFLANE_LIVE_ENABLED"] = "true"
os.environ["PROOFLANE_OPERATOR_TOKEN"] = "review-only-not-a-secret"
os.environ["VULTR_INFERENCE_API_KEY"] = ""
os.environ["VULTR_MODEL"] = ""

original_exists = Path.exists
with patch.object(Path, "exists", lambda path: False if path == ROOT / ".env" else original_exists(path)):
    import prooflane.app as app_module
app_module.load_local_config = lambda: None

import httpx
from fastapi.testclient import TestClient
from prooflane.analysis import contract_output, parse_csv, summarize
from prooflane.provider import ProviderError, VultrProvider
from prooflane.sandbox import SandboxError

CSV = "invoice_id,vendor,quantity,unit_price,contract_price,notes\nTEST,Vendor,1,2,1,Synthetic\n"
EXPECTED = contract_output(summarize(parse_csv(CSV)))
PAYLOAD = {"csv": CSV, "mode": "vultr", "operator_token": "review-only-not-a-secret"}
HEADERS = {"X-Prooflane-Request": "1"}


class FakeProvider:
    model = "review-only"

    def __init__(self, plan=None):
        self.calls = 0
        self.plan = plan or ["calculate"]

    def configured(self):
        return True

    def generate(self, *args, **kwargs):
        self.calls += 1
        return {"plan": self.plan, "code": "# Test double; never executed", "model": self.model,
                "requested_model": self.model, "usage": {}}


class FakeSandbox:
    def __init__(self, behavior):
        self.behavior = behavior
        self.calls = 0

    def available(self):
        return {"available": True, "detail": "Audit double"}

    def stale_containers(self):
        return []

    def run(self, *args):
        self.calls += 1
        if self.behavior == "timeout_then_success" and self.calls == 1:
            raise SandboxError("Synthetic wall-clock timeout", {"cleanup": True, "exit_code": -1})
        stdout = "[" * 2000 + "0" + "]" * 2000 if self.behavior == "deep_json" else json.dumps(EXPECTED)
        return {"stdout": stdout, "stderr": "", "exit_code": 0, "cleanup": True, "elapsed_ms": 1}


results = []
for behavior in ("timeout_then_success", "deep_json", "normal"):
    provider, sandbox = FakeProvider(), FakeSandbox(behavior)
    app = app_module.create_app(SESSION / behavior, provider=provider, sandbox=sandbox)
    with TestClient(app, raise_server_exceptions=False) as client:
        response = client.post("/api/runs", json=PAYLOAD, headers=HEADERS)
        try:
            body = response.json()
        except ValueError:
            body = response.text
        stored_count = len(client.get("/api/runs").json()["runs"])
    results.append({"case": behavior, "http_status": response.status_code, "body": body,
                    "provider_calls": provider.calls, "sandbox_calls": sandbox.calls,
                    "stored_runs": stored_count})

original_client = httpx.Client
for choice in (None, "invalid-choice"):
    envelope = {"model": "review-only", "choices": [choice]}
    def respond(request):
        return httpx.Response(200, json=envelope)
    provider = VultrProvider.__new__(VultrProvider)
    provider.key = "review-only-not-real"
    provider.model = "review-only"
    with patch.object(httpx, "Client", lambda **kw: original_client(transport=httpx.MockTransport(respond), **kw)):
        try:
            provider.generate("synthetic request", 1)
            outcome = "unexpected success"
        except Exception as exc:
            outcome = {"exception": type(exc).__name__, "message": str(exc),
                       "handled_as_provider_error": isinstance(exc, ProviderError)}
    results.append({"case": "invalid_provider_choice", "choice": choice, "result": outcome})

provider = VultrProvider.__new__(VultrProvider)
provider.key = "review-only-not-real"
provider.model = "review-only"
app = app_module.create_app(SESSION / "provider-malformed-api", provider=provider, sandbox=FakeSandbox("normal"))
def malformed_response(request):
    return httpx.Response(200, json={"choices": [None]})
with patch.object(httpx, "Client", lambda **kw: original_client(transport=httpx.MockTransport(malformed_response), **kw)):
    with TestClient(app, raise_server_exceptions=False) as client:
        response = client.post("/api/runs", json=PAYLOAD, headers=HEADERS)
        stored_count = len(client.get("/api/runs").json()["runs"])
results.append({"case": "invalid_provider_choice_api", "http_status": response.status_code,
                "body": response.text, "stored_runs": stored_count})

output = {"scope": "Local TestClient and mocked HTTP/Docker; no live calls", "results": results}
(OUT / "engineering-probes.json").write_text(json.dumps(output, indent=2), encoding="utf-8")
print(json.dumps([{k:v for k,v in record.items() if k != 'body'} | {
    'status': record.get('body', {}).get('status') if isinstance(record.get('body'), dict) else record.get('body')
} for record in results], indent=2))
