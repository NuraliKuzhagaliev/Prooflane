"""Workbench HTTP boundaries using real application routes and labeled runtime doubles."""
import copy
from concurrent.futures import ThreadPoolExecutor
import json
import sqlite3
import threading
import time
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from prooflane.analysis import canonical, contract_output, digest, parse_csv, summarize
from prooflane.app import create_app
from prooflane.case_evidence import check_case_packet

INVOICES = Path("examples/case-invoices.csv").read_text(encoding="utf-8")
CONTRACTS = Path("examples/case-contracts.csv").read_text(encoding="utf-8")
HEADERS = {"X-Prooflane-Request": "1"}


class UnavailableSandbox:
    def available(self):
        return {"available": False, "detail": "QA test double: no daemon"}

    def run(self, *args):
        raise AssertionError("Unavailable sandbox must not execute")


def request_body(**overrides):
    return {"name": "Synthetic supplier review", "mode": "reference", "invoices_csv": INVOICES,
            "contracts_csv": CONTRACTS, "selections": {"5": "C2R"},
            "exclusions": {"7": "No active supplied contract; excluded from this review"}, **overrides}


def create_case(client, **overrides):
    response = client.post("/api/cases", json=request_body(**overrides), headers=HEADERS)
    assert response.status_code == 200, response.text
    return response.json()["case"]


def propose(case, name="Revised shared contract", value="80.00", **overrides):
    return {"revision": case["revision"], "name": name,
            "changes": [{"target": "contract:C1", "value": value}], **overrides}


@pytest.fixture
def client(tmp_path):
    with TestClient(create_app(tmp_path, sandbox=UnavailableSandbox())) as value:
        yield value


def test_cases_reconcile_before_execution_and_preserve_manual_baseline(client):
    sample = client.get("/api/cases/sample").json()
    assert sample["invoices_csv"] == INVOICES
    assert sample["contracts_csv"] == CONTRACTS
    unresolved = request_body(selections={}, exclusions={})
    assert client.post("/api/cases", json=unresolved, headers=HEADERS).status_code == 422
    assert client.get("/api/runs").json()["runs"] == []
    case = create_case(client)
    assert case["revision"] == 1
    assert case["baseline"]["summary"]["total_variance"] == "768.00"
    assert case["baseline"]["summary"]["total_billed"] == "7110.00"
    assert case["baseline"]["execution"]["runtime"] == "trusted-reference"
    assert case["source"]["counts"]["excluded"] == 1
    target = next(t for t in case["targets"] if t["id"] == "contract:C1")
    assert target["rows"] == [2, 3, 8]
    assert case["intelligence"]["low"] == case["intelligence"]["high"] == "768.00"


def test_case_owner_isolation_covers_reads_changes_and_download(client):
    case = create_case(client)
    cid = case["id"]
    with TestClient(client.app) as stranger:
        assert stranger.get("/api/cases").json() == {"cases": []}
        for path in (f"/api/cases/{cid}", f"/api/cases/{cid}/packet"):
            assert stranger.get(path).status_code == 404
        assert stranger.post(f"/api/cases/{cid}/variants", json=propose(case), headers=HEADERS).status_code == 404
        assert stranger.post(f"/api/cases/{cid}/bounds", json={"revision":1,"bounds":[]}, headers=HEADERS).status_code == 404
        assert stranger.post("/api/cases", json={"name":"Foreign import","baseline_run_id":case["baseline"]["id"]}, headers=HEADERS).status_code == 404
    assert len(client.get("/api/cases").json()["cases"]) == 1


def test_joint_alternative_is_immutable_shared_and_not_sum_of_individual_effects(client):
    case = create_case(client)
    baseline_before = copy.deepcopy(case["baseline"])
    changes = [{"target":"contract:C1","value":"80.00"}, {"target":"row:2:quantity","value":"80"}]
    response = client.post(f"/api/cases/{case['id']}/variants", json=propose(case, changes=changes), headers=HEADERS)
    assert response.status_code == 200, response.text
    updated = response.json()["case"]
    variant = updated["variants"][0]
    # C1 first record: 80*(85-80)=400; second=20; others=148. Joint total568.
    # Summing isolated effects instead would incorrectly give888.
    assert variant["run"]["summary"]["total_variance"] == "568.00"
    assert variant["delta"] == {"total_variance":"-200.00", "total_billed":"3400.00", "flagged_count":0}
    assert variant["changed_rows"] == [2,3,8]
    assert updated["revision"] == 2
    assert updated["baseline"] == baseline_before
    assert client.get(f"/api/runs/{baseline_before['id']}").json() == baseline_before
    rid = variant["run"]["id"]
    assert client.post("/api/cases", json={"name":"Chained case","baseline_run_id":rid}, headers=HEADERS).status_code == 422
    # The legacy one-cell path must not turn this case alternative into a new original.
    old = {"baseline_receipt_sha256":variant["run"]["receipt_hash"], "row":2,"field":"quantity","value":"90"}
    assert client.post(f"/api/runs/{rid}/scenario", json=old, headers=HEADERS).status_code == 422


