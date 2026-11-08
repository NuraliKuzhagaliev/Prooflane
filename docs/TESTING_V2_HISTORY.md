# Historical verification of the single-CSV/scenario versions

These counts belong to3 November revisions, not the current suite. Final historical scenario regression:83 Python tests on Windows and Linux,6 JS formatting tests,24/24 independent CSV checks via actual HTTP/Reference/Docker (16 receipts,zero model calls),36/36 baseline→scenario→export checks, and actual container caps/timeout/output/cleanup probes. Earlier53/4 and38-test stages remain historical.

The independent fixture corpus includes eight valid and four invalid CSVs in each mode. Expectations were manually authored rather than copied from production `summarize`. A negative evaluator control changed0.60 to0.59 in memory; the real HTTP check failed and returned exit1 without changing the canonical fixture. [Corpus](../examples/evaluation/README.md).

A large-amount browser defect rounded99999899990000.01 to the next cent through Number conversion. The formatter now groups the decimal string directly; the actual browser displayed99,999,899,990,000.01. A Windows MIME issue for.mjs was fixed by serving the browser module as.js and rerunning the workflow.

Actual browser checks included24 rows/6 findings/1480 variance/34353 billed, source-row inspection with Escape/focus return, five containment outcomes, malformed CSV and literal HTML-like text, changed decimal input0.60, download/CLI and narrow layouts. Legacy scenarios showed1480→1160 and1480→960 with original preserved. Saved packets independently checked full differences and rejected rehashed semantic forgeries.

Independent audits found cleanup failure did not block new work, invalid Unicode CSV/token handling, malformed provider choice and surrogate model/plan persistence issues. Fixes added persistent/startup quarantine, safe422 handling, credential comparisons and strict provider validation; original triggers were retested. A clean execution timeout permits one repair; uncertain cleanup does not.

The Windows restricted environment initially blocked ensurepip/network/asyncio socketpair. Project-local temporary directories, permitted dependency installation and an allowed local test run resolved those environment gates; failed attempts were not counted as passes. A Dockerfile permission failure was reproduced and corrected before actual runtime smoke passed.

A single local eight-case sample measured median HTTP-case19.59ms Reference and2019.69ms Docker; ranges16.38–24.74ms/1962.90–2495.05ms. It included receipt/ownership requests and was not a public load/cloud comparison. At the original date real VSI/VM/HTTPS, final video/GitHub submission, SIGKILL/OOM and user studies were NOT_RUN. Later evidence is in [current TESTING](../TESTING.md), not retroactively attributed here.

## Historical source preservation

This English page is an editorial summary/update prepared for the final publication, not a newly conducted independent review or a full literal translation. The [complete original at its prior revision](https://github.com/NuraliKuzhagaliev/Prooflane/blob/ff0b6b117fd7f16b819f25894e5aec07314389ad/docs/TESTING_V2_HISTORY.md) retains original wording, dates, hashes, detailed findings and limitations. Raw probe files were not translated or altered. Current release evidence belongs to [TESTING](../TESTING.md).

Preserved original source/evidence links:

- [windows-cycle1.txt](../artifacts/optimization/windows-cycle1.txt)
- [linux-final.txt](../artifacts/optimization/linux-final.txt)
- [linux-build.txt](../artifacts/optimization/linux-build.txt)
- [node-final.txt](../artifacts/optimization/node-final.txt)
- [evaluation.json](../artifacts/optimization/evaluation.json)
- [scenario-smoke.json](../artifacts/optimization/scenario-smoke.json)
- [sandbox-smoke.json](../artifacts/sandbox-smoke.json)
- [frontend-implementation.md](../artifacts/optimization-review/frontend-implementation.md)
- [engineering-cycle1.md](../artifacts/optimization-review/engineering-cycle1.md)
- [judge-cycle1.md](../artifacts/optimization-review/judge-cycle1.md)
- [engineering-cycle2.md](../artifacts/optimization-review/engineering-cycle2.md)
- [scenario-smoke.json](../artifacts/optimization/final/scenario-smoke.json)
- [ux-cycle1.md](../artifacts/optimization-review/ux-cycle1.md)
- [ux-cycle2.md](../artifacts/optimization-review/ux-cycle2.md)
- [judge-cycle2.md](../artifacts/optimization-review/judge-cycle2.md)
- [validation-summary.json](../artifacts/optimization/validation-summary.json)
- [sandbox-comparison.json](../artifacts/optimization/sandbox-comparison.json)
- [reference-comparison.json](../artifacts/optimization/reference-comparison.json)
- [evaluation-local.json](../artifacts/evaluation-local.json)
- [README.md](../examples/evaluation/README.md)
- [evaluation-negative-control.json](../artifacts/evaluation-negative-control.json)
- [large-amount-fixed.jpg](../artifacts/screenshots/large-amount-fixed.jpg)
- [offline-demo-ready.jpg](../artifacts/screenshots/offline-demo-ready.jpg)
- [linux-tests.txt](../artifacts/linux-tests.txt)
- [api-smoke.json](../artifacts/api-smoke.json)
- [dependency-audit.json](../artifacts/dependency-audit.json)
- [browser-receipt.json](../artifacts/browser-receipt.json)
- [desktop-review.jpg](../artifacts/screenshots/desktop-review.jpg)
- [mobile-review.jpg](../artifacts/screenshots/mobile-review.jpg)
- [source-record.jpg](../artifacts/screenshots/source-record.jpg)
- [REPORT.md](../artifacts/audit/REPORT.md)
- [reproduction-before.json](../artifacts/audit/reproduction-before.json)
- [reproduction.json](../artifacts/audit/reproduction.json)
