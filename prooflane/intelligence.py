"""Exact, deterministic exploration of declared assumptions; no AI or causal claims."""
import csv
import io
from decimal import Decimal

from .analysis import FIELDS, InputError, MONEY, canonical, parse_csv, summarize

METHOD = "prooflane.monotone-box.v1"
MAX_BOUNDS = 24
MAX_CHANGES = 12


def money(value):
    return f"{value:.2f}"


def numeric(field, value):
    if not isinstance(value, str) or not 1 <= len(value) <= 32:
        raise InputError("Values must be short decimal strings.")
    if field == "quantity":
        if not value.isascii() or not value.isdigit() or str(int(value)) != value or not 1 <= int(value) <= 999999:
            raise InputError("Quantity must be a whole number from 1 to 999999.")
    elif not MONEY.fullmatch(value):
        raise InputError("Prices must be nonnegative USD with at most two decimals.")
    return Decimal(value)


def targets_for(csv_text, bindings=None):
    rows = parse_csv(csv_text)
    by_row = {b["row"]: b for b in (bindings or [])}
    targets = {}
    for row in rows:
        n = row["row"]
        for field in ("contract_price", "unit_price", "quantity"):
            binding = by_row.get(n) if field == "contract_price" else None
            key = "contract:" + binding["contract_id"] if binding else f"row:{n}:{field}"
            if key not in targets:
                targets[key] = {"id": key, "label": f"Contract {binding['contract_id']}" if binding else f"{row['invoice_id']} · record {n} · {field.replace('_', ' ')}",
                                "field": field, "rows": [], "before": row[field], "invoice_id": row["invoice_id"]}
                if binding:
                    targets[key]["contract_id"] = binding["contract_id"]
                    targets[key]["contract_row"] = binding["contract_row"]
            if Decimal(targets[key]["before"]) != Decimal(row[field]):
                raise InputError("One contract target cannot have inconsistent source prices.")
            targets[key]["rows"].append(n)
    return list(targets.values())


def apply_changes(csv_text, targets, changes):
    if not isinstance(changes, list) or not 1 <= len(changes) <= MAX_CHANGES:
        raise InputError(f"Choose 1 to {MAX_CHANGES} distinct assumptions.")
    mapping = {t["id"]: t for t in targets}
    rows = parse_csv(csv_text)
    seen, changed_rows, normalized = set(), set(), []
    for change in changes:
        if not isinstance(change, dict) or set(change) != {"target", "value"}:
            raise InputError("Each change needs a target and decimal value.")
        key = change["target"]
        if not isinstance(key, str) or key not in mapping or key in seen:
            raise InputError("Unknown or repeated assumption target.")
        seen.add(key)
        target = mapping[key]
        value = numeric(target["field"], change["value"])
        if value == Decimal(target["before"]):
            raise InputError("Every proposed value must differ numerically from the original.")
        for n in target["rows"]:
            rows[n - 2][target["field"]] = change["value"]
            changed_rows.add(n)
        normalized.append({"target": key, "value": change["value"]})
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=FIELDS, extrasaction="ignore", lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    candidate = stream.getvalue()
    parse_csv(candidate)
    return candidate, normalized, sorted(changed_rows)


def validated_bounds(targets, bounds):
    if not isinstance(bounds, list) or len(bounds) > MAX_BOUNDS:
        raise InputError(f"At most {MAX_BOUNDS} declared ranges are supported.")
    mapping, seen, result = {t["id"]: t for t in targets}, set(), []
    for item in bounds:
        if not isinstance(item, dict) or set(item) != {"target", "low", "high"}:
            raise InputError("Each range needs a target, low and high value.")
        key = item["target"]
        if not isinstance(key, str) or key not in mapping or key in seen:
            raise InputError("Unknown or repeated range target.")
        seen.add(key)
        target = mapping[key]
        lo, hi = numeric(target["field"], item["low"]), numeric(target["field"], item["high"])
        if not lo <= Decimal(target["before"]) <= hi:
            raise InputError("A range must contain the original value, with low no greater than high.")
        result.append(dict(item))
    return result


def _box(rows, targets, bounds):
    limits = {(r["row"], f): (Decimal(r[f]), Decimal(r[f])) for r in rows for f in ("quantity", "unit_price", "contract_price")}
    mapping = {t["id"]: t for t in targets}
    for bound in bounds:
        t = mapping[bound["target"]]
        for n in t["rows"]:
            limits[n, t["field"]] = Decimal(bound["low"]), Decimal(bound["high"])
    lower, upper, details = Decimal(0), Decimal(0), []
    for r in rows:
        n = r["row"]
        q, p, c = (limits[n, f] for f in ("quantity", "unit_price", "contract_price"))
        lo, hi = q[0] * max(p[0] - c[1], 0), q[1] * max(p[1] - c[0], 0)
        lower += lo
        upper += hi
        details.append({"row": n, "invoice_id": r["invoice_id"], "vendor": r["vendor"],
                        "baseline": money(Decimal(r["quantity"]) * max(Decimal(r["unit_price"]) - Decimal(r["contract_price"]), 0)),
                        "low": money(lo), "high": money(hi), "span": money(hi - lo),
                        "guaranteed_positive": lo > 0, "possible_positive": hi > 0})
    return lower, upper, details, limits


