import copy
import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from prooflane.analysis import canonical, contract_output, digest, parse_csv, summarize
from prooflane.app import create_app
from prooflane.comparison import apply_assumption, check_bundle, make_bundle
from prooflane.receipts import make_receipt

SAMPLE = Path("examples/invoices.csv").read_text(encoding="utf-8")
HEADERS = {"X-Prooflane-Request": "1"}


def receipt_for(text, run_id, lineage=None):
    summary = summarize(parse_csv(text))
    return make_receipt({"run_id": run_id, "input_csv": text, "code": "fixed test reference",
        "summary": summary, "output": contract_output(summary), "provenance": {"mode": "reference", "model_calls": 0},
        **({"lineage": lineage} if lineage else {})})


def pair():
    baseline = receipt_for(SAMPLE, "baseline")
    text, change = apply_assumption(SAMPLE, 3, "contract_price", "80.00")
    lineage = {"schema": "prooflane.scenario.v1", "baseline_run_id": "baseline",
               "baseline_receipt_sha256": baseline["receipt_sha256"], "change": change}
    return baseline, receipt_for(text, "scenario", lineage)


def rehash_bundle(bundle):
    bundle["bundle_sha256"] = digest(canonical({k: v for k, v in bundle.items() if k != "bundle_sha256"}))
    return bundle


def test_independently_verifiable_single_assumption_and_exact_deltas():
    baseline, scenario = pair()
    before = canonical(baseline)
    bundle = make_bundle(baseline, scenario)
    result = check_bundle(bundle)
    assert result["passed"]
    assert result["comparison"]["baseline"]["total_variance"] == "1480.00"
    assert result["comparison"]["scenario"]["total_variance"] == "1160.00"
    assert result["comparison"]["delta"] == {"total_variance": "-320.00", "total_billed": "0.00", "flagged_count": 0}
    assert result["comparison"]["change"]["before_variance"] == "520.00"
    assert result["comparison"]["change"]["after_variance"] == "200.00"
    assert result["comparison"]["unchanged_records"] == 23
    assert canonical(baseline) == before


def test_rehashed_hidden_source_edit_rejected_even_when_arithmetic_is_valid():
    baseline, scenario = pair()
    altered = scenario["input_csv"].replace("Safety gloves", "Undeclared replacement")
    forged = receipt_for(altered, "scenario", scenario["lineage"])
    with pytest.raises(ValueError, match="undeclared"):
        make_bundle(baseline, forged)


def test_rehashed_delta_forgery_rejected():
    bundle = make_bundle(*pair())
    bundle["comparison"]["delta"]["total_variance"] = "-999.00"
    with pytest.raises(ValueError, match="deltas"):
        check_bundle(rehash_bundle(bundle))


@pytest.mark.parametrize("damage", ["parent_hash", "before", "same_id", "mode"])
def test_false_lineage_is_rejected(damage):
    baseline, scenario = pair()
    if damage == "parent_hash":
        scenario["lineage"]["baseline_receipt_sha256"] = "0" * 64
    elif damage == "before":
        scenario["lineage"]["change"]["before"] = "70.00"
    elif damage == "same_id":
        scenario["run_id"] = baseline["run_id"]
    else:
        scenario["provenance"]["mode"] = "vultr"
    scenario.pop("receipt_sha256")
    scenario = make_receipt(scenario)
    with pytest.raises(ValueError):
        make_bundle(baseline, scenario)


@pytest.mark.parametrize("row,field,value", [(True,"unit_price","2"), (999,"quantity","2"),
    (3,"notes","changed"), (3,"contract_price","72.0"), (3,"quantity","1.5"),
    (3,"unit_price","-1"), (3,"contract_price","80.001")])
def test_invalid_or_semantically_unchanged_assumption(row, field, value):
    with pytest.raises(ValueError):
        apply_assumption(SAMPLE, row, field, value)


def test_zero_variance_can_become_a_new_finding():
    text = "invoice_id,vendor,quantity,unit_price,contract_price,notes\nA,North,2,10,12,example\n"
    baseline = receipt_for(text, "base")
    changed, change = apply_assumption(text, 2, "contract_price", "9")
    scenario = receipt_for(changed, "next", {"schema":"prooflane.scenario.v1", "baseline_run_id":"base",
        "baseline_receipt_sha256":baseline["receipt_sha256"], "change":change})
    result = make_bundle(baseline, scenario)["comparison"]
    assert result["delta"] == {"total_variance":"2.00", "total_billed":"0.00", "flagged_count":1}


