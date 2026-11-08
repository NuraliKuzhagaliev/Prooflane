from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from prooflane.app import create_app
from prooflane.analysis import contract_output, parse_csv, summarize
from prooflane.receipts import check_receipt

SAMPLE = Path("examples/invoices.csv").read_text()
HEADERS = {"X-Prooflane-Request": "1"}


class UnavailableSandbox:
    def available(self):
        return {"available": False, "detail": "Test double: no daemon"}
    def run(self, *args):
        raise AssertionError("Must not execute")


@pytest.fixture
def client(tmp_path):
    return TestClient(create_app(tmp_path, sandbox=UnavailableSandbox()))


def test_reference_receipt_and_session_isolation(client):
    response = client.post("/api/runs", json={"csv": SAMPLE, "mode": "reference"}, headers=HEADERS)
    assert response.status_code == 200, response.text
    run = response.json()
    assert run["status"] == "verified"
    assert run["execution"]["runtime"] == "trusted-reference"
    assert run["summary"]["total_variance"] == "1480.00"
    receipt = client.get(f"/api/runs/{run['id']}/receipt").json()
    assert check_receipt(receipt)["passed"]
    assert receipt["provenance"]["model_calls"] == 0
    assert len(client.get("/api/runs").json()["runs"]) == 1
    with TestClient(client.app) as stranger:
        assert stranger.get(f"/api/runs/{run['id']}").status_code == 404
        assert stranger.get(f"/api/runs/{run['id']}/receipt").status_code == 404
        assert stranger.get("/api/runs").json() == {"runs": []}


def test_sandbox_fails_closed(client):
    run = client.post("/api/runs", json={"csv": SAMPLE, "mode": "sandbox"}, headers=HEADERS).json()
    assert run["status"] == "failed"
    assert run["summary"] is None
    assert "no code was executed" in run["error"].lower()
    assert client.get(f"/api/runs/{run['id']}/receipt").status_code == 404


def test_live_requires_explicit_configuration(client):
    response = client.post("/api/runs", json={"csv": SAMPLE, "mode": "vultr"}, headers=HEADERS)
    assert response.status_code == 503


def test_csrf_origin_validation_and_limits(client):
    assert client.post("/api/runs", json={"csv": SAMPLE}).status_code == 403
    assert client.post("/api/runs", json={"csv": SAMPLE}, headers={**HEADERS,"Origin":"https://evil.example"}).status_code == 403
    assert client.post("/api/runs", json={"csv":"bad"}, headers=HEADERS).status_code == 422
    assert client.post("/api/runs", json={"csv":"x"*180001}, headers=HEADERS).status_code == 413
    assert client.get("/api/health", headers={"Host":"evil.example"}).status_code == 400


def test_mismatching_sandbox_output_withheld(tmp_path):
    class WrongSandbox(UnavailableSandbox):
        def available(self):
            return {"available": True, "detail": "Test double"}
        def run(self, *args):
            return {"stdout": '{"row_count":24,"total_billed":"0.00","total_variance":"0.00","findings":[]}',
                    "stderr": "", "exit_code": 0, "cleanup": True, "elapsed_ms": 1}
    with TestClient(create_app(tmp_path, sandbox=WrongSandbox())) as client:
        run = client.post("/api/runs", json={"csv":SAMPLE,"mode":"sandbox"}, headers=HEADERS).json()
        assert run["status"] == "failed"
        assert run["summary"] is None
        assert not run["verification"]["passed"]


def test_uncertain_cleanup_quarantines_until_operator_resolution(tmp_path):
    from prooflane.sandbox import SandboxError
    class LeakingSandbox(UnavailableSandbox):
        calls = 0
        def available(self):
            return {"available":True,"detail":"Test double"}
        def run(self, *args):
            self.calls += 1
            raise SandboxError("Cleanup not verified", {"cleanup":False,"container_id":"test-container"})
    sandbox = LeakingSandbox()
    with TestClient(create_app(tmp_path, sandbox=sandbox)) as client:
        for _ in range(2):
            run = client.post("/api/runs", json={"csv":SAMPLE,"mode":"sandbox"}, headers=HEADERS).json()
            assert run["status"] == "failed"
        assert sandbox.calls == 1
        assert not client.get("/api/health").json()["docker"]["available"]
        assert client.post("/api/containment", json={}, headers=HEADERS).status_code == 503
    with TestClient(create_app(tmp_path, sandbox=sandbox)) as restarted:
        assert not restarted.get("/api/health").json()["docker"]["available"]


def test_invalid_unicode_is_client_error(client):
    assert client.post("/api/runs", content='{"csv":"\\ud800"}', headers={**HEADERS,"Content-Type":"application/json"}).status_code == 422


def test_non_ascii_operator_token_rejected_cleanly(tmp_path, monkeypatch):
    class ConfiguredProvider:
        model = "test-model"
        def configured(self): return True
    monkeypatch.setenv("PROOFLANE_LIVE_ENABLED", "true")
    monkeypatch.setenv("PROOFLANE_OPERATOR_TOKEN", "test-only-token")
    with TestClient(create_app(tmp_path, sandbox=UnavailableSandbox(), provider=ConfiguredProvider())) as client:
        response = client.post("/api/runs", json={"csv":SAMPLE,"mode":"vultr","operator_token":"неверный"}, headers=HEADERS)
        assert response.status_code == 403


