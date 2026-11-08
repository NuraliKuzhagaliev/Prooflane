from .analysis import canonical, digest, parse_csv, summarize, verify_output


def make_receipt(payload):
    hashes = {"input_sha256": digest(payload["input_csv"]), "code_sha256": digest(payload["code"]),
              "output_sha256": digest(canonical(payload["output"]))}
    body = {"schema": "prooflane.receipt.v1", **payload, "hashes": hashes}
    return {**body, "receipt_sha256": digest(canonical(body))}


def check_receipt(receipt):
    body = {k: v for k, v in receipt.items() if k != "receipt_sha256"}
    if receipt.get("schema") != "prooflane.receipt.v1":
        raise ValueError("Unsupported receipt schema")
    if digest(canonical(body)) != receipt.get("receipt_sha256"):
        raise ValueError("Receipt hash mismatch")
    for key, value in {"input_sha256": receipt["input_csv"], "code_sha256": receipt["code"],
                       "output_sha256": canonical(receipt["output"])}.items():
        if digest(value) != receipt["hashes"].get(key):
            raise ValueError(key + " mismatch")
    expected = summarize(parse_csv(receipt["input_csv"]))
    verification = verify_output(receipt["output"], expected)
    if not verification["passed"] or canonical(receipt["summary"]) != canonical(expected):
        raise ValueError("Independent arithmetic verification failed")
    return {"passed": True, "checks": verification["checks"],
            "scope": "Artifact integrity and fixed price-variance arithmetic; no authentication of the issuer or runtime."}