class UnavailableSandbox:
    def available(self):
        return {"available": False, "detail": "Test double: unavailable"}


def create_baseline(client, mode="reference"):
    response = client.post("/api/runs", json={"csv":SAMPLE,"mode":mode}, headers=HEADERS)
    assert response.status_code == 200
    return response.json()


def proposed(run, **overrides):
    return {"baseline_receipt_sha256":run["receipt_hash"], "row":3, "field":"contract_price", "value":"80.00", **overrides}


def test_api_versions_export_and_cross_session_privacy(tmp_path):
    app = create_app(tmp_path, sandbox=UnavailableSandbox())
    with TestClient(app) as client, TestClient(app) as stranger:
        baseline = create_baseline(client)
        source = client.get(f"/api/runs/{baseline['id']}/source").json()
        assert source["rows"][1]["contract_price"] == "72.00"
        assert len(source["rows"]) == 24
        scenario = client.post(f"/api/runs/{baseline['id']}/scenario", json=proposed(baseline), headers=HEADERS).json()
        assert scenario["status"] == "verified"
        assert scenario["comparison"]["delta"]["total_variance"] == "-320.00"
        assert client.get(f"/api/runs/{baseline['id']}").json() == baseline
        response = client.get(f"/api/runs/{scenario['id']}/comparison")
        assert response.status_code == 200
        assert "attachment" in response.headers["content-disposition"]
        bundle = response.json()
        assert check_bundle(bundle)["passed"]
        for path in (f"/api/runs/{baseline['id']}/source", f"/api/runs/{scenario['id']}/comparison"):
            assert stranger.get(path).status_code == 404
        assert stranger.post(f"/api/runs/{baseline['id']}/scenario", json=proposed(baseline), headers=HEADERS).status_code == 404
        assert client.post(f"/api/runs/{scenario['id']}/scenario", json=proposed(scenario), headers=HEADERS).status_code == 422
    # Both receipts are embedded; no database/network is required to check an exported packet.
    assert check_bundle(bundle)["passed"]


def test_api_rejects_stale_hash_invalid_fields_and_unicode(tmp_path):
    with TestClient(create_app(tmp_path, sandbox=UnavailableSandbox())) as client:
        baseline = create_baseline(client)
        endpoint = f"/api/runs/{baseline['id']}/scenario"
        assert client.post(endpoint, json=proposed(baseline), headers={}).status_code == 403
        assert client.post(endpoint, json=proposed(baseline, baseline_receipt_sha256="0"*64), headers=HEADERS).status_code == 409
        for fields in ({"field":"notes"}, {"row":True}, {"value":"72.0"}, {"value":"\ud800"}, {"operator_token":"\ud800"}):
            response = client.post(endpoint, content=json.dumps(proposed(baseline, **fields)), headers={**HEADERS,"Content-Type":"application/json"})
            assert response.status_code == 422
            assert "operator_token" not in response.text
        assert len(client.get("/api/runs").json()["runs"]) == 1


def test_failed_scenario_does_not_change_original_or_export_packet(tmp_path):
    class Sandbox:
        failed = False
        def available(self): return {"available":not self.failed,"detail":"Test double"}
        def run(self, code, csv):
            return {"stdout":json.dumps(contract_output(summarize(parse_csv(csv)))), "stderr":"", "exit_code":0,"cleanup":True,"elapsed_ms":1}
    sandbox = Sandbox()
    with TestClient(create_app(tmp_path, sandbox=sandbox)) as client:
        baseline = create_baseline(client, "sandbox")
        sandbox.failed = True
        result = client.post(f"/api/runs/{baseline['id']}/scenario", json=proposed(baseline), headers=HEADERS).json()
        assert result["status"] == "failed" and result["summary"] is None
        assert client.get(f"/api/runs/{result['id']}/comparison").status_code == 404
        assert client.get(f"/api/runs/{baseline['id']}").json() == baseline
