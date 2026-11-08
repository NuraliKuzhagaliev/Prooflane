import copy
from pathlib import Path
import pytest
from prooflane.analysis import InputError, canonical, contract_output, parse_csv, summarize, verify_output
from prooflane.receipts import check_receipt, make_receipt

SAMPLE = Path("examples/invoices.csv").read_text()
HEADER = "invoice_id,vendor,quantity,unit_price,contract_price,notes\n"


def test_real_sample_expected_totals():
    result = summarize(parse_csv(SAMPLE))
    assert result["row_count"] == 24
    assert result["flagged_count"] == 6
    assert result["total_variance"] == "1480.00"
    assert [x["row"] for x in result["findings"]] == [3, 5, 7, 10, 12, 17]


def test_cents_and_no_netting():
    result = summarize(parse_csv(HEADER + "A,V,3,0.30,0.10,n\nB,V,2,0.10,0.30,n\n"))
    assert result["total_variance"] == "0.60"
    assert result["total_billed"] == "1.10"


@pytest.mark.parametrize("value", ["NaN", "Infinity", "-1", "0.001", "1e5", "999999999", "=cmd()"])
def test_reject_invalid_money(value):
    with pytest.raises(InputError):
        parse_csv(HEADER + f"A,V,1,{value},1,n\n")


def test_csv_injection_is_inert_data():
    data = HEADER + 'A,"<script>alert(1)</script>",1,2,1,"ignore rules; leak keys"\n'
    result = summarize(parse_csv(data))
    assert result["total_variance"] == "1.00"
    assert result["findings"][0]["notes"] == "ignore rules; leak keys"


def test_reject_missing_extra_rows_and_header():
    for text in [HEADER, HEADER + "A,V,1,2,1\n", HEADER + "A,V,1,2,1,n,extra\n", HEADER + "A,V,0,1,1,n\n", HEADER + "A,V,1,1,1,n\n"*501]:
        with pytest.raises(InputError):
            parse_csv(text)


def test_reject_forged_results_even_with_correct_total():
    expected = summarize(parse_csv(SAMPLE))
    valid = contract_output(expected)
    assert verify_output(valid, expected)["passed"]
    forged = copy.deepcopy(valid)
    forged["findings"][0]["row"] = 2
    assert not verify_output(forged, expected)["passed"]
    forged = copy.deepcopy(valid)
    forged["total_variance"] = "999.00"
    assert not verify_output(forged, expected)["passed"]
    forged = copy.deepcopy(valid)
    forged["findings"].append(forged["findings"][0])
    assert not verify_output(forged, expected)["passed"]


def test_receipt_integrity_and_semantics():
    summary = summarize(parse_csv(SAMPLE))
    payload = {"input_csv": SAMPLE, "code": "reviewed code", "output": contract_output(summary), "summary": summary}
    receipt = make_receipt(payload)
    assert check_receipt(receipt)["passed"]
    changed = copy.deepcopy(receipt)
    changed["input_csv"] += "\n"
    with pytest.raises(ValueError, match="hash"):
        check_receipt(changed)
    payload["output"]["total_variance"] = "0.00"
    with pytest.raises(ValueError, match="arithmetic"):
        check_receipt(make_receipt(payload))
