"""Immutable, one-cell hypothetical scenarios and independently checked bundles.

No generated code runs here. A scenario's execution goes through the regular app
pipeline; this module validates the relationship between its two input versions.
"""
import csv
import io
from decimal import Decimal

from .analysis import FIELDS, InputError, canonical, digest, parse_csv
from .receipts import check_receipt

EDITABLE_FIELDS = ("quantity", "unit_price", "contract_price")


def apply_assumption(csv_text, row, field, value):
    rows = parse_csv(csv_text)
    if type(row) is not int or not 2 <= row <= len(rows) + 1:
        raise InputError("Choose an existing source record.")
    if field not in EDITABLE_FIELDS or not isinstance(value, str) or not 1 <= len(value) <= 32:
        raise InputError("Change quantity, unit price or contract price only.")
    before = rows[row - 2][field]
    proposed = value.strip()
    if before == proposed:
        raise InputError("The proposed value must differ from the original value.")
    rows[row - 2][field] = proposed
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=FIELDS, extrasaction="ignore", lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    candidate = output.getvalue()
    validated = parse_csv(candidate)
    after = validated[row - 2][field]
    if Decimal(before) == Decimal(after):
        raise InputError("The proposed value must change the numeric assumption.")
    return candidate, {"row": row, "field": field, "before": before, "after": after}


def compare_receipts(baseline, scenario):
    check_receipt(baseline)
    check_receipt(scenario)
    if baseline.get("lineage"):
        raise ValueError("Use an original review as the baseline, not another scenario.")
    lineage = scenario.get("lineage")
    if not isinstance(lineage, dict) or set(lineage) != {"schema", "baseline_run_id", "baseline_receipt_sha256", "change"}:
        raise ValueError("Missing or invalid scenario lineage.")
    if lineage["schema"] != "prooflane.scenario.v1":
        raise ValueError("Unsupported scenario lineage.")
    if lineage["baseline_run_id"] != baseline["run_id"] or lineage["baseline_receipt_sha256"] != baseline["receipt_sha256"]:
        raise ValueError("Scenario is linked to a different baseline.")
    if scenario["run_id"] == baseline["run_id"]:
        raise ValueError("A scenario must have a separate run ID.")
    if scenario["provenance"]["mode"] != baseline["provenance"]["mode"]:
        raise ValueError("Baseline and scenario must use the same execution mode.")
    change = lineage["change"]
    if not isinstance(change, dict) or set(change) != {"row", "field", "before", "after"}:
        raise ValueError("Invalid declared source change.")
    expected_csv, actual_change = apply_assumption(baseline["input_csv"], change["row"], change["field"], change["after"])
    if canonical(actual_change) != canonical(change):
        raise ValueError("The declared original value does not match the baseline.")
    if canonical(parse_csv(scenario["input_csv"])) != canonical(parse_csv(expected_csv)):
        raise ValueError("Scenario contains undeclared source changes.")
    before_summary, after_summary = baseline["summary"], scenario["summary"]
    row_number = change["row"]
    source = parse_csv(baseline["input_csv"])[row_number - 2]
    before_variance = next((f["variance"] for f in before_summary["findings"] if f["row"] == row_number), "0.00")
    after_variance = next((f["variance"] for f in after_summary["findings"] if f["row"] == row_number), "0.00")

    def totals(receipt):
        return {"run_id": receipt["run_id"], "receipt_sha256": receipt["receipt_sha256"],
                "mode": receipt["provenance"]["mode"],
                **{key: receipt["summary"][key] for key in ("row_count", "flagged_count", "total_billed", "total_variance")}}

    return {"scope": "Hypothetical assumption; not a contract correction, payment instruction or recovered savings.",
            "baseline": totals(baseline), "scenario": totals(scenario),
            "delta": {"total_variance": f"{Decimal(after_summary['total_variance']) - Decimal(before_summary['total_variance']):.2f}",
                      "total_billed": f"{Decimal(after_summary['total_billed']) - Decimal(before_summary['total_billed']):.2f}",
                      "flagged_count": after_summary["flagged_count"] - before_summary["flagged_count"]},
            "change": {**change, "invoice_id": source["invoice_id"], "vendor": source["vendor"],
                       "before_variance": before_variance, "after_variance": after_variance,
                       "variance_delta": f"{Decimal(after_variance) - Decimal(before_variance):.2f}"},
            "unchanged_records": len(parse_csv(expected_csv)) - 1}


def make_bundle(baseline, scenario):
    body = {"schema": "prooflane.comparison.v1", "baseline": baseline, "scenario": scenario,
            "comparison": compare_receipts(baseline, scenario)}
    return {**body, "bundle_sha256": digest(canonical(body))}


def check_bundle(bundle):
    if not isinstance(bundle, dict) or set(bundle) != {"schema", "baseline", "scenario", "comparison", "bundle_sha256"}:
        raise ValueError("Invalid comparison bundle structure.")
    if bundle["schema"] != "prooflane.comparison.v1":
        raise ValueError("Unsupported comparison bundle.")
    body = {k: v for k, v in bundle.items() if k != "bundle_sha256"}
    if digest(canonical(body)) != bundle["bundle_sha256"]:
        raise ValueError("Comparison bundle hash mismatch.")
    actual = compare_receipts(bundle["baseline"], bundle["scenario"])
    if canonical(actual) != canonical(bundle["comparison"]):
        raise ValueError("Comparison deltas do not match independently recalculated results.")
    return {"passed": True, "checks": ["Both receipt hashes and arithmetic", "Baseline identity and hash",
            "Exactly one declared source assumption", "Same execution mode", "Every signed delta"],
            "comparison": actual,
            "scope": "Integrity and arithmetic only. No authentication of issuer, execution host or truth of the assumption."}
