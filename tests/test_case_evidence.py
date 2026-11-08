"""Offline consistency attacks on synthetic artifacts; no runtime attestation claim."""
import copy
import subprocess
import sys
from pathlib import Path

import pytest

from prooflane.analysis import canonical, contract_output, digest, parse_csv, summarize
from prooflane.case_evidence import check_case_packet, make_case_packet
from prooflane.intelligence import apply_changes, targets_for
from prooflane.receipts import check_receipt, make_receipt
from prooflane.reconciliation import reconcile

INVOICES = Path("examples/case-invoices.csv").read_text(encoding="utf-8")
CONTRACTS = Path("examples/case-contracts.csv").read_text(encoding="utf-8")


def receipt_for(csv_text, run_id, context=None, mode="reference"):
    summary = summarize(parse_csv(csv_text))
    payload = {"run_id": run_id, "input_csv": csv_text, "code": "synthetic arithmetic fixture; not executed",
               "output": contract_output(summary), "summary": summary, "provenance": {"mode": mode, "model_calls": 0}}
    if context is not None:
        payload["case_context"] = context
    return make_receipt(payload)


def fixture_parts():
    sources = {"kind": "contracts", "invoices_csv": INVOICES, "contracts_csv": CONTRACTS,
               "selections": {"5": "C2R"}, "exclusions": {"7": "No active supplied contract; excluded from this review"}}
    source = reconcile(INVOICES, CONTRACTS, sources["selections"], sources["exclusions"])
    baseline = receipt_for(source["canonical_csv"], "base-fixture", {"kind":"baseline", "case_id":"case-fixture"})
    changes = [{"target": "contract:C1", "value": "80.00"}]
    csv_text, changes, changed_rows = apply_changes(source["canonical_csv"], targets_for(source["canonical_csv"], source["bindings"]), changes)
    context = {"kind": "alternative", "case_id": "case-fixture", "baseline_run_id": baseline["run_id"],
               "baseline_receipt_sha256": baseline["receipt_sha256"], "changes": changes}
    alternative = {"name": "Revised shared contract", "changes": changes, "changed_rows": changed_rows,
                   "receipt": receipt_for(csv_text, "variant-fixture", context)}
    case = {"id": "case-fixture", "name": "Synthetic supplier review", "created_at": "2026-11-04T00:00:00+00:00",
            "sources": sources, "bounds": [{"target": "contract:C1", "low": "65.00", "high": "85.00"}]}
    return case, baseline, [alternative]


def rehash(packet):
    packet["case_sha256"] = digest(canonical({k: v for k, v in packet.items() if k != "case_sha256"}))
    return packet


def test_case_packet_reconstructs_manual_totals_shared_changes_and_complete_scope():
    case, baseline, alternatives = fixture_parts()
    original = canonical(baseline)
    packet = make_case_packet(case, baseline, alternatives)
    result = check_case_packet(packet)
    assert result["passed"] is True
    assert result["counts"] == {"total": 8, "matched": 6, "selected": 1, "unresolved": 0, "excluded": 1}
    assert result["range"] == {"low": "148.00", "high": "1193.00", "width": "1045.00"}
    assert packet["comparisons"][0]["total_variance"] == "368.00"
    assert packet["comparisons"][0]["changed_rows"] == [2, 3, 8]
    assert packet["comparisons"][0]["delta"] == {"total_variance": "-400.00", "total_billed": "0.00", "flagged_count": 0}
    assert canonical(baseline) == original
    assert "No issuer authentication" in result["scope"]


def test_priority_boundary_is_reconstructed_and_legacy_packets_still_verify():
    packet = make_case_packet(*fixture_parts())
    assert packet["priority_switch"]["transitions"][0]["at"]["price"] == "82.60"
    changed = copy.deepcopy(packet)
    changed["priority_switch"]["transitions"][0]["at"]["price"] = "82.61"
    with pytest.raises(ValueError, match="Reconstructed priority switch"):
        check_case_packet(rehash(changed))
    del packet["priority_switch"]
    assert check_case_packet(rehash(packet))["passed"]


def test_rehashed_partial_shared_propagation_fails_despite_valid_standalone_arithmetic():
    case, baseline, alternatives = fixture_parts()
    forged = copy.deepcopy(alternatives)
    csv_text = forged[0]["receipt"]["input_csv"].replace("10,82.00,80.00", "10,82.00,72.00")
    forged[0]["receipt"] = receipt_for(csv_text, "variant-fixture", forged[0]["receipt"]["case_context"])
    assert check_receipt(forged[0]["receipt"])["passed"] is True
    with pytest.raises(ValueError, match="undeclared|propagation"):
        make_case_packet(case, baseline, forged)


