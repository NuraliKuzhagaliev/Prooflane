"""Actual routes/SQLite with labeled sandbox doubles; no real provider requests."""
import json
import sqlite3
import subprocess
import sys
import threading
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from prooflane.analysis import contract_output, parse_csv, summarize
from prooflane.app import create_app
from prooflane.operations import CaseLocks
from prooflane.strict_json import load_evidence_json

HEADERS = {"X-Prooflane-Request": "1"}
ROOT = Path(__file__).resolve().parents[1]


def body(**overrides):
    return {"name": "Recovery test · synthetic", "mode": "reference",
            "invoices_csv": (ROOT / "examples/case-invoices.csv").read_text(encoding="utf-8"),
            "contracts_csv": (ROOT / "examples/case-contracts.csv").read_text(encoding="utf-8"),
            "selections": {"5": "C2R"}, "exclusions": {"7": "No eligible supplied contract"}, **overrides}


def new_case(client, **overrides):
    response = client.post("/api/cases", headers=HEADERS, json=body(**overrides))
    assert response.status_code == 200, response.text
    return response.json()["case"]


def test_replay_binds_explicit_fields_that_affect_promotion_contract(tmp_path):
    with TestClient(create_app(tmp_path, sandbox=CountingSandbox())) as client:
        source = new_case(client)
        payload = {'name': 'Promoted', 'baseline_run_id': source['baseline']['id'], 'request_id': str(uuid.uuid4())}
        first = client.post('/api/cases', headers=HEADERS, json=payload)
        assert first.status_code == 200
        assert client.post('/api/cases', headers=HEADERS, json=payload).json()['case']['id'] == first.json()['case']['id']
        explicit = {**payload, 'mode': 'reference'}
        assert client.post('/api/cases', headers=HEADERS, json=explicit).status_code == 409
        assert client.post('/api/cases', headers=HEADERS, json={**explicit, 'request_id': str(uuid.uuid4())}).status_code == 422


class CountingSandbox:
    """Contract double only; cannot establish actual Docker isolation."""
    def __init__(self):
        self.calls = 0
        self.entered = threading.Event()
        self.release = threading.Event()
        self.block_on = None

    def available(self):
        return {"available": True, "detail": "Controlled test double"}

    def run(self, code, csv_text):
        self.calls += 1
        if self.calls == self.block_on:
            self.entered.set()
            assert self.release.wait(5), "Test failed to release blocked execution"
        return {"stdout": json.dumps(contract_output(summarize(parse_csv(csv_text)))), "stderr": "",
                "exit_code": 0, "cleanup": True, "elapsed_ms": 1}


def test_lost_create_response_is_recoverable_without_a_second_execution(tmp_path):
    sandbox = CountingSandbox()
    request_id = str(uuid.uuid4())
    with TestClient(create_app(tmp_path, sandbox=sandbox)) as client:
        payload = body(mode="sandbox", request_id=request_id, operator_token="not-persisted-secret")
        first = client.post("/api/cases", headers=HEADERS, json=payload)
        assert first.status_code == 200
        case = first.json()["case"]
        # Pretend the first response was lost: only the previously saved ID is needed.
        status = client.get("/api/operations/" + request_id).json()["operation"]
        assert status == {"id": request_id, "status": "completed", "case_id": case["id"], "http_status": 200}
        reopened = client.get("/api/cases/" + status["case_id"]).json()["case"]
        retry = client.post("/api/cases", headers=HEADERS, json={**payload, "operator_token": "different-token-not-hashed"})
        assert retry.status_code == 200 and retry.json()["case"] == reopened
        assert sandbox.calls == 1
        assert len(client.get("/api/runs").json()["runs"]) == 1
        assert client.post("/api/cases", headers=HEADERS, json={**payload, "name": "different"}).status_code == 409
        with TestClient(client.app) as stranger:
            assert stranger.get("/api/operations/" + request_id).status_code == 404
        with sqlite3.connect(tmp_path / "prooflane.sqlite3") as db:
            record = repr(db.execute("SELECT * FROM operations").fetchall())
        assert "not-persisted-secret" not in record and "different-token" not in record
        assert "invoice_id,vendor" not in record and "No eligible" not in record


