"""Manual source-matching oracles; fixtures are synthetic, not supplier evidence."""
from pathlib import Path

import pytest

from prooflane.analysis import InputError, parse_csv, summarize
from prooflane.reconciliation import reconcile, source_result

INVOICES = Path("examples/case-invoices.csv").read_text(encoding="utf-8")
CONTRACTS = Path("examples/case-contracts.csv").read_text(encoding="utf-8")
SELECTIONS = {"5": "C2R"}
EXCLUSIONS = {"7": "No active supplied contract; excluded from this review"}


def test_unresolved_matches_block_baseline_and_expose_candidates():
    result = reconcile(INVOICES, CONTRACTS)
    assert result["ready"] is False
    assert result["canonical_csv"] is None
    assert result["counts"] == {"total": 8, "matched": 6, "selected": 0, "unresolved": 2, "excluded": 0}
    records = {r["invoice_row"]: r for r in result["records"]}
    assert records[5]["status"] == "ambiguous"
    assert [c["contract_id"] for c in records[5]["candidates"]] == ["C2", "C2R"]
    assert records[7]["status"] == "unmatched"
    assert records[7]["candidates"] == []
    with pytest.raises(InputError, match="Resolve every"):
        source_result({"kind": "contracts", "invoices_csv": INVOICES, "contracts_csv": CONTRACTS,
                       "selections": {}, "exclusions": {}})


def test_explicit_selection_exclusion_preserve_coverage_and_record_provenance():
    result = reconcile(INVOICES, CONTRACTS, SELECTIONS, EXCLUSIONS)
    assert result["ready"] is True
    assert result["counts"] == {"total": 8, "matched": 6, "selected": 1, "unresolved": 0, "excluded": 1}
    rows = parse_csv(result["canonical_csv"])
    assert [r["invoice_id"] for r in rows] == ["INV501", "INV502", "INV503", "INV504", "INV505", "INV507", "INV508"]
    assert rows[3]["contract_price"] == "110.00"
    summary = summarize(rows)
    assert summary["row_count"] == 7
    assert summary["total_variance"] == "768.00"
    assert summary["flagged_count"] == 5
    assert summary["total_billed"] == "7110.00"
    assert [(b["row"], b["invoice_row"]) for b in result["bindings"]] == [(2,2),(3,3),(4,4),(5,5),(6,6),(7,8),(8,9)]
    assert [b["row"] for b in result["bindings"] if b["contract_id"] == "C1"] == [2, 3, 8]
    assert result["records"][5]["reason"] == EXCLUSIONS["7"]


def test_dates_include_both_endpoints_and_never_use_expired_contract():
    invoices = "invoice_id,vendor,item_id,invoice_date,quantity,unit_price,notes\nA,V,I,2026-11-01,1,2,\nB,V,I,2026-11-30,1,2,\nC,V,I,2026-12-01,1,2,\n"
    contracts = "contract_id,vendor,item_id,valid_from,valid_to,contract_price\nC,V,I,2026-11-01,2026-11-30,1\n"
    result = reconcile(invoices, contracts)
    assert [r["status"] for r in result["records"]] == ["matched", "matched", "unmatched"]
    assert result["canonical_csv"] is None


def test_exact_case_sensitive_identity_trims_cells_without_fuzzy_guessing():
    changed = INVOICES.replace("INV501,Atlas,FILTER", "INV501, Atlas , FILTER ")
    assert reconcile(changed, CONTRACTS)["records"][0]["status"] == "matched"
    changed = INVOICES.replace("INV501,Atlas,FILTER", "INV501,atlas,FILTER")
    assert reconcile(changed, CONTRACTS)["records"][0]["status"] == "unmatched"


@pytest.mark.parametrize("selections,exclusions", [
    ({"5": "C1"}, EXCLUSIONS), ({"999": "C1"}, EXCLUSIONS),
    ({"5": "C2R"}, {"5": "Conflicting decision"}), ({}, {"7": " "}),
    ([], EXCLUSIONS), ({}, []), (False, EXCLUSIONS), ({}, ""),
])
def test_invalid_decisions_are_not_silently_interpreted_as_empty(selections, exclusions):
    with pytest.raises(InputError):
        reconcile(INVOICES, CONTRACTS, selections, exclusions)


@pytest.mark.parametrize("invoices,contracts", [
    (INVOICES.replace("2026-11-01", "2026-02-30", 1), CONTRACTS),
    (INVOICES, CONTRACTS.replace("2026-11-01,2026-11-30", "2026-12-01,2026-11-30", 1)),
    (INVOICES, CONTRACTS.replace("C2R,", "C2,", 1)),
    (INVOICES, CONTRACTS.replace("72.00", "72.001", 1)),
    (INVOICES.replace(",40,85.00,", ",0,85.00,", 1), CONTRACTS),
    (INVOICES.replace("invoice_date", "date", 1), CONTRACTS),
    (INVOICES + "\x00", CONTRACTS),
])
def test_invalid_source_contract_is_rejected(invoices, contracts):
    with pytest.raises(InputError):
        reconcile(invoices, contracts, SELECTIONS, EXCLUSIONS)


def test_excluding_every_invoice_does_not_create_an_empty_verified_case():
    result = reconcile(INVOICES, CONTRACTS, {}, {str(n): "Outside review scope" for n in range(2, 10)})
    assert result["counts"]["excluded"] == 8
    assert result["counts"]["unresolved"] == 0
    assert result["ready"] is False
    assert result["canonical_csv"] is None


def test_multiline_notes_keep_csv_record_numbers_not_physical_line_numbers():
    invoices = INVOICES.replace("First shipment against shared contract", '"First line\nSecond line"')
    result = reconcile(invoices, CONTRACTS, SELECTIONS, EXCLUSIONS)
    assert result["ready"]
    assert result["records"][0]["notes"] == "First line\nSecond line"
    assert result["records"][3]["invoice_row"] == 5
    assert result["records"][3]["chosen_contract_id"] == "C2R"


def test_each_source_byte_and_record_limits_apply_before_matching():
    with pytest.raises(InputError):
        reconcile(INVOICES + "x" * 131072, CONTRACTS)
    header = INVOICES.splitlines()[0] + "\n"
    record = "X,Atlas,FILTER,2026-11-01,1,85,\n"
    with pytest.raises(InputError, match="500"):
        reconcile(header + record * 501, CONTRACTS)


def test_overlapping_contract_explosion_is_bounded_even_for_small_source_files():
    invoices = "invoice_id,vendor,item_id,invoice_date,quantity,unit_price,notes\n" + "I,V,X,2026-11-01,1,2,\n" * 100
    contracts = "contract_id,vendor,item_id,valid_from,valid_to,contract_price\n" + "".join(
        f"C{n},V,X,2026-11-01,2026-11-30,1\n" for n in range(51))
    with pytest.raises(InputError, match="5,000"):
        reconcile(invoices, contracts)
