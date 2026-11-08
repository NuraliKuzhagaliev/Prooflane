"""Independent integer-cent enumeration of real engine results.

The oracle enumerates complete feasible target assignments. It does not use the
engine's bound, sensitivity, residual-width, or pairwise formulas for expected
values. Fixtures are synthetic; no code/model execution is claimed.
"""
import csv
import io
import itertools
from collections import defaultdict

import pytest

from prooflane.analysis import InputError
from prooflane.case_evidence import check_case_packet, make_case_packet
from prooflane.intelligence import apply_changes, explore, targets_for
from prooflane.receipts import make_receipt
from prooflane.reconciliation import reconcile


def dollars(cents):
    sign = "-" if cents < 0 else ""
    whole, fraction = divmod(abs(cents), 100)
    return f"{sign}{whole}.{fraction:02d}"


def cents(text):
    sign = -1 if text.startswith("-") else 1
    whole, fraction = text.lstrip("+-").split(".")
    return sign * (int(whole) * 100 + int(fraction))


def csv_text(fields, rows):
    stream = io.StringIO(newline="")
    writer = csv.writer(stream, lineterminator="\n")
    writer.writerow(fields)
    writer.writerows(rows)
    return stream.getvalue()


def problem(qi, qj, pi, pj, cr, shared):
    groups = ["C1", "C1" if shared else "C2"]
    domains = {"row:2:quantity": qi, "row:3:quantity": qj,
               "row:2:unit_price": pi, "row:3:unit_price": pj}
    domains.update({"contract:" + group: cr for group in groups})
    nominal = {key: (lo + hi) // 2 for key, (lo, hi) in domains.items()}
    invoices = csv_text(
        ["invoice_id", "vendor", "item_id", "invoice_date", "quantity", "unit_price", "notes"],
        [["DUPLICATE", "V", groups[i], "2026-11-01" if i == 0 else "2026-11-30",
          nominal[f"row:{i+2}:quantity"], dollars(nominal[f"row:{i+2}:unit_price"]), "Synthetic"]
         for i in range(2)])
    contracts = csv_text(
        ["contract_id", "vendor", "item_id", "valid_from", "valid_to", "contract_price"],
        [[group, "V", group, "2026-11-01", "2026-11-30", dollars(nominal["contract:" + group])]
         for group in dict.fromkeys(groups)])
    sources = {"kind": "contracts", "invoices_csv": invoices, "contracts_csv": contracts,
               "selections": {}, "exclusions": {}}
    source = reconcile(invoices, contracts)
    assert source["ready"] and source["counts"]["matched"] == 2
    assert [(b["row"], b["invoice_row"], b["contract_id"]) for b in source["bindings"]] == [
        (2, 2, groups[0]), (3, 3, groups[1])]
    targets = targets_for(source["canonical_csv"], source["bindings"])
    assert {t["id"] for t in targets} == set(domains)
    bounds = [{"target": key, "low": str(lo) if key.endswith(":quantity") else dollars(lo),
               "high": str(hi) if key.endswith(":quantity") else dollars(hi)}
              for key, (lo, hi) in domains.items()]
    return sources, source, targets, bounds, domains, nominal, groups


def row_values(state, groups):
    return tuple(state[f"row:{n}:quantity"] * max(
        state[f"row:{n}:unit_price"] - state["contract:" + group], 0)
        for n, group in enumerate(groups, 2))


def feasible_states(domains, groups):
    keys = tuple(domains)
    return [(dict(zip(keys, values)), row_values(dict(zip(keys, values)), groups))
            for values in itertools.product(*(range(lo, hi + 1) for lo, hi in domains.values()))]


@pytest.mark.parametrize("shared", [True, False], ids=["shared-contract", "independent-contracts"])
def test_complete_cent_grid_matches_bounds_oat_next_fact_and_strict_leader(shared):
    checked = 0
    for qi, qj, pi, pj, cr in itertools.product(
            [(1, 1), (1, 3)], [(1, 1), (1, 3)],
            [(0, 0), (0, 2), (2, 3)], [(0, 0), (0, 2), (2, 3)],
            [(0, 0), (0, 2), (1, 3)]):
        _, source, targets, bounds, domains, nominal, groups = problem(qi, qj, pi, pj, cr, shared)
        result = explore(source["canonical_csv"], targets, bounds)
        feasible = feasible_states(domains, groups)
        totals = [sum(values) for _, values in feasible]
        lower, upper = min(totals), max(totals)
        width = upper - lower
        assert [cents(result[key]) for key in ("low", "high", "width")] == [lower, upper, width]
        assert cents(result["baseline_variance"]) == sum(row_values(nominal, groups))
        for i, actual in enumerate(result["rows"]):
            expected = [values[i] for _, values in feasible]
            assert cents(actual["low"]) == min(expected)
            assert cents(actual["high"]) == max(expected)
            assert actual["guaranteed_positive"] == all(value > 0 for value in expected)
            assert actual["possible_positive"] == any(value > 0 for value in expected)

        sensitivities = {item["target"]: item for item in result["sensitivity"]}
        review = {item["target"]: item for item in result["review_queue"]}
        for target, (lo, hi) in domains.items():
            endpoint_totals = [sum(row_values({**nominal, target: value}, groups)) for value in (lo, hi)]
            actual = sensitivities[target]
            assert [cents(actual[key]) for key in ("at_low", "at_high")] == endpoint_totals
            assert cents(actual["outcome_span"]) == abs(endpoint_totals[1] - endpoint_totals[0])
            # Partition the entire feasible set by EVERY possible resolved value.
            # This tests the endpoint shortcut against all interior values too.
            partitions = defaultdict(list)
            for state, values in feasible:
                partitions[state[target]].append(sum(values))
            residual_widths = [max(values) - min(values) for values in partitions.values()]
            assert cents(review[target]["guaranteed_width_reduction"]) == width - max(residual_widths)
            assert cents(review[target]["possible_width_reduction"]) == width - min(residual_widths)

        leader = result["leader"]
        candidate = leader["candidate_row"] - 2
        challenger = 1 - candidate
        exact_minimum = min(values[candidate] - values[challenger] for _, values in feasible)
        assert cents(leader["minimum_margin"]) == exact_minimum
        assert leader["certified"] == (exact_minimum > 0)
        all_strict_leaders = [i for i in range(2) if all(values[i] > values[1 - i] for _, values in feasible)]
        assert bool(all_strict_leaders) == leader["certified"]
        if all_strict_leaders:
            assert all_strict_leaders == [candidate]
        checked += 1
    assert checked == 108


def test_shared_price_interior_cent_kink_is_in_exact_margin():
    # Baseline A leads 9c to 5c. At c=3c its margin reaches -2c;
    # evaluating only c=0 and c=4c would report the wrong minimum (-1c).
    text = "invoice_id,vendor,quantity,unit_price,contract_price,notes\nA,V,3,0.03,0.00,\nB,V,1,0.05,0.00,\n"
    bindings = [{"row": n, "contract_id": "C", "contract_row": 2} for n in (2, 3)]
    result = explore(text, targets_for(text, bindings), [{"target": "contract:C", "low": "0.00", "high": "0.04"}])
    assert result["leader"]["candidate_row"] == 2
    assert result["leader"]["minimum_margin"] == "-0.02"
    assert result["leader"]["certified"] is False


def test_hidden_interaction_and_joint_changes_use_source_groups():
    text = "invoice_id,vendor,quantity,unit_price,contract_price,notes\nA,V,1,0.10,0.10,\nB,V,1,0.11,0.10,\n"
    bindings = [{"row": n, "contract_id": "C", "contract_row": 2} for n in (2, 3)]
    targets = targets_for(text, bindings)
    bounds = [{"target": "row:2:quantity", "low": "1", "high": "100"},
              {"target": "contract:C", "low": "0.09", "high": "0.10"}]
    result = explore(text, targets, bounds)
    quantity = next(item for item in result["sensitivity"] if item["target"] == "row:2:quantity")
    fact = next(item for item in result["review_queue"] if item["target"] == "row:2:quantity")
    assert quantity["outcome_span"] == "0.00"
    assert (result["low"], result["high"]) == ("0.01", "1.02")
    assert (fact["guaranteed_width_reduction"], fact["possible_width_reduction"]) == ("0.00", "0.99")
    changed, _, affected = apply_changes(text, targets, [
        {"target": "row:2:quantity", "value": "100"}, {"target": "contract:C", "value": "0.09"}])
    records = list(csv.DictReader(io.StringIO(changed)))
    assert affected == [2, 3]
    assert [(int(r["quantity"]), r["contract_price"]) for r in records] == [(100, "0.09"), (1, "0.09")]
    # Independent integer cents: joint102c; baseline1c; OAT q0c and c2c deltas miss99c.
    assert sum(int(r["quantity"]) * max(cents(r["unit_price"]) - cents(r["contract_price"]), 0) for r in records) == 102


def test_twenty_four_cap_counts_distinct_targets_not_affected_rows():
    text = "invoice_id,vendor,quantity,unit_price,contract_price,notes\n" + "A,V,1,0.03,0.01,\n" * 12
    bindings = [{"row": n, "contract_id": "C", "contract_row": 2} for n in range(2, 14)]
    targets = targets_for(text, bindings)
    assert len(targets) == 25
    bounds = [{"target": t["id"], "low": t["before"], "high": t["before"]} for t in targets]
    bounds[0]["high"] = "0.02"
    result = explore(text, targets, bounds[:24])
    assert result["range_count"] == 24
    assert (result["low"], result["high"]) == ("0.12", "0.24")
    with pytest.raises(InputError, match="24"):
        explore(text, targets, bounds)


def test_one_shared_target_covers_five_hundred_rows_and_maximum_money_exactly():
    text = "invoice_id,vendor,quantity,unit_price,contract_price,notes\n" + "A,V,999999,99999999.99,0.00,\n" * 500
    bindings = [{"row": n, "contract_id": "C", "contract_row": 2} for n in range(2, 502)]
    targets = targets_for(text, bindings)
    result = explore(text, targets, [{"target": "contract:C", "low": "0.00", "high": "0.01"}])
    lower = 500 * 999999 * (9999999999 - 1)
    upper = 500 * 999999 * 9999999999
    assert (result["low"], result["high"], result["width"]) == (dollars(lower), dollars(upper), dollars(upper - lower))
    assert result["range_count"] == 1
    assert len(result["sensitivity"][0]["rows"]) == 500
    assert result["leader"]["minimum_margin"] == "0.00"
    assert not result["leader"]["certified"]


def integer_cent_receipt(text, case_id):
    """Create a receipt with independently assembled cents-based arithmetic."""
    rows = list(csv.DictReader(io.StringIO(text)))
    billed, total = 0, 0
    findings, vendors = [], defaultdict(int)
    for n, row in enumerate(rows, 2):
        quantity = int(row["quantity"])
        price, contract = cents(row["unit_price"]), cents(row["contract_price"])
        billed += quantity * price
        variance = quantity * max(price - contract, 0)
        if variance:
            total += variance
            vendors[row["vendor"]] += variance
            findings.append({**row, "row": n, "quantity": quantity, "unit_price": dollars(price),
                             "contract_price": dollars(contract), "variance": dollars(variance)})
    summary = {"row_count": len(rows), "total_billed": dollars(billed), "total_variance": dollars(total),
               "flagged_count": len(findings), "findings": findings,
               "vendors": [{"vendor": name, "variance": dollars(value)} for name, value in sorted(vendors.items(), key=lambda item: (-item[1], item[0]))]}
    output = {"row_count": len(rows), "total_billed": dollars(billed), "total_variance": dollars(total),
              "findings": [{"row": f["row"], "variance": f["variance"]} for f in findings]}
    return make_receipt({"run_id": "integer-cent-fixture", "input_csv": text,
                         "code": "synthetic independently computed fixture; never executed", "output": output,
                         "summary": summary, "provenance": {"mode": "reference", "model_calls": 0},
                         "case_context": {"kind": "baseline", "case_id": case_id}})


def test_case_packet_checks_math_against_independent_receipt_and_declared_baseline_identity():
    sources, source, _, bounds, domains, _, groups = problem((1, 3), (1, 3), (0, 2), (2, 3), (0, 2), True)
    case = {"id": "oracle-case", "name": "Oracle", "created_at": "2026-11-04T00:00:00+00:00", "sources": sources, "bounds": bounds}
    baseline = integer_cent_receipt(source["canonical_csv"], "oracle-case")
    packet = make_case_packet(case, baseline, [])
    assert check_case_packet(packet)["passed"]
    totals = [sum(values) for _, values in feasible_states(domains, groups)]
    assert (packet["intelligence"]["low"], packet["intelligence"]["high"]) == (dollars(min(totals)), dollars(max(totals)))
    contradictory_baseline = integer_cent_receipt(source["canonical_csv"], "different-case")
    with pytest.raises(ValueError, match="[Bb]aseline|context|case"):
        make_case_packet(case, contradictory_baseline, [])
    # Reusing an existing original as embedded evidence is intentionally allowed.
    embedded = {**case, "sources": {"kind": "embedded", "csv": source["canonical_csv"]}, "bounds": []}
    assert check_case_packet(make_case_packet(embedded, contradictory_baseline, []))["passed"]