def test_concurrent_duplicate_observes_pending_and_does_not_execute(tmp_path):
    sandbox = CountingSandbox()
    sandbox.block_on = 1
    payload = body(mode="sandbox", request_id=str(uuid.uuid4()))
    with TestClient(create_app(tmp_path, sandbox=sandbox)) as client:
        client.get("/api/cases")  # Establish the same owner before concurrent POSTs.
        with ThreadPoolExecutor(max_workers=1) as pool:
            pending = pool.submit(client.post, "/api/cases", headers=HEADERS, json=payload)
            try:
                assert sandbox.entered.wait(5)
                repeated = client.post("/api/cases", headers=HEADERS, json=payload)
                assert repeated.status_code == 202 and "case" not in repeated.json()
                assert repeated.headers["Retry-After"] == "2"
                assert repeated.json()["operation"]["status"] == "pending"
                assert client.get("/api/operations/" + payload["request_id"]).json()["operation"]["status"] == "pending"
                assert sandbox.calls == 1
            finally:
                sandbox.release.set()
            assert pending.result(timeout=5).status_code == 200
        assert client.post("/api/cases", headers=HEADERS, json=payload).status_code == 200
        assert sandbox.calls == 1


def test_variant_key_replays_after_revision_changed_and_rejects_other_scope(tmp_path):
    with TestClient(create_app(tmp_path)) as client:
        case = new_case(client)
        request_id = str(uuid.uuid4())
        payload = {"request_id": request_id, "revision": 1, "name": "Price 80",
                   "changes": [{"target": "contract:C1", "value": "80.00"}]}
        endpoint = f"/api/cases/{case['id']}/variants"
        first = client.post(endpoint, headers=HEADERS, json=payload)
        assert first.status_code == 200
        assert first.json()["case"]["revision"] == 2
        repeated = client.post(endpoint, headers=HEADERS, json=payload)
        assert repeated.status_code == 200
        assert repeated.json()["case"] == first.json()["case"]
        assert len(client.get("/api/runs").json()["runs"]) == 2
        assert client.post(endpoint, headers=HEADERS, json={**payload, "name": "Changed"}).status_code == 409
        assert client.post("/api/cases", headers=HEADERS, json=body(request_id=request_id)).status_code == 409


def test_failed_execution_is_replayed_without_fabricating_a_case(tmp_path):
    class Unavailable:
        def available(self):
            return {"available": False, "detail": "Unavailable test double"}

    request_id = str(uuid.uuid4())
    payload = body(mode="sandbox", request_id=request_id)
    with TestClient(create_app(tmp_path, sandbox=Unavailable())) as client:
        first = client.post("/api/cases", headers=HEADERS, json=payload)
        repeated = client.post("/api/cases", headers=HEADERS, json=payload)
        assert first.status_code == repeated.status_code == 422
        assert "case" not in repeated.json()
        assert repeated.json()["failed_run"]["id"] == first.json()["failed_run"]["id"]
        assert repeated.json()["operation"]["status"] == "failed"
        assert len(client.get("/api/runs").json()["runs"]) == 1


def test_restart_reconciles_committed_create_and_marks_unknown_work_interrupted(tmp_path):
    request_id, interrupted = str(uuid.uuid4()), str(uuid.uuid4())
    with TestClient(create_app(tmp_path)) as client:
        case = new_case(client, request_id=request_id)
        cookies = dict(client.cookies)
    with sqlite3.connect(tmp_path / "prooflane.sqlite3") as db:
        db.execute("UPDATE operations SET status='pending' WHERE id=?", (request_id,))
        owner = db.execute("SELECT owner FROM operations WHERE id=?", (request_id,)).fetchone()[0]
        db.execute("INSERT INTO operations VALUES (?,?,?,?,?,'pending',?,NULL,202,NULL)",
                   (owner, interrupted, time.time(), "create", "test-digest", str(uuid.uuid4())))
    with TestClient(create_app(tmp_path)) as client:
        client.cookies.update(cookies)
        complete = client.get("/api/operations/" + request_id).json()["operation"]
        assert complete["status"] == "completed" and complete["case_id"] == case["id"]
        stopped = client.get("/api/operations/" + interrupted).json()["operation"]
        assert stopped["status"] == "interrupted" and "will not execute again" in stopped["error"]
        assert len(client.get("/api/runs").json()["runs"]) == 1
        with sqlite3.connect(tmp_path / "prooflane.sqlite3") as db:
            db.execute("UPDATE operations SET created=?", (time.time() - 86401,))
        assert client.get("/api/operations/" + request_id).status_code == 404