def test_bounds_revision_and_reset_do_not_execute_a_run(client):
    case = create_case(client)
    endpoint = f"/api/cases/{case['id']}/bounds"
    body = {"revision":1,"bounds":[{"target":"contract:C1","low":"65.00","high":"85.00"}]}
    result = client.post(endpoint, json=body, headers=HEADERS)
    assert result.status_code == 200, result.text
    updated = result.json()["case"]
    assert updated["revision"] == 2
    assert {k:updated["intelligence"][k] for k in ("low","high","width")} == {"low":"148.00","high":"1193.00","width":"1045.00"}
    assert updated["intelligence"]["review_queue"][0]["guaranteed_width_reduction"] == "1045.00"
    assert len(client.get("/api/runs").json()["runs"]) == 1
    assert client.post(endpoint, json=body, headers=HEADERS).status_code == 409
    assert client.post(f"/api/cases/{case['id']}/variants", json=propose(case), headers=HEADERS).status_code == 409
    assert len(client.get("/api/runs").json()["runs"]) == 1
    reset = client.post(endpoint, json={"revision":2,"bounds":[]}, headers=HEADERS).json()["case"]
    assert reset["intelligence"]["width"] == "0.00"
    assert reset["revision"] == 3


def test_case_packet_browser_verification_rejects_rehashed_tampering_without_import(client):
    case = create_case(client)
    case = client.post(f"/api/cases/{case['id']}/variants", json=propose(case), headers=HEADERS).json()["case"]
    response = client.get(f"/api/cases/{case['id']}/packet")
    assert response.status_code == 200
    assert "attachment" in response.headers["content-disposition"]
    packet = response.json()
    assert check_case_packet(packet)["passed"]
    with TestClient(client.app) as stranger:
        result = stranger.post("/api/verify-packet", json=packet, headers=HEADERS).json()
        assert result["passed"] is True
        assert stranger.get("/api/cases").json() == {"cases":[]}
        assert stranger.get("/api/runs").json() == {"runs":[]}
        packet["intelligence"]["high"] = "99999999.00"
        packet["case_sha256"] = digest(canonical({k:v for k,v in packet.items() if k != "case_sha256"}))
        invalid = stranger.post("/api/verify-packet", json=packet, headers=HEADERS).json()
        assert invalid["passed"] is False
        assert "No code was executed" in invalid["error"]


def test_failed_baseline_and_alternative_are_not_saved_as_verified_cases(tmp_path):
    class Sandbox:
        failed = False
        calls = 0
        def available(self):
            return {"available": not self.failed, "detail":"QA orchestration double"}
        def run(self, code, csv_text):
            self.calls += 1
            return {"stdout":json.dumps(contract_output(summarize(parse_csv(csv_text)))), "stderr":"",
                    "exit_code":0,"cleanup":True,"elapsed_ms":1}
    sandbox = Sandbox()
    with TestClient(create_app(tmp_path, sandbox=sandbox)) as client:
        case = create_case(client, mode="sandbox")
        assert sandbox.calls == 1
        sandbox.failed = True
        response = client.post(f"/api/cases/{case['id']}/variants", json=propose(case), headers=HEADERS)
        assert response.status_code == 200, response.text
        assert response.json()["case"] == case
        failed = response.json()["failed_run"]
        assert failed["status"] == "failed" and failed["summary"] is None
        assert client.get(f"/api/runs/{failed['id']}/receipt").status_code == 404
        assert sandbox.calls == 1
        response = client.post("/api/cases", json=request_body(mode="sandbox"), headers=HEADERS)
        assert response.status_code == 422
        assert response.json()["failed_run"]["status"] == "failed"
        assert len(client.get("/api/cases").json()["cases"]) == 1


def test_case_api_rejects_noop_invalid_fields_excess_variants_and_secret_echo(client):
    case = create_case(client)
    endpoint = f"/api/cases/{case['id']}/variants"
    for change in ([{"target":"contract:C1","value":"72.0"}],
                   [{"target":"contract:C1","value":"80"},{"target":"contract:C1","value":"81"}],
                   [{"target":"row:2:notes","value":"1"}], [{"target":[],"value":"80"}]):
        assert client.post(endpoint, json=propose(case, changes=change), headers=HEADERS).status_code == 422
    bad = propose(case, operator_token="private-value-\ud800")
    response = client.post(endpoint, content=json.dumps(bad), headers={**HEADERS,"Content-Type":"application/json"})
    assert response.status_code == 422
    assert "private-value" not in response.text
    assert len(client.get("/api/runs").json()["runs"]) == 1
    for n in range(4):
        result = client.post(endpoint, json=propose(case, name=f"Alternative {n}", value=str(80+n)), headers=HEADERS)
        assert result.status_code == 200, result.text
        case = result.json()["case"]
    assert client.post(endpoint, json=propose(case, name="Fifth", value="90"), headers=HEADERS).status_code == 422
    assert len(client.get("/api/runs").json()["runs"]) == 5


