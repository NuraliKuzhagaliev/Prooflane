# Adversarial QA — source matching, case evidence, HTTP boundaries

Date: 2026-11-04 (local project date). Reviewer: independent QA subagent. Scope: owned synthetic fixtures and three new test files; application modules were changed by the root implementation agent, not this reviewer.

## Executed evidence

```powershell
.venv/Scripts/python.exe -m pytest tests/test_reconciliation.py tests/test_case_evidence.py tests/test_cases.py -q --tb=short
```

Final targeted run: **56 passed**, 1 dependency deprecation warning, in 1.59 seconds. This duration is a test-run observation, not an application performance benchmark. The warning concerns Starlette TestClient's httpx integration; it did not prevent route execution.

The first un-escalated TestClient invocation stalled with no test output under the environment's loopback restrictions. Only its two inspected pytest processes were stopped, and the targeted suite was re-run with local loopback permission. The API tests use the real FastAPI routes, reference arithmetic, and explicitly labeled runtime doubles. No real Docker or model integration is claimed by these tests.

An intermediate combined run produced 55 passes and one failure because an offline CLI subprocess loaded a newly strengthened case-context rule while the parent pytest process still had the previous module loaded. The synthetic baseline fixture was updated to carry the required `{kind: "baseline", case_id: "case-fixture"}` metadata. The final fresh run above passed all 56 tests.

## Independent scenario oracle

`examples/case-invoices.csv` contains eight synthetic invoices; `examples/case-contracts.csv` contains five synthetic contract versions. No supplier data or third-party dataset is represented.

- Source invoice record 5 has two date-eligible contract versions and requires an explicit `C2R` selection.
- Source invoice record 7 has no active supplied contract. It is excluded only with a stated reason, preserving coverage as seven reviewed invoices out of eight sources.
- Baseline billed amount: **7110.00 USD**. Positive variance: **768.00 USD**. Five positive findings; below-price records remain included in the review.
- Contract C1 binds normalized records **2, 3, 8**. Setting its price to 80 changes all three; total variance becomes **368.00 USD**, a **−400.00 USD** delta.
- Jointly setting C1 to 80 and first invoice quantity to 80 gives **568.00 USD**. Adding separate one-variable effects would incorrectly yield 888.00 USD; the API test checks the joint result.
- Declaring C1 price in [65,85] gives total variance **[148.00,1193.00] USD**, width **1045.00 USD**. Learning that single uncertain value exactly eliminates the declared width.

## Attacks and failure paths exercised

Source tests reject invalid calendar dates, inverted contract validity, duplicate contract IDs, unsupported decimal precision, invalid quantities, wrong headers, null bytes, invalid or conflicting selection/exclusion structures, excessive source sizes, over 500 records, and more than 5,000 eligible links. Dates are inclusive; vendor/item matches are case-sensitive after trimming; multiline CSV notes preserve record-number references. An all-excluded review does not become an empty verified baseline.

Evidence tests rebuild hashes around forged derived ranges, evidence priorities, deltas, coverage, source decisions, source prices, parent identity, execution mode, changed-row claims, and duplicate names/run identities. A partially propagated shared-contract edit is arithmetically valid as a standalone receipt but fails complete case verification. This is a meaningful negative control beyond detecting stale hashes. Malformed metadata is rejected before it can be returned to the browser.

The actual offline CLI accepts a complete consistent synthetic case and exits nonzero for a recomputed-root-hash forgery. Its fixture includes receipt code that would raise an exception if executed; verification succeeds because checking artifacts does not execute receipt code. This also demonstrates the important limit: a valid code hash is not execution attestation.

HTTP tests cover session ownership for cases, mutation, baseline reuse and downloads; immutable original baselines; rejection of alternative chaining through both new and legacy endpoints; stale revisions; failure preservation; four-alternative limits; no-op and duplicate-target rejection; secret redaction; legacy case import; 24-hour source expiry; same-origin markers; scoped 2 MiB/8 MiB request limits; malformed/deep/non-finite packet JSON; successful matching of two valid sources whose combined body exceeds the old 180 KB limit; and concurrent variant/bounds serialization without a second execution.

Browser verification is tested through its HTTP endpoint: it returns success/failure without importing a case or creating runs in the verifying session. This is an API assertion, not a visual browser interaction test.

## Findings and boundaries

Inspection identified that `selections or {}` / `exclusions or {}` would silently treat invalid empty list/string/false values as an empty decision map. Root corrected this before the first final pure-module run; the regression cases now pass. Metadata validation was strengthened concurrently and is covered by the new tests. A separate science review found and root corrected the baseline-to-case identity issue; this reviewer adapted its valid fixture to the stronger contract.

No unresolved failing test remains in this owned suite. This result does not establish cloud readiness, model quality, production-scale concurrency, source authenticity, financial recovery, visual usability or accessibility. The supported server design remains one application worker; multi-process mutation coordination would require separate validation. Actual Docker, browser desktop/mobile flows, full regression and second-cycle review belong to the broader release evidence.