@pytest.mark.parametrize("target", ["range", "priority", "comparison", "coverage", "source_decision"])
def test_rehashed_derived_forgery_is_rejected_by_recalculation(target):
    packet = make_case_packet(*fixture_parts())
    if target == "range":
        packet["intelligence"]["high"] = "999999.00"
    elif target == "priority":
        packet["intelligence"]["review_queue"][0]["guaranteed_width_reduction"] = "0.00"
    elif target == "comparison":
        packet["comparisons"][0]["delta"]["total_variance"] = "-9999.00"
    elif target == "coverage":
        packet["source"]["counts"]["excluded"] = 0
    else:
        packet["sources"]["exclusions"]["7"] = "Different reason not reflected in evidence"
    with pytest.raises(ValueError, match="Reconstructed"):
        check_case_packet(rehash(packet))


def test_rehashed_source_contract_cannot_disagree_with_baseline():
    packet = make_case_packet(*fixture_parts())
    packet["sources"]["contracts_csv"] = CONTRACTS.replace("72.00", "71.00")
    with pytest.raises(ValueError, match="Baseline input"):
        check_case_packet(rehash(packet))


@pytest.mark.parametrize("damage", ["parent_hash", "case_identity", "mode", "duplicate_run", "changed_rows", "duplicate_name"])
def test_false_alternative_identity_and_scope_are_rejected(damage):
    case, baseline, alternatives = fixture_parts()
    variant = alternatives[0]
    if damage == "changed_rows":
        variant["changed_rows"] = [2]
    elif damage == "duplicate_name":
        alternatives.append(copy.deepcopy(variant))
    else:
        body = {k: v for k, v in variant["receipt"].items() if k != "receipt_sha256"}
        if damage == "parent_hash":
            body["case_context"]["baseline_receipt_sha256"] = "0" * 64
        elif damage == "case_identity":
            body["case_context"]["case_id"] = "foreign-case"
        elif damage == "mode":
            body["provenance"]["mode"] = "sandbox"
        else:
            body["run_id"] = baseline["run_id"]
        variant["receipt"] = make_receipt(body)
    with pytest.raises(ValueError):
        make_case_packet(case, baseline, alternatives)


@pytest.mark.parametrize("field,value", [("name", []), ("name", "\ud800"), ("name", "x" * 81),
                                         ("created_at", []), ("case_id", "\ud800")])
def test_rehashed_malformed_metadata_is_not_returned_to_browser(field, value):
    packet = make_case_packet(*fixture_parts())
    packet[field] = value
    with pytest.raises((ValueError, UnicodeError)):
        check_case_packet(rehash(packet))


def test_embedded_legacy_csv_can_be_checked_without_claiming_contract_source():
    csv_text = "invoice_id,vendor,quantity,unit_price,contract_price,notes\nA,V,2,12,10,legacy\n"
    baseline = receipt_for(csv_text, "legacy-original")
    case = {"id": "legacy-case", "name": "Original CSV", "created_at": "2026-11-04T00:00:00+00:00",
            "sources": {"kind": "embedded", "csv": csv_text}, "bounds": []}
    packet = make_case_packet(case, baseline, [])
    result = check_case_packet(packet)
    assert result["range"] == {"low": "4.00", "high": "4.00", "width": "0.00"}
    assert result["counts"]["embedded"] == 1
    assert "no separate contract source" in packet["source"]["scope"]


def test_offline_cli_checks_complete_packet_and_rejects_rehashed_forgery(tmp_path):
    case, baseline, alternatives = fixture_parts()
    # Valid code hash is not evidence that code was executed. This verifier must not run it.
    baseline_body = {k:v for k,v in baseline.items() if k != "receipt_sha256"}
    baseline_body["code"] = "raise AssertionError('Artifact verifier must not execute receipt code')"
    baseline = make_receipt(baseline_body)
    packet = make_case_packet(case, baseline, [])
    path = tmp_path / "synthetic-case.json"
    path.write_text(canonical(packet), encoding="utf-8")
    checked = subprocess.run([sys.executable, "scripts/verify_receipt.py", str(path)], capture_output=True, text=True, timeout=15)
    assert checked.returncode == 0, checked.stdout + checked.stderr
    assert '"passed": true' in checked.stdout
    packet["intelligence"]["high"] = "123456.00"
    path.write_text(canonical(rehash(packet)), encoding="utf-8")
    rejected = subprocess.run([sys.executable, "scripts/verify_receipt.py", str(path)], capture_output=True, text=True, timeout=15)
    assert rejected.returncode != 0
    assert "FAIL:" in rejected.stderr