def test_original_legacy_review_import_inherits_mode_and_rejects_mixed_inputs(client):
    csv_text = "invoice_id,vendor,quantity,unit_price,contract_price,notes\nA,V,2,12,10,legacy\n"
    baseline = client.post("/api/runs", json={"csv":csv_text,"mode":"reference"}, headers=HEADERS).json()
    body = {"name":"Legacy case","baseline_run_id":baseline["id"]}
    result = client.post("/api/cases", json=body, headers=HEADERS)
    assert result.status_code == 200, result.text
    case = result.json()["case"]
    assert case["source"]["kind"] == "embedded"
    assert case["baseline"] == baseline
    assert case["intelligence"]["baseline_variance"] == "4.00"
    assert client.post("/api/cases", json={**body,"mode":"sandbox"}, headers=HEADERS).status_code == 422
    assert len(client.get("/api/runs").json()["runs"]) == 1


def test_expired_baseline_hides_case_and_blocks_changes(tmp_path):
    with TestClient(create_app(tmp_path, sandbox=UnavailableSandbox())) as client:
        case = create_case(client)
        with sqlite3.connect(tmp_path / "prooflane.sqlite3") as db:
            db.execute("UPDATE runs SET created=? WHERE id=?", (time.time()-86401, case["baseline"]["id"]))
        assert client.get("/api/cases").json() == {"cases":[]}
        assert client.get(f"/api/cases/{case['id']}").status_code == 404
        assert client.get(f"/api/cases/{case['id']}/packet").status_code == 404
        assert client.post(f"/api/cases/{case['id']}/bounds", json={"revision":1,"bounds":[]}, headers=HEADERS).status_code == 404
        assert client.post(f"/api/cases/{case['id']}/variants", json=propose(case), headers=HEADERS).status_code == 404


def test_csrf_body_limits_and_malformed_packets_fail_cleanly(client):
    assert client.post("/api/cases", json=request_body()).status_code == 403
    assert client.post("/api/cases", json=request_body(), headers={**HEADERS,"Origin":"https://foreign.example"}).status_code == 403
    assert client.post("/api/cases/match", content="x"*(2*1024*1024+1), headers={**HEADERS,"Content-Type":"application/json"}).status_code == 413
    assert client.post("/api/verify-packet", content="x"*(8*1024*1024+1), headers={**HEADERS,"Content-Type":"application/json"}).status_code == 413
    for content in ("[]", "null", '{"schema":"prooflane.case.v1","name":"\\ud800"}', '{"x":NaN}', "["*1100+"0"+"]"*1100):
        response = client.post("/api/verify-packet", content=content, headers={**HEADERS,"Content-Type":"application/json"})
        assert response.status_code == 200, response.text
        assert response.json()["passed"] is False


def test_two_valid_large_sources_can_cross_old_180kb_body_limit(client):
    invoice_header = "invoice_id,vendor,item_id,invoice_date,quantity,unit_price,notes\n"
    contract_header = "contract_id,vendor,item_id,valid_from,valid_to,contract_price\n"
    invoices = invoice_header + "".join(f"I{n},V{n},ITEM,2026-11-01,1,2,{'n'*200}\n" for n in range(500))
    contracts = contract_header + "".join(f"C{n}{'c'*140},V{n},ITEM,2026-11-01,2026-11-30,1\n" for n in range(500))
    body = {"invoices_csv":invoices,"contracts_csv":contracts}
    assert len(invoices.encode()) < 131072 and len(contracts.encode()) < 131072
    assert len(json.dumps(body).encode()) > 180000
    response = client.post("/api/cases/match", json=body, headers=HEADERS)
    assert response.status_code == 200, response.text
    assert response.json()["ready"] is True
    assert response.json()["counts"]["matched"] == 500


def test_concurrent_revision_update_is_rejected_before_second_mutation(tmp_path):
    entered, release = threading.Event(), threading.Event()
    class BlockingSandbox:
        calls = 0
        def available(self):
            return {"available":True,"detail":"QA synchronization double"}
        def run(self, code, csv_text):
            self.calls += 1
            if self.calls == 2:
                entered.set()
                assert release.wait(5), "QA release signal was not sent"
            return {"stdout":json.dumps(contract_output(summarize(parse_csv(csv_text)))), "stderr":"",
                    "exit_code":0,"cleanup":True,"elapsed_ms":1}
    sandbox = BlockingSandbox()
    with TestClient(create_app(tmp_path, sandbox=sandbox)) as client:
        case = create_case(client, mode="sandbox")
        with ThreadPoolExecutor(max_workers=1) as executor:
            pending = executor.submit(client.post, f"/api/cases/{case['id']}/variants", json=propose(case), headers=HEADERS)
            try:
                assert entered.wait(5), "Variant execution did not reach the controlled test double"
                conflict = client.post(f"/api/cases/{case['id']}/bounds", json={"revision":1,"bounds":[]}, headers=HEADERS)
                assert conflict.status_code == 409
            finally:
                release.set()
            completed = pending.result(timeout=5)
        assert completed.status_code == 200, completed.text
        updated = completed.json()["case"]
        assert updated["revision"] == 2 and len(updated["variants"]) == 1
        assert sandbox.calls == 2
        assert client.get(f"/api/cases/{case['id']}").json()["case"] == updated
