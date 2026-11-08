"""Independent cent enumeration for the priority-switch boundary search."""
import itertools
from decimal import Decimal
from pathlib import Path

from prooflane.intelligence import targets_for
from prooflane.priority import priority_switch
from prooflane.reconciliation import reconcile


def test_fictional_contract_switch_preserves_the_exact_tie():
    source = reconcile(Path("examples/case-invoices.csv").read_text(encoding="utf-8"),
                       Path("examples/case-contracts.csv").read_text(encoding="utf-8"),
                       {"5": "C2R"}, {"7": "No active contract in the synthetic fixture."})
    result = priority_switch(source["canonical_csv"], targets_for(source["canonical_csv"], source["bindings"]))
    assert result["candidate_row"] == 2
    assert result["affected_rows"] == [2, 3, 8]
    assert result["strict_price_interval"] == {"low": "0.00", "high": "82.59"}
    change, = result["transitions"]
    assert change["direction"] == "increase"
    assert [change[key]["price"] for key in ("last_strict", "at", "beyond")] == ["82.59", "82.60", "82.61"]
    assert [(row["invoice_id"], row["variance"]) for row in change["at"]["leaders"]] == [("INV501", "96.00"), ("INV503", "96.00")]
    assert change["beyond"]["leaders"] == [{"row": 4, "invoice_id": "INV503", "variance": "96.00"}]


def test_small_cent_grids_match_every_boundary_and_witness():
    for shared, qa, qb, pa, pb, contract, outsider in itertools.product(
            (False, True), (1, 3), (1, 2), (2, 5, 10), (1, 4, 8), (0, 1, 3, 7), (1, 4)):
        prices, quantities, contracts = [pa, pb, outsider], [qa, qb, 1], [contract, contract, 0]
        lines = ["invoice_id,vendor,quantity,unit_price,contract_price,notes"]
        for number, (quantity, price, nominal) in enumerate(zip(quantities, prices, contracts), 2):
            lines.append(f"DUP,V,{quantity},0.{price:02d},0.{nominal:02d},Synthetic {number}")
        csv = "\n".join(lines) + "\n"
        bindings = [{"row": 2, "contract_id": "C1", "contract_row": 2},
                    {"row": 3, "contract_id": "C1" if shared else "C2", "contract_row": 2 if shared else 3},
                    {"row": 4, "contract_id": "C3", "contract_row": 4}]
        result = priority_switch(csv, targets_for(csv, bindings))
        original = [quantity * max(price - nominal, 0) for quantity, price, nominal in zip(quantities, prices, contracts)]
        leaders = [index for index, value in enumerate(original) if value == max(original)]
        if len(leaders) > 1:
            assert result["status"] == "baseline_tie"
            continue
        candidate, = leaders
        group = {candidate}
        if shared and candidate in (0, 1):
            group = {0, 1}

        def values_at(price):
            return [quantity * max(billed - (price if index in group else nominal), 0)
                    for index, (quantity, billed, nominal) in enumerate(zip(quantities, prices, contracts))]

        strict = []
        for price in range(max(prices) + 2):
            values = values_at(price)
            if values[candidate] > 0 and all(index == candidate or values[candidate] > amount for index, amount in enumerate(values)):
                strict.append(price)
        assert result["candidate_row"] == candidate + 2
        assert result["affected_rows"] == [index + 2 for index in sorted(group)]
        interval = result["strict_price_interval"]
        assert [int(Decimal(interval[side]) * 100) for side in ("low", "high")] == [min(strict), max(strict)]
        boundaries = {min(strict) - 1, max(strict) + 1} - {-1}
        assert {int(Decimal(item["at"]["price"]) * 100) for item in result["transitions"]} == boundaries
        for change in result["transitions"]:
            for key in ("last_strict", "at", "beyond"):
                witness = change[key]
                if witness is None:
                    continue
                values = values_at(int(Decimal(witness["price"]) * 100))
                assert int(Decimal(witness["candidate_variance"]) * 100) == values[candidate]
                expected = [index + 2 for index, value in enumerate(values) if value == max(values) and value > 0]
                assert [row["row"] for row in witness["leaders"]] == expected


def test_noncent_crossing_never_invents_a_tie():
    csv = "invoice_id,vendor,quantity,unit_price,contract_price,notes\nA,V,3,0.10,0.00,a\nB,V,1,0.01,0.00,b\n"
    result = priority_switch(csv, targets_for(csv))
    change, = result["transitions"]
    assert change["last_strict"]["price"] == "0.09"
    assert change["at"]["price"] == "0.10"
    assert change["at"]["status"] == "unique"
    assert change["at"]["leaders"][0]["invoice_id"] == "B"


def test_empty_or_single_priority_is_explained():
    zero = "invoice_id,vendor,quantity,unit_price,contract_price,notes\nA,V,1,1.00,1.00,a\n"
    single = zero.replace("1.00,1.00", "2.00,1.00")
    assert priority_switch(zero, targets_for(zero))["status"] == "no_positive"
    assert priority_switch(single, targets_for(single))["status"] == "single_invoice"
