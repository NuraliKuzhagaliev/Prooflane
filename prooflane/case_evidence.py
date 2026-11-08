"""Portable case verification reconstructs sources and assumptions; never executes code."""
from .analysis import canonical, digest, parse_csv
from .intelligence import apply_changes, comparison_delta, explore, targets_for
from .receipts import check_receipt
from .priority import priority_switch
from .reconciliation import source_result

MAX_PACKET_BYTES = 8 * 1024 * 1024


def derive_case(sources, baseline, alternatives, bounds, case_id):
    original = source_result(sources)
    check_receipt(baseline)
    if original["canonical_csv"] != baseline["input_csv"]:
        raise ValueError("Baseline input does not match reconstructed source reconciliation.")
    if baseline.get("lineage") or baseline.get("case_context", {}).get("kind") == "alternative":
        raise ValueError("Case baseline must be an original review.")
    if sources["kind"] == "contracts" and baseline.get("case_context") != {"kind": "baseline", "case_id": case_id}:
        raise ValueError("Reconciled baseline must declare this case as its source context.")
    mode = baseline["provenance"]["mode"]
    if mode not in {"reference", "sandbox", "vultr"}:
        raise ValueError("Unsupported baseline execution mode.")
    targets = targets_for(original["canonical_csv"], original["bindings"])
    if not isinstance(alternatives, list) or len(alternatives) > 4:
        raise ValueError("A case supports at most four alternatives.")
    names, ids, comparisons = set(), {baseline["run_id"]}, []
    for alternative in alternatives:
        if not isinstance(alternative, dict) or set(alternative) != {"name", "changes", "changed_rows", "receipt"}:
            raise ValueError("Invalid alternative structure.")
        name = alternative["name"]
        if not isinstance(name, str) or not name.strip() or len(name) > 80 or name in names:
            raise ValueError("Alternative names must be distinct and at most 80 characters.")
        name.encode("utf-8")
        names.add(name)
        receipt = alternative["receipt"]
        check_receipt(receipt)
        if receipt["run_id"] in ids or receipt["provenance"]["mode"] != mode:
            raise ValueError("Alternatives need distinct run IDs and the original execution mode.")
        ids.add(receipt["run_id"])
        candidate, changes, changed_rows = apply_changes(original["canonical_csv"], targets, alternative["changes"])
        if canonical(parse_csv(candidate)) != canonical(parse_csv(receipt["input_csv"])):
            raise ValueError("Alternative contains an undeclared source change or incorrect shared propagation.")
        if alternative["changed_rows"] != changed_rows:
            raise ValueError("Declared changed records do not match the source propagation.")
        expected_context = {"kind": "alternative", "case_id": case_id, "baseline_run_id": baseline["run_id"],
                            "baseline_receipt_sha256": baseline["receipt_sha256"], "changes": changes}
        if canonical(receipt.get("case_context")) != canonical(expected_context):
            raise ValueError("Alternative parent identity or assumptions do not match.")
        comparisons.append({"name": name, "run_id": receipt["run_id"], "changed_rows": changed_rows,
                            "delta": comparison_delta(baseline["summary"], receipt["summary"]),
                            "total_variance": receipt["summary"]["total_variance"], "total_billed": receipt["summary"]["total_billed"]})
    return {"source": {k: v for k, v in original.items() if k != "canonical_csv"},
            "intelligence": explore(original["canonical_csv"], targets, bounds), "comparisons": comparisons}


def make_case_packet(case, baseline, alternatives):
    derived = derive_case(case["sources"], baseline, alternatives, case["bounds"], case["id"])
    body = {"schema": "prooflane.case.v1", "case_id": case["id"], "name": case["name"], "created_at": case["created_at"],
            "sources": case["sources"], "baseline": baseline, "alternatives": alternatives, "bounds": case["bounds"],
            **derived}
    targets = targets_for(baseline["input_csv"], derived["source"]["bindings"])
    body["priority_switch"] = priority_switch(baseline["input_csv"], targets)
    packet = {**body, "case_sha256": digest(canonical(body))}
    if len(canonical(packet).encode("utf-8")) > MAX_PACKET_BYTES:
        raise ValueError("Case packet exceeds 8 MiB. Download individual receipts instead.")
    return packet


def check_case_packet(packet):
    fields = {"schema", "case_id", "name", "created_at", "sources", "baseline", "alternatives", "bounds",
              "source", "intelligence", "comparisons", "case_sha256"}
    if not isinstance(packet, dict) or set(packet) not in (fields, fields | {"priority_switch"}) or packet["schema"] != "prooflane.case.v1":
        raise ValueError("Invalid case packet structure.")
    body = {k: v for k, v in packet.items() if k != "case_sha256"}
    if digest(canonical(body)) != packet["case_sha256"]:
        raise ValueError("Case packet hash mismatch.")
    for key, limit in (("case_id", 64), ("name", 80), ("created_at", 64)):
        value = packet[key]
        if not isinstance(value, str) or not value.strip() or len(value) > limit:
            raise ValueError("Invalid case metadata.")
        value.encode("utf-8")
    derived = derive_case(packet["sources"], packet["baseline"], packet["alternatives"], packet["bounds"], packet["case_id"])
    for key, value in derived.items():
        if canonical(value) != canonical(packet[key]):
            raise ValueError(f"Reconstructed {key} does not match the packet.")
    if "priority_switch" in packet:
        targets = targets_for(packet["baseline"]["input_csv"], derived["source"]["bindings"])
        expected = priority_switch(packet["baseline"]["input_csv"], targets)
        if canonical(expected) != canonical(packet["priority_switch"]):
            raise ValueError("Reconstructed priority switch does not match the packet.")
    return {"passed": True, "case_name": packet["name"], "case_id": packet["case_id"],
            "checks": ["Source reconciliation and explicit exclusions", "Baseline receipt and source CSV", "All alternative arithmetic and parent links",
                       "Declared changes and shared-contract propagation", "Exact ranges, sensitivity and review priorities", "Case hash and all comparisons"] +
                      (["Priority boundaries and cent-grid witnesses"] if "priority_switch" in packet else []),
            "counts": packet["source"]["counts"], "alternatives": len(packet["alternatives"]),
            "range": {k: packet["intelligence"][k] for k in ("low", "high", "width")},
            "scope": "Source/assumption consistency and arithmetic only. No issuer authentication, runtime attestation or proof that supplied contracts are true."}
