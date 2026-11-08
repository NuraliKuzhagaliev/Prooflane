# Reliability contracts and evidence — 8 November

Before this change, synchronous case/variant POSTs had no operation identity, so a lost response made safe recovery ambiguous. A global mutation lock also held across model/container latency. A local duplicate-key JSON probe accepted an ambiguous hash field because ordinary parsing kept the last key. A suspected Unicode-name defect was not reproduced and was not counted as a fix.

**F1:** durable owner-scoped request IDs store fingerprints/result references, not request bodies or tokens. Unchanged replay returns the same result; changed replay409; another owner404. A browser deadline covers response body reading and never automatically repeats the POST. Status-only recovery distinguishes unknown outcome; aborting a browser request does not cancel server work. Startup must restore pending identity before async readiness/history.

**F2:** owner/case locks replace an unnecessarily global mutation lock. Unrelated cases can progress, while same-case revision conflict remains. Global execution concurrency stays2. This is one-worker support, not distributed locking.

**F3:** API/CLI reject duplicate keys including nested conflicts. Browser syntax-checks JSON but sends the original text, not parse→stringify, which would erase duplicates. Ordinary packets still pass. This resolves ambiguous representation, not a claim to prevent every self-consistent forgery.

Independent cycle2 found the fingerprint also had to include supplied field names: an absent default and explicit default were semantically different to validation. It also found late pending-ID restoration. Both were corrected and retested at their actual levels. [Review](TRANSFORMATION_REVIEW_CYCLE2.md). Real240-second delayed browser testing, multiworker deployment, crash/OOM experiments and user studies remained NOT_RUN.

## Historical source preservation

This English page is an editorial summary/update prepared for the final publication, not a newly conducted independent review or a full literal translation. The [complete original at its prior revision](https://github.com/NuraliKuzhagaliev/Prooflane/blob/ff0b6b117fd7f16b819f25894e5aec07314389ad/docs/TRANSFORMATION_RELIABILITY_20261108.md) retains original wording, dates, hashes, detailed findings and limitations. Raw probe files were not translated or altered. Current release evidence belongs to [TESTING](../TESTING.md).

Preserved original source/evidence links:

- [reliability-pytest.txt](../artifacts/transformation-20261108/reliability-pytest.txt)
- [docs.stripe.com — idempotent_requests](https://docs.stripe.com/api/idempotent_requests)
- [www.sqlite.org — lang_transaction.html](https://www.sqlite.org/lang_transaction.html)
- [docs.python.org — json.html](https://docs.python.org/3.13/library/json.html#repeated-names-within-an-object)