def test_orphaned_container_blocks_new_runs_after_restart(tmp_path):
    class OrphanSandbox(UnavailableSandbox):
        def stale_containers(self): return ["orphan-from-prior-process"]
        def available(self): return {"available":True,"detail":"Test double"}
    with TestClient(create_app(tmp_path, sandbox=OrphanSandbox())) as client:
        response = client.post("/api/runs", json={"csv":SAMPLE,"mode":"sandbox"}, headers=HEADERS)
        assert response.json()["status"] == "failed"
        assert (tmp_path / "sandbox-quarantine.json").exists()


def test_live_repair_contract_records_both_attempts(tmp_path, monkeypatch):
    """Provider and runtime doubles; verifies orchestration, not real model quality."""
    import json
    class Provider:
        model = "fixture-model"
        calls = 0
        def configured(self): return True
        def generate(self, question, row_count, feedback=None):
            self.calls += 1
            assert bool(feedback) == (self.calls == 2)
            return {"code":f"attempt {self.calls}","plan":["compute"],"model":self.model,"requested_model":self.model,"usage":{}}
        def explain(self, row_count, flagged_count):
            assert self.calls == 2 and (row_count, flagged_count) == (24, 6)
            return {"lead": "variance", "review": "contracts", "model": self.model, "request_id": "fixture-explanation"}
    class Sandbox:
        calls = 0
        def available(self): return {"available":True,"detail":"Test double"}
        def run(self, code, csv):
            self.calls += 1
            output = contract_output(summarize(parse_csv(csv)))
            if self.calls == 1: output["total_variance"] = "0.00"
            return {"stdout":json.dumps(output),"stderr":"","exit_code":0,"cleanup":True,"elapsed_ms":1}
    monkeypatch.setenv("PROOFLANE_LIVE_ENABLED", "true")
    monkeypatch.setenv("PROOFLANE_OPERATOR_TOKEN", "fixture-token")
    provider, sandbox = Provider(), Sandbox()
    with TestClient(create_app(tmp_path, sandbox=sandbox, provider=provider)) as client:
        run = client.post("/api/runs", json={"csv":SAMPLE,"mode":"vultr","operator_token":"fixture-token"}, headers=HEADERS).json()
        assert run["status"] == "verified"
        assert provider.calls == sandbox.calls == 2
        assert len(run["attempts"]) == 2
        assert not run["attempts"][0]["verification"]["passed"]
        receipt = client.get(f"/api/runs/{run['id']}/receipt").json()
        assert receipt["provenance"]["model_calls"] == 3
        assert receipt["explanation_trace"]["request_id"] == "fixture-explanation"
        assert receipt["explanation"].startswith("Positive price differences total USD 1480.00.")
        assert len(receipt["attempts"]) == 2


@pytest.mark.parametrize("cleanup", [True, False])
def test_live_runtime_failure_repairs_only_after_confirmed_cleanup(tmp_path, monkeypatch, cleanup):
    """Runtime/provider doubles test retry policy, not model quality."""
    import json
    from prooflane.sandbox import SandboxError
    class Provider:
        model = "fixture-model"
        calls = 0
        def configured(self): return True
        def generate(self, question, row_count, feedback=None):
            self.calls += 1
            assert bool(feedback) == (self.calls == 2)
            return {"code":"fixed fixture", "plan":["compute"], "model":self.model, "requested_model":self.model}
        def explain(self, row_count, flagged_count):
            from prooflane.provider import ProviderError
            assert cleanup and self.calls == 2
            raise ProviderError("Fixture unavailable")
    class Sandbox:
        calls = 0
        def available(self): return {"available":True,"detail":"Test double"}
        def run(self, code, csv):
            self.calls += 1
            if self.calls == 1:
                raise SandboxError("Wall-clock time exceeded", {"cleanup":cleanup,"container_id":"fixture-only"})
            return {"stdout":json.dumps(contract_output(summarize(parse_csv(csv)))), "stderr":"", "exit_code":0,"cleanup":True,"elapsed_ms":1}
    monkeypatch.setenv("PROOFLANE_LIVE_ENABLED", "true")
    monkeypatch.setenv("PROOFLANE_OPERATOR_TOKEN", "fixture-token")
    provider, sandbox = Provider(), Sandbox()
    with TestClient(create_app(tmp_path, sandbox=sandbox, provider=provider)) as client:
        run = client.post("/api/runs", json={"csv":SAMPLE,"mode":"vultr","operator_token":"fixture-token"}, headers=HEADERS).json()
        assert run["status"] == ("verified" if cleanup else "failed")
        assert provider.calls == sandbox.calls == (2 if cleanup else 1)
        assert len(run["attempts"]) == (2 if cleanup else 1)
        assert run.get("explanation_trace") == ({"status": "unavailable"} if cleanup else None)
        assert (tmp_path / "sandbox-quarantine.json").exists() is (not cleanup)