def test_one_slow_case_does_not_block_mutating_an_unrelated_case(tmp_path):
    sandbox = CountingSandbox()
    with TestClient(create_app(tmp_path, sandbox=sandbox)) as client:
        slow = new_case(client, mode="sandbox")
        other = new_case(client)
        sandbox.block_on = 2
        proposal = {"revision": 1, "name": "Slow variant", "changes": [{"target": "contract:C1", "value": "80.00"}]}
        with ThreadPoolExecutor(max_workers=1) as pool:
            pending = pool.submit(client.post, f"/api/cases/{slow['id']}/variants", headers=HEADERS, json=proposal)
            try:
                assert sandbox.entered.wait(5)
                unrelated = client.post(f"/api/cases/{other['id']}/bounds", headers=HEADERS,
                                        json={"revision": 1, "bounds": [{"target": "contract:C1", "low": "65", "high": "85"}]})
                assert unrelated.status_code == 200 and unrelated.json()["case"]["revision"] == 2
                same = client.post(f"/api/cases/{slow['id']}/bounds", headers=HEADERS, json={"revision": 1, "bounds": []})
                assert same.status_code == 409
            finally:
                sandbox.release.set()
            assert pending.result(timeout=5).status_code == 200


def test_lock_registry_is_bounded_and_releases_idle_entries():
    locks = CaseLocks(maximum=1)
    assert locks.acquire("owner", "a")
    assert not locks.acquire("owner", "a") and not locks.acquire("owner", "b")
    locks.release("owner", "a")
    assert locks.acquire("owner", "b")
    locks.release("owner", "b")
    assert not locks.active


def test_ambiguous_packet_keys_are_rejected_by_api_and_cli(tmp_path):
    with TestClient(create_app(tmp_path)) as client:
        case = new_case(client)
        packet = client.get(f"/api/cases/{case['id']}/packet").text
        ambiguous = packet.replace('"case_sha256":', '"case_sha256":"conflicting-first","case_sha256":', 1)
        assert ambiguous != packet
        bad = client.post("/api/verify-packet", content=ambiguous,
                          headers={**HEADERS, "Content-Type": "application/json"})
        assert bad.status_code == 200 and bad.json()["passed"] is False
        assert "No code was executed" in bad.json()["error"]
        assert client.post("/api/verify-packet", content=packet,
                           headers={**HEADERS, "Content-Type": "application/json"}).json()["passed"]
        path = tmp_path / "duplicate-keys.json"
        path.write_text(ambiguous, encoding="utf-8")
        result = subprocess.run([sys.executable, str(ROOT / "scripts/verify_receipt.py"), str(path)], capture_output=True, text=True, timeout=15)
        assert result.returncode != 0 and "Duplicate JSON object keys" in result.stderr
    for schema in ("prooflane.case.v1", "prooflane.receipt.v1", "prooflane.comparison.v1"):
        with pytest.raises(ValueError, match="Duplicate JSON object keys"):
            load_evidence_json(json.dumps({"schema": schema})[:-1] + ',"nested":{"claim":1,"claim":2}}')
    with pytest.raises(ValueError, match="Non-finite"):
        load_evidence_json('{"value":NaN}')


def test_invalid_utf8_with_recovery_key_still_returns_safe_422(tmp_path):
    with TestClient(create_app(tmp_path)) as client:
        for payload in (body(name="do-not-echo-\ud800", request_id=str(uuid.uuid4())),
                        body(invoices_csv="do-not-echo-\ud800", request_id=str(uuid.uuid4()))):
            response = client.post("/api/cases", content=json.dumps(payload),
                                   headers={**HEADERS, "Content-Type": "application/json"})
            assert response.status_code == 422 and "do-not-echo" not in response.text
        assert not client.get("/api/runs").json()["runs"]