def _leader(rows, targets, details, limits):
    """Certify one candidate against every other row; exact shared-price kinks."""
    if len(rows) < 2:
        return {"candidate_row": rows[0]["row"], "certified": False, "reason": "Only one source record; no priority comparison."}
    candidate = max(details, key=lambda r: (Decimal(r["baseline"]), Decimal(r["high"]), -r["row"]))
    a = candidate["row"]
    contract_groups = {n: t["id"] for t in targets if t["field"] == "contract_price" for n in t["rows"]}
    margins = []
    for other in details:
        b = other["row"]
        if b == a:
            continue
        if contract_groups[a] == contract_groups[b]:
            aq, ap = limits[a, "quantity"][0], limits[a, "unit_price"][0]
            bq, bp = limits[b, "quantity"][1], limits[b, "unit_price"][1]
            lo, hi = limits[a, "contract_price"]
            points = {lo, hi, *[v for v in (ap, bp) if lo <= v <= hi]}
            margin = min(aq * max(ap - c, 0) - bq * max(bp - c, 0) for c in points)
        else:
            margin = Decimal(candidate["low"]) - Decimal(other["high"])
        margins.append((margin, b))
    margin, challenger = min(margins)
    return {"candidate_row": a, "invoice_id": candidate["invoice_id"], "certified": margin > 0,
            "minimum_margin": money(margin), "challenger_row": challenger,
            "method": "Exact pairwise lower difference, including shared contract-price breakpoints.",
            "reason": "This record stays strictly above every other record throughout the declared ranges." if margin > 0 else
                      "Strict first place is not certified; ties or a different order are feasible under these ranges."}


def explore(csv_text, targets, bounds):
    rows = parse_csv(csv_text)
    bounds = validated_bounds(targets, bounds)
    baseline = summarize(rows)
    low, high, details, limits = _box(rows, targets, bounds)
    width = high - low
    mapping = {t["id"]: t for t in targets}
    row_values = {r["row"]: {f: Decimal(r[f]) for f in ("quantity", "unit_price", "contract_price")} for r in rows}
    sensitivity, review_queue = [], []
    for bound in bounds:
        t = mapping[bound["target"]]
        endpoint_totals, residual_widths = [], []
        for side in ("low", "high"):
            value = bound[side]
            # Only this target's rows change. Avoid serializing and reparsing the
            # entire source twice per bound to obtain a one-target total.
            total = Decimal(baseline["total_variance"])
            for number in t["rows"]:
                before = row_values[number]
                after = {**before, t["field"]: Decimal(value)}
                total += (after["quantity"] * max(after["unit_price"] - after["contract_price"], 0)
                          - before["quantity"] * max(before["unit_price"] - before["contract_price"], 0))
            endpoint_totals.append(total)
            # Learning this target affects only its bound rows. Keep every
            # other declared interval, including joint quantity/price effects.
            residual = width
            for number in t["rows"]:
                fixed = {field: limits[number, field] for field in ("quantity", "unit_price", "contract_price")}
                fixed[t["field"]] = (Decimal(value), Decimal(value))
                q, p, c = (fixed[field] for field in ("quantity", "unit_price", "contract_price"))
                span = q[1] * max(p[1] - c[0], 0) - q[0] * max(p[0] - c[1], 0)
                residual += span - Decimal(details[number - 2]["span"])
            residual_widths.append(residual)
        sensitivity.append({"target": t["id"], "label": t["label"], "rows": t["rows"], "low_value": bound["low"], "high_value": bound["high"],
                            "at_low": money(endpoint_totals[0]), "at_high": money(endpoint_totals[1]),
                            "outcome_span": money(abs(endpoint_totals[1] - endpoint_totals[0]))})
        review_queue.append({"target": t["id"], "label": t["label"], "rows": t["rows"],
                             "guaranteed_width_reduction": money(width - max(residual_widths)),
                             "possible_width_reduction": money(width - min(residual_widths)),
                             "reason": "Range removed by learning this input exactly; all other declared ranges remain."})
    sensitivity.sort(key=lambda x: (-Decimal(x["outcome_span"]), x["target"]))
    review_queue.sort(key=lambda x: (-Decimal(x["guaranteed_width_reduction"]), -Decimal(x["possible_width_reduction"]), x["target"]))
    break_even = []
    for t in targets:
        if t["field"] == "contract_price":
            required = max(Decimal(rows[n - 2]["unit_price"]) for n in t["rows"])
            affected = sum((Decimal(rows[n - 2]["quantity"]) * max(Decimal(rows[n - 2]["unit_price"]) - Decimal(rows[n - 2]["contract_price"]), 0) for n in t["rows"]), Decimal(0))
            break_even.append({"target": t["id"], "label": t["label"], "rows": t["rows"], "before": t["before"],
                               "zero_variance_price": money(required), "baseline_variance": money(affected)})
    break_even.sort(key=lambda x: (-Decimal(x["baseline_variance"]), x["target"]))
    return {"method": METHOD, "scope": "Exact arithmetic under declared independent target ranges. Shared contracts are single variables. Not probabilities, causal effects, contract truth or savings.",
            "baseline_variance": baseline["total_variance"], "low": money(low), "high": money(high), "width": money(width),
            "range_count": len(bounds), "rows": details, "sensitivity": sensitivity, "review_queue": review_queue,
            "break_even": break_even, "leader": _leader(rows, targets, details, limits),
            "method_notes": ["Interval extrema are joint feasible corners; positive-only variance is monotone in each target.",
                             "Sensitivity varies one target with all others fixed. Its deltas must not be added for joint scenarios.",
                             "Next evidence ranks deterministic range reduction, not expected financial benefit."]}


def comparison_delta(original, scenario):
    return {"total_variance": money(Decimal(scenario["total_variance"]) - Decimal(original["total_variance"])),
            "total_billed": money(Decimal(scenario["total_billed"]) - Decimal(original["total_billed"])),
            "flagged_count": scenario["flagged_count"] - original["flagged_count"]}
