# Case workbench implementation

Implemented in this worker's owned UI files on 2026-11-04. This records actual evidence and remaining browser work; it is not a claim of completed end-to-end acceptance.

## Delivered behavior

- New primary blue/slate case shell, compact case header, recent-case rail, Sources / Overview / Explore / Evidence views, retained baseline identity and packet action.
- Two-source CSV import/paste and actual fictional sample endpoint. Exact source reconciliation displays overlaps, candidates, explicit selections and reasoned exclusions. Creation stays disabled until reconciliation is ready; changing files invalidates the report and decisions.
- Read-only saved source decisions, coverage totals, included-row search/filter, exact source/contract/normalized-record inspector and baseline figures from the API.
- Up to four named alternatives with up to twelve explicit targets, shared-contract affected-row labels, joint server recomputation, immutable baseline/alternative matrix, signed exact-decimal displays and duplicate-as-draft.
- Server-supplied declared range analysis, SVG one-at-a-time endpoint plot, keyboard target selection, accessible numeric data table, next-evidence queue, exact joint bounds, robust-priority statement and contract break-even thresholds.
- Interactive source → contract → normalized input → baseline → alternative → receipt dependency path, actual execution/check/code details, case packet download and read-only packet verification.
- Existing single CSV workflow, history, source dialog, one-cell scenarios, receipts and containment are preserved behind “Single CSV review”. Original single CSV runs can be promoted to a case. Case alternatives cannot enter the legacy one-cell scenario flow.
- Reference statuses read “Reference complete”; independent output verification is reserved for sandbox executions. Range analysis is explicitly a trusted estimate, not an executed alternative.
- Responsive rules and reduced-motion support are implemented. Their actual narrow-screen/1440px rendering remains for the independent browser reviewer.

Files: `web/index.html`, `web/app.js`, `web/scenario.js`, new `web/workbench.js`, `web/workbench-model.js`, `web/workbench.css`, new `tests/test_workbench.mjs`. Existing monetary formatting is reused; numeric conversion is limited to chart geometry.

## Checks executed

- `node --check web/workbench.js`: PASS.
- `node --check web/workbench-model.js`: PASS.
- `node --check web/app.js`: PASS.
- `node --check web/scenario.js`: PASS.
- `node --test tests/test_format.mjs tests/test_workbench.mjs`: PASS, 12 tests, 0 failures. Covers exact cents, reference provenance, numeric no-ops, duplicate/capacity/numeric limits, required range containment, source filters and explicit candidate selection.
- Python read-only DOM-ID inspection: 237 IDs, no duplicate IDs, no missing statically referenced IDs (excluding the dynamically created exclusion textarea).

Independent engineer source probes identified four async/contract issues during integration. All were fixed: HTTP-200 `failed_run` keeps the draft and displays failure events; string packet checks inherit the actual verifier pass result; case identity and source rows commit only after the source request succeeds; packet results are bound to the captured packet revision and file/paste inputs are disabled while verification runs. The independent engineer owns the reproduction evidence and final rerun.

## Actual browser evidence

Used a newly created isolated Chrome task session at `http://127.0.0.1:8765/`; the user's existing IAB tab was not selected or changed.

1. Loaded the fictional sample through the real UI/API. Observed 8 source rows, 6 exact matches, 2 unresolved rows, 0 exclusions.
2. Inspected invoice `INV504`, source row 5, with candidates C2 at $108 and C2R at $110 and their actual contract intervals.
3. Selected C2R using “Use this contract row”. Observed 1 explicit selection and 1 remaining unresolved row.
4. Inspected unmatched `INV506`, source row 7. Entered “Outside this review; no supplied contract available.” and recorded its exclusion.
5. Created the real reference baseline using “Create baseline · 7 rows”. Case ID: `c465a0e5-3815-44ba-8131-c1ae6d95fc06`; baseline run ID begins `c6220daa-dcc`.
6. Observed the Overview with “Reference complete”, positive variance $768.00, 5 flagged rows, coverage 7/8, 1 exclusion, billed total $7,110.00. The selected INV501 inspector showed original quantity 40, billed unit price $85, C1 contract price $72, and row variance $520. These are real server outputs, not UI fixtures.
7. Browser console error inspection returned an empty list at the initial page.

Last actual browser journey preceded the final error-path and revision-binding fixes; those later changes received syntax/source checks, not another browser journey in this worker.

## Browser stop and honest limitations

Both documented browser screenshot attempts failed with:

> Timed out after 5000ms waiting for CDP command Page.captureScreenshot.

A documented viewport override requested 1440×900, but subsequent read-only DOM inspection reported `innerWidth: 1920`, `innerHeight: 1200`, and document scroll width 1900. Therefore this worker does **not** claim a successful 1440×900 layout check.

After reading the documented browser troubleshooting/screenshot guidance, this worker attempted the native screenshot fallback for the returned Chrome window. The CUA safety layer stopped that tool turn with this exact message:

> Computer Use has been stopped for this turn because it could not determine the current browser URL on Windows with enough confidence to enforce policy. Stop your work and send a final message noting why Computer Use ended.

No further computer actions were issued after that safety stop. This was a browser-policy enforcement stop, not an app defect and not permission to bypass that control. Root was notified and assigned an independent reviewer to continue using a verified local browser target. No screenshots were captured by this worker, and no existing user tab was repurposed.

Remaining browser acceptance for the independent reviewer: source file upload/paste variants; exact 1440×900 and mobile screenshots; saved-case reopen; three named alternatives including shared-contract and joint changes; invalid/stale draft behavior; range plot keyboard/numeric interaction; case packet download, valid verification and tamper rejection; legacy review/scenario/receipt/containment accessibility; reduced-motion inspection. Runtime integrations remain governed by the root's separate real execution evidence.
