import copy

import pytest
from fastapi.testclient import TestClient

from prooflane.app import create_app
from prooflane.receipts import make_receipt
from scripts.evaluate_csv import CORPUS, check_run, evaluate_case, load_cases


class UnavailableSandbox:
    def available(self):
        return {"available": False, "detail": "Test double; Docker not connected"}

    def run(self, *args):
        raise AssertionError("Unexpected Docker call")


@pytest.fixture
def app(tmp_path):
    return create_app(tmp_path / "data", sandbox=UnavailableSandbox())


@pytest.mark.parametrize("case", load_cases(), ids=lambda case: case["id"])
def test_reference_http_matches_manual_corpus(app, tmp_path, case):
    with TestClient(app) as client, TestClient(app) as stranger:
        result = evaluate_case(client, stranger, case, "reference", tmp_path)
    assert result["passed"], result


def test_evaluator_rejects_missing_docker(app, tmp_path):
    with TestClient(app) as client, TestClient(app) as stranger:
        result = evaluate_case(client, stranger, load_cases()[0], "sandbox", tmp_path)
    assert not result["passed"]
    assert "Run failed" in result["error"]


def test_manual_oracle_rejects_wrong_total(app, tmp_path):
    case = copy.deepcopy(load_cases()[1])
    case["expected"]["total_variance"] = "0.59"
    with TestClient(app) as client, TestClient(app) as stranger:
        result = evaluate_case(client, stranger, case, "reference", tmp_path)
    assert not result["passed"]
    assert "manually calculated" in result["error"]


def test_evaluator_rejects_rehashed_receipt_with_different_input(app, tmp_path):
    case = load_cases()[1]
    csv_text = (CORPUS / (case["id"] + ".csv")).read_text(encoding="utf-8")
    with TestClient(app) as client:
        run = client.post("/api/runs", json={"csv": csv_text, "mode": "reference"},
                          headers={"X-Prooflane-Request": "1"}).json()
        receipt = client.get(f"/api/runs/{run['id']}/receipt").json()
    # Arithmetic is unchanged and the hashes are recomputed, but this is not the submitted input.
    receipt["input_csv"] = csv_text.replace("Exact cents", "Replaced note")
    receipt.pop("receipt_sha256")
    receipt = make_receipt(receipt)
    run["receipt_hash"] = receipt["receipt_sha256"]
    with pytest.raises(ValueError, match="input differs"):
        check_run(run, receipt, case, csv_text, "reference")
