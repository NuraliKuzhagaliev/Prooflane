"""Trusted fixed arithmetic. This module never executes submitted/generated code."""
import csv
import hashlib
import io
import json
import re
from collections import defaultdict
from decimal import Decimal

MAX_CSV_BYTES = 131072
MAX_ROWS = 500
FIELDS = ["invoice_id", "vendor", "quantity", "unit_price", "contract_price", "notes"]
MONEY = re.compile(r"^(?:0|[1-9][0-9]{0,7})(?:\.[0-9]{1,2})?$")


class InputError(ValueError):
    pass


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False)


def digest(value):
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def validate_quantity(value, row_number):
    if not re.fullmatch(r"[1-9][0-9]{0,5}", value):
        raise InputError(f"Record {row_number}: quantity must be an integer from 1 to 999999.")


def validate_price(value, field, row_number):
    if not MONEY.fullmatch(value):
        raise InputError(f"Record {row_number}: {field} must be nonnegative USD with at most 2 decimals.")


def parse_csv(text):
    if not isinstance(text, str) or not text.strip():
        raise InputError("Choose a non-empty UTF-8 CSV file.")
    try:
        byte_length = len(text.encode("utf-8"))
    except UnicodeError as exc:
        raise InputError("CSV must contain valid UTF-8 text.") from exc
    if byte_length > MAX_CSV_BYTES or "\x00" in text:
        raise InputError("CSV must be at most 128 KiB and contain no null bytes.")
    try:
        reader = csv.DictReader(io.StringIO(text.lstrip("\ufeff")), strict=True)
        if reader.fieldnames != FIELDS:
            raise InputError("CSV columns must be: " + ",".join(FIELDS))
        rows = []
        for row_number, values in enumerate(reader, start=2):
            if len(rows) >= MAX_ROWS:
                raise InputError("CSV is limited to 500 records.")
            if None in values or any(v is None for v in values.values()):
                raise InputError(f"Record {row_number}: unexpected number of columns.")
            row = {k: v.strip() for k, v in values.items()}
            if not row["invoice_id"] or not row["vendor"]:
                raise InputError(f"Record {row_number}: invoice ID and vendor are required.")
            if any(len(v) > 300 for v in row.values()):
                raise InputError(f"Record {row_number}: cells must be at most 300 characters.")
            validate_quantity(row["quantity"], row_number)
            for field in ("unit_price", "contract_price"):
                validate_price(row[field], field, row_number)
            rows.append({**row, "row": row_number})
    except (csv.Error, UnicodeError) as exc:
        raise InputError("Malformed CSV. Use a UTF-8 file with quoted commas.") from exc
    if not rows:
        raise InputError("CSV must contain at least one data record.")
    return rows


def summarize(rows):
    billed, variance = Decimal("0"), Decimal("0")
    vendors = defaultdict(lambda: Decimal("0"))
    findings = []
    for row in rows:
        quantity = int(row["quantity"])
        price, contract = Decimal(row["unit_price"]), Decimal(row["contract_price"])
        billed += price * quantity
        difference = max(price - contract, Decimal("0")) * quantity
        if difference:
            variance += difference
            vendors[row["vendor"]] += difference
            findings.append({**row, "quantity": quantity, "unit_price": f"{price:.2f}",
                             "contract_price": f"{contract:.2f}", "variance": f"{difference:.2f}"})
    return {"row_count": len(rows), "total_billed": f"{billed:.2f}", "total_variance": f"{variance:.2f}",
            "flagged_count": len(findings), "findings": findings,
            "vendors": [{"vendor": name, "variance": f"{value:.2f}"} for name, value in
                        sorted(vendors.items(), key=lambda item: (-item[1], item[0]))]}


def contract_output(summary):
    return {"row_count": summary["row_count"], "total_billed": summary["total_billed"],
            "total_variance": summary["total_variance"],
            "findings": [{"row": f["row"], "variance": f["variance"]} for f in summary["findings"]]}


def verify_output(output, expected):
    target = contract_output(expected)
    checks = []
    if not isinstance(output, dict):
        return {"passed": False, "checks": [{"name": "Output structure", "passed": False,
                 "detail": "Expected one JSON object."}]}
    checks.append({"name": "Output schema", "passed": set(output) == set(target),
                   "detail": "Only the four documented output fields are accepted."})
    for field, label in [("row_count", "Record coverage"), ("total_billed", "Billed total"),
                         ("total_variance", "Positive variance"), ("findings", "Every source record")]:
        # Canonical comparison also distinguishes bool from int and rejects duplicate/extra rows.
        passed = canonical(output.get(field)) == canonical(target[field])
        checks.append({"name": label, "passed": passed,
                       "detail": "Matches independent Decimal calculation." if passed else
                       "Does not match the independent calculation; result withheld."})
    return {"passed": all(c["passed"] for c in checks), "checks": checks}
