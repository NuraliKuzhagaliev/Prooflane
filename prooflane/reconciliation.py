"""Exact dated source matching. Ambiguity is exposed, never guessed away."""
import csv
import io
import re
from datetime import date

from .analysis import FIELDS, InputError, MAX_CSV_BYTES, MAX_ROWS, canonical, digest, parse_csv, validate_price, validate_quantity

INVOICE_FIELDS = ["invoice_id", "vendor", "item_id", "invoice_date", "quantity", "unit_price", "notes"]
CONTRACT_FIELDS = ["contract_id", "vendor", "item_id", "valid_from", "valid_to", "contract_price"]


def _csv(text, fields):
    if not isinstance(text, str):
        raise InputError("Source must be UTF-8 CSV text.")
    try:
        if not text.strip() or len(text.encode("utf-8")) > MAX_CSV_BYTES or "\x00" in text:
            raise InputError("Each source must be non-empty and at most 128 KiB, without null bytes.")
        reader = csv.DictReader(io.StringIO(text.lstrip("\ufeff")), strict=True)
        if reader.fieldnames != fields:
            raise InputError("Source columns must be: " + ",".join(fields))
        rows = []
        for n, value in enumerate(reader, 2):
            if len(rows) >= MAX_ROWS or None in value or any(v is None for v in value.values()):
                raise InputError("Each source is limited to 500 complete records.")
            item = {k: v.strip() for k, v in value.items()}
            if any(len(v) > 300 for v in item.values()) or any(not v for k, v in item.items() if k != "notes"):
                raise InputError(f"Source record {n}: required cells must be non-empty and at most 300 characters.")
            rows.append({**item, "row": n})
    except (UnicodeError, csv.Error) as exc:
        raise InputError("Malformed source CSV or invalid UTF-8.") from exc
    if not rows:
        raise InputError("Source has no data records.")
    return rows


def _date(value):
    if not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", value):
        raise InputError("Dates must use YYYY-MM-DD.")
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise InputError("Invalid calendar date.") from exc


def _serialize(rows):
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=FIELDS, extrasaction="ignore", lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue()


def reconcile(invoices_csv, contracts_csv, selections=None, exclusions=None):
    invoices, contracts = _csv(invoices_csv, INVOICE_FIELDS), _csv(contracts_csv, CONTRACT_FIELDS)
    selections = {} if selections is None else selections
    exclusions = {} if exclusions is None else exclusions
    allowed = {str(i["row"]) for i in invoices}
    for decisions in (selections, exclusions):
        if not isinstance(decisions, dict) or any(k not in allowed or not isinstance(v, str) for k, v in decisions.items()):
            raise InputError("Decisions must refer to existing invoice source records.")
    if set(selections) & set(exclusions):
        raise InputError("A source record cannot be selected and excluded at the same time.")
    if any(not 3 <= len(v.strip()) <= 200 for v in exclusions.values()):
        raise InputError("Every exclusion requires a reason of 3 to 200 characters.")
    for text in [*selections.values(), *exclusions.values()]:
        try:
            text.encode("utf-8")
        except UnicodeError as exc:
            raise InputError("Decisions must be valid UTF-8.") from exc
    ids, index = set(), {}
    for c in contracts:
        if c["contract_id"] in ids:
            raise InputError("Contract IDs must be unique; use a distinct ID for each version.")
        ids.add(c["contract_id"])
        if _date(c["valid_from"]) > _date(c["valid_to"]):
            raise InputError("Contract valid_from must not follow valid_to.")
        # Same numeric validators as canonical CSV, without a tiny CSV roundtrip
        # per record. The complete canonical result is still parsed below.
        validate_price(c["contract_price"], "contract_price", c["row"])
        index.setdefault((c["vendor"], c["item_id"]), []).append(c)
    counts = {"total": len(invoices), "matched": 0, "selected": 0, "unresolved": 0, "excluded": 0}
    records, canonical_rows, bindings = [], [], []
    candidate_links = 0
    for invoice in invoices:
        _date(invoice["invoice_date"])
        validate_quantity(invoice["quantity"], invoice["row"])
        validate_price(invoice["unit_price"], "unit_price", invoice["row"])
        n, key = invoice["row"], str(invoice["row"])
        candidates = [c for c in index.get((invoice["vendor"], invoice["item_id"]), [])
                      if c["valid_from"] <= invoice["invoice_date"] <= c["valid_to"]]
        candidate_links += len(candidates)
        if candidate_links > 5000:
            raise InputError("More than 5,000 eligible source links. Narrow the source files or remove overlapping contract versions.")
        chosen = None
        if key in exclusions:
            status = "excluded"
        elif key in selections:
            chosen = next((c for c in candidates if c["contract_id"] == selections[key]), None)
            if chosen is None:
                raise InputError(f"Invoice record {n}: selection is not an eligible contract.")
            status = "selected"
        elif len(candidates) == 1:
            chosen, status = candidates[0], "matched"
        else:
            status = "unmatched" if not candidates else "ambiguous"
        counts[status if status in counts else "unresolved"] += 1
        records.append({**{k: invoice[k] for k in ("invoice_id", "vendor", "item_id", "invoice_date", "quantity", "unit_price", "notes")},
                        "invoice_row": n, "status": status, "chosen_contract_id": chosen["contract_id"] if chosen else None,
                        "reason": exclusions.get(key, ""), "candidates": [
                            {"contract_row": c["row"], **{k: c[k] for k in ("contract_id", "contract_price", "valid_from", "valid_to")}} for c in candidates]})
        if chosen:
            bindings.append({"row": len(canonical_rows) + 2, "invoice_row": n,
                             "contract_id": chosen["contract_id"], "contract_row": chosen["row"]})
            canonical_rows.append({**invoice, "contract_price": chosen["contract_price"]})
    ready = counts["unresolved"] == 0 and bool(canonical_rows)
    normalized = _serialize(canonical_rows) if ready else None
    if normalized:
        parse_csv(normalized)
    return {"ready": ready, "counts": counts, "records": records, "canonical_csv": normalized,
            "bindings": bindings, "source_hashes": {"invoices": digest(invoices_csv), "contracts": digest(contracts_csv)},
            "scope": "Exact vendor/item/date matching against supplied sources; no authentication of contract truth. Exclusions limit coverage."}


def source_result(sources):
    if not isinstance(sources, dict):
        raise InputError("Invalid case sources.")
    if sources.get("kind") == "contracts" and set(sources) == {"kind", "invoices_csv", "contracts_csv", "selections", "exclusions"}:
        result = reconcile(sources["invoices_csv"], sources["contracts_csv"], sources["selections"], sources["exclusions"])
        if not result["ready"]:
            raise InputError("Resolve every unmatched or ambiguous record before creating a baseline.")
        return result
    if sources.get("kind") == "embedded" and set(sources) == {"kind", "csv"}:
        rows = parse_csv(sources["csv"])
        return {"ready": True, "canonical_csv": sources["csv"], "bindings": [],
                "counts": {"total": len(rows), "matched": 0, "selected": 0, "unresolved": 0, "excluded": 0, "embedded": len(rows)},
                "records": [{**r, "invoice_row": r["row"], "status": "embedded", "candidates": [], "chosen_contract_id": None, "reason": ""} for r in rows],
                "scope": "Contract prices embedded in invoice CSV; no separate contract source was checked."}
    raise InputError("Unsupported source evidence structure.")
