import pytest

from prooflane.analysis import InputError, parse_csv, summarize
from prooflane.intelligence import apply_changes, explore, targets_for

CSV = "invoice_id,vendor,quantity,unit_price,contract_price,notes\nA,Vendor,40,85,72,a\nB,Vendor,10,82,72,b\n"
BINDINGS = [{"row": 2, "invoice_row": 2, "contract_id": "C1", "contract_row": 2},
            {"row": 3, "invoice_row": 3, "contract_id": "C1", "contract_row": 2}]


def test_shared_contract_change_and_tight_bounds():
    targets = targets_for(CSV, BINDINGS)
    candidate, changes, rows = apply_changes(CSV, targets, [{"target": "contract:C1", "value": "80.00"}])
    assert rows == [2, 3]
    assert summarize(parse_csv(candidate))["total_variance"] == "220.00"
    result = explore(CSV, targets, [{"target": "contract:C1", "low": "70", "high": "90"}])
    assert (result["low"], result["high"], result["width"]) == ("0.00", "720.00", "720.00")
    assert result["review_queue"][0]["guaranteed_width_reduction"] == "720.00"
    assert result["sensitivity"][0]["at_high"] == "0.00"
    assert result["break_even"][0]["zero_variance_price"] == "85.00"


def test_joint_changes_are_not_added_oat_deltas():
    targets = targets_for(CSV)
    candidate, _, _ = apply_changes(CSV, targets, [{"target": "row:2:quantity", "value": "80"},
                                                  {"target": "row:2:contract_price", "value": "80"}])
    # Original620; q-only1140; price-only300. Joint500, NOT820.
    assert summarize(parse_csv(candidate))["total_variance"] == "500.00"


def test_shared_dependency_certifies_order_when_marginals_overlap():
    csv = "invoice_id,vendor,quantity,unit_price,contract_price,notes\nA,V,10,20,10,a\nB,V,10,15,10,b\n"
    result = explore(csv, targets_for(csv, BINDINGS), [{"target": "contract:C1", "low": "10", "high": "18"}])
    assert result["rows"][0]["low"] == "20.00"
    assert result["rows"][1]["high"] == "50.00"
    assert result["leader"]["certified"] is True
    assert result["leader"]["minimum_margin"] == "20.00"


def test_next_fact_exposes_interaction_hidden_from_oat():
    csv = "invoice_id,vendor,quantity,unit_price,contract_price,notes\nA,V,1,10,10,a\n"
    bounds = [{"target": "row:2:quantity", "low": "1", "high": "100"},
              {"target": "row:2:unit_price", "low": "10", "high": "11"}]
    result = explore(csv, targets_for(csv), bounds)
    assert (result["low"], result["high"]) == ("0.00", "100.00")
    q = next(i for i in result["sensitivity"] if i["target"].endswith("quantity"))
    assert q["outcome_span"] == "0.00"
    q_fact = next(i for i in result["review_queue"] if i["target"].endswith("quantity"))
    assert q_fact["possible_width_reduction"] == "99.00"
    assert q_fact["guaranteed_width_reduction"] == "0.00"


@pytest.mark.parametrize("bounds", [
    [{"target": "contract:C1", "low": "73", "high": "80"}],
    [{"target": "row:2:quantity", "low": "1.5", "high": "80"}],
    [{"target": "row:2:contract_price", "low": "70", "high": "80"}],
    [{"target": "contract:C1", "low": "70", "high": "80"}] * 2,
])
def test_invalid_and_conflicting_bounds_rejected(bounds):
    with pytest.raises(InputError):
        explore(CSV, targets_for(CSV, BINDINGS), bounds)


def test_empty_bounds_are_exact_original_and_no_op_rejected():
    targets = targets_for(CSV, BINDINGS)
    result = explore(CSV, targets, [])
    assert result["low"] == result["high"] == "620.00"
    assert result["width"] == "0.00"
    with pytest.raises(InputError):
        apply_changes(CSV, targets, [{"target": "contract:C1", "value": "72.00"}])
