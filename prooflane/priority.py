"""Exact cent-grid boundaries for the original invoice's review priority."""
from decimal import Decimal

from .analysis import parse_csv

MAX_PRICE_CENTS = 9_999_999_999


def price_text(cents):
    return f"{cents // 100}.{cents % 100:02d}"


def priority_switch(csv_text, targets):
    rows = parse_csv(csv_text)
    values = {row["row"]: (int(row["quantity"]), int(Decimal(row["unit_price"]) * 100),
                           int(Decimal(row["contract_price"]) * 100)) for row in rows}
    original = {number: quantity * max(price - contract, 0)
                for number, (quantity, price, contract) in values.items()}
    maximum = max(original.values())
    candidates = [number for number, amount in original.items() if amount == maximum]
    scope = "One shared contract price varies in whole cents. All other inputs stay at the original baseline values."
    result = {"method": "prooflane.priority-switch.v1", "scope": scope,
              "status": "available", "transitions": []}
    if maximum == 0:
        return {**result, "status": "no_positive"}
    if len(candidates) != 1:
        return {**result, "status": "baseline_tie", "candidate_rows": candidates}
    if len(rows) == 1:
        return {**result, "status": "single_invoice", "candidate_rows": candidates}

    candidate = candidates[0]
    target = next(item for item in targets if item["field"] == "contract_price" and candidate in item["rows"])
    affected = set(target["rows"])
    baseline_price = int(Decimal(target["before"]) * 100)

    def amount(number, cents):
        quantity, price, contract = values[number]
        return quantity * max(price - (cents if number in affected else contract), 0)

    def strictly_first(cents):
        leading = amount(candidate, cents)
        return leading > 0 and all(number == candidate or leading > amount(number, cents) for number in values)

    def witness(cents):
        amounts = {number: amount(number, cents) for number in values}
        largest = max(amounts.values())
        leaders = [{"row": row["row"], "invoice_id": row["invoice_id"], "variance": price_text(largest)}
                   for row in rows if largest > 0 and amounts[row["row"]] == largest]
        status = "unique"
        if largest == 0:
            status = "no_positive"
        elif len(leaders) > 1:
            status = "tie"
        return {"price": price_text(cents), "candidate_variance": price_text(amounts[candidate]),
                "status": status, "leaders": leaders}

    # Each pairwise strict-leader region is an interval for one common price.
    # Their intersection contains the original price, so both searches are monotone.
    low, high = 0, baseline_price
    while low < high:
        middle = (low + high) // 2
        if strictly_first(middle):
            high = middle
        else:
            low = middle + 1
    first = low
    low, high = baseline_price, MAX_PRICE_CENTS
    while low < high:
        middle = (low + high + 1) // 2
        if strictly_first(middle):
            low = middle
        else:
            high = middle - 1
    last = low

    transitions = []
    for direction, boundary, strict, following in (
            ("decrease", first - 1, first, first - 2),
            ("increase", last + 1, last, last + 2)):
        if 0 <= boundary <= MAX_PRICE_CENTS:
            transitions.append({"direction": direction, "last_strict": witness(strict),
                                "at": witness(boundary),
                                "beyond": witness(following) if 0 <= following <= MAX_PRICE_CENTS else None})
    return {**result, "candidate_row": candidate, "target": target["id"], "label": target["label"],
            "affected_rows": target["rows"], "original_price": price_text(baseline_price),
            "strict_price_interval": {"low": price_text(first), "high": price_text(last)},
            "transitions": transitions}
