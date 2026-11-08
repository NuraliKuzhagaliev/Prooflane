"""Unambiguous JSON parsing for portable evidence, without executing its code."""
import json


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            # Do not echo a possibly sensitive source key into error messages.
            raise ValueError("Duplicate JSON object keys are not allowed in evidence packets.")
        result[key] = value
    return result


def load_evidence_json(text):
    return json.loads(text, object_pairs_hook=_unique_object,
                      parse_constant=lambda _: (_ for _ in ()).throw(ValueError("Non-finite JSON number")))
