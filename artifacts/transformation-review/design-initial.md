# Initial product-design audit

Date: 2026-11-03. Repository: `D:/projects/vultre`, observed revision `82f1ec3`. The only working-tree changes made by this reviewer are this report, the workspace design brief, and browser screenshots. No application code was changed. Review method follows `hub-audit` and its `references/review.md`; critical flow was exercised in the real application through an isolated Chrome tab at `http://127.0.0.1:8765/`.

## Verdict

The existing reference calculation, one-cell scenario and verifiable comparison packet are functional. The current presentation is a tidy demo page, not yet a professional investigation workspace. Its strongest differentiator—linked source, calculation, alternative and receipt evidence—is buried in a long vertical sequence. The requested transformation requires a case model and workflow architecture, not another cosmetic pass.

Select the **case workbench** described in `docs/WORKSPACE_DESIGN.md`: source-matching queue, compact case overview, sensitivity tool, named alternatives matrix, contextual evidence inspector and a verified case packet. Preserve immutable baselines and legacy one-cell lineage rules. The subsequently agreed new-case contract adds explicitly declared multi-target alternatives and shared-contract propagation; it must verify all affected rows without changing the legacy contract.

## Evidence collected

| ID | Observation / artifact |
|---|---|
| E1 | `before-initial.jpg`: real initial UI after service readiness; desktop viewport measured through read-only DOM at 1762 × 1175 CSS px. Initial run button begins at y=1325.7, below the viewport. Empty-state panel is 650 px high |
| E2 | Actual browser actions: `Use synthetic sample` → `Run invoice review` in Reference mode. Baseline `dcd86fcf-d014-4090-aa0a-2534077e5bf3`; 24 rows, 6 flagged, USD 34,353 billed, USD 1,480 positive variance |
| E3 | `before-source-detail.jpg`: clicked INV-2402, source row 3. Dialog shows Atlas Industrial, quantity 40, billed 85.00, contract 72.00 and variance 520.00. Source is an embedded contract price, not a separate contract match |
| E4 | Actual browser actions: `Test an assumption on this row` → contract price `80` → `Run comparison`. Scenario `1565f218-075a-4cc7-8ab5-746a76d5faa4`; total variance 1,160.00, signed change −320.00, 23 unchanged records, same Reference mode |
| E5 | `before-comparison.jpg`: real completed comparison, separate receipt links, `Return to original baseline`, and repeated `hypothetical-scenario.csv` entries in history |
| E6 | Actual browser download: `Download comparison packet` saved `C:/Users/nural/Downloads/prooflane-comparison-1565f218-075a-4cc7-8ab5-746a76d5faa4.json` |
| E7 | `.venv/Scripts/python.exe scripts/verify_receipt.py 'C:/Users/nural/Downloads/prooflane-comparison-1565f218-075a-4cc7-8ab5-746a76d5faa4.json'` exited 0 with `passed: true`: both receipt hashes/arithmetic, baseline identity/hash, exactly one declared assumption, same execution mode and every signed delta |
| E8 | Source inspection: `web/index.html`, `web/styles.css`, `web/app.js`, `web/scenario.js`, `prooflane/app.py`, `prooflane/analysis.py`, `prooflane/comparison.py`, `prooflane/store.py`. Current CSV parser requires the exact six-column schema; no case, separate source matching, multi-alternative collection or sensitivity endpoint exists in the inspected baseline |

Browser work was limited to local synthetic data and Reference mode. The isolated review tab was closed after capture. User-existing tabs were not navigated or closed.

## Findings

### D-01 — Important work is displaced below introductory material

- Severity: medium. Dimension: UX / task efficiency. Status: open. Confidence: high.
- Location: `web/index.html` page-heading, setup panel and empty-state; `web/styles.css` layout and empty-state sizing.
- Trigger: open the application at the observed desktop viewport.
- Consequence: the primary run action is below a 1175 px-tall viewport; an experienced user must traverse marketing-style copy and a large empty illustration before finishing a small input task. After execution, the persistent upload column continues to constrain result width.
- Evidence: E1, E5, E8.
- Reproduction: open `/`, return to top, inspect the run button and empty-state bounds. No zoom or viewport override was applied by this reviewer.
- Recommendation: compact case header; import surface becomes source chips after baseline creation; analytical canvas gets the primary width.
- Acceptance: at 1440 × 900, the loaded case shows identity, mode, source coverage, next action and actionable findings without scrolling past a hero.

### D-02 — No source-matching model or unresolved-work surface

- Severity: medium relative to the requested product scope. Dimension: workflow completeness. Status: open. Confidence: high.
- Location: current upload form and exact six-column parser.
- Trigger: attempt to review invoices against a separate contract-price source.
- Consequence: users can supply an embedded `contract_price`, but cannot inspect which independent contract row supplied it, see ambiguous candidates or resolve missing matches. The UI cannot substantiate a separate matching claim.
- Evidence: E1, E3, E8. This is a missing requested capability, not a failure of the existing embedded-price calculation contract.
- Recommendation: add deterministic import/match preview and a source manifest, with Exact / Unmatched / Ambiguous / Manually selected / Embedded states. Do not fill or silently exclude unresolved rows.
- Acceptance: a real two-file synthetic case includes ambiguous and unmatched examples, exposes candidate source rows, blocks completion until resolution and binds the result to the packet.

### D-03 — Alternatives are separate runs without a comparison workspace

- Severity: medium relative to the requested scope. Dimension: information architecture. Status: open. Confidence: high.
- Location: `web/scenario.js`, history list and comparison-result region.
- Trigger: complete a scenario and try to investigate several alternatives.
- Consequence: the user must return to the original and infer relationships among repeated `hypothetical-scenario.csv` history entries. There is no named collection, multi-alternative matrix or common-scale sensitivity view. The verified pairwise delta is useful but difficult to compare across experiments.
- Evidence: E4, E5, E8.
- Recommendation: named alternatives grouped under one immutable baseline; distinguish draft preview, running, completed and failed. Add a matrix and sensitivity plot with exact numeric access.
- Acceptance: three to six alternatives remain simultaneously legible and inspectable; every completed one links to the same baseline and original mode; failed/draft rows cannot appear verified.

### D-04 — Reference completion receives the generic verified label

- Severity: low. Dimension: trust communication. Status: open. Confidence: high.
- Location: `web/app.js` `renderRun` (generic `Result verified` and live announcement), explanation label; scenario completion copy.
- Trigger: run Reference calculation.
- Consequence: the most prominent completion label uses the same broad wording as independent execution verification. The nearby provenance banner and lower check label correctly clarify that no model or sandbox was used, so this is an ambiguity, not an observed false model-execution claim.
- Evidence: E2, E4, E8.
- Recommendation: mode-specific state labels: `Reference complete`; `Sandbox result independently verified`; `Agent result independently verified`, contingent on actual returned checks. Keep mode in the persistent case header.
- Acceptance: Reference mode never visually implies independently executed generated code; successful container/model runs do not lose their actual evidence.

### D-05 — Source inspection interrupts the analytical context

- Severity: low. Dimension: UX / comparison efficiency. Status: open. Confidence: high.
- Location: `finding-dialog` and `showFinding`.
- Trigger: inspect a finding from the table.
- Consequence: a large modal dims the table and the other findings. It explains one row clearly, but makes scanning several evidence chains or comparing a contract candidate slower.
- Evidence: E3.
- Recommendation: desktop inspector beside the table, with selected-row state; use modal/full-width sheet only at narrow sizes.
- Acceptance: users inspect successive rows without losing filters, baseline context or table position, and keyboard focus returns predictably on close.

## What worked and must survive

- Source-row numbers, exact arithmetic and the limitation of supplied prices are shown in the detail view.
- Scenario entry can start from a finding, carries the row forward, states the original values and retains the baseline's execution mode.
- Completed scenario clearly displays original and hypothetical totals, signed delta and unchanged-record count.
- Baseline and scenario receipts are separate, and the actual downloaded comparison packet passed the offline verifier.
- Reference provenance is candid in the banner. Vultr mode was disabled as unconfigured, not simulated.

These successes are evidence for the tested reference flow only. They do not prove cloud, model or containment integration.

## Design research used

Primary references consulted on 2026-11-03: [SAP Fiori layouts](https://www.sap.com/design-system/fiori-design-web/v1-136/page-types/floorplan-overview), [Carbon data-table guidelines](https://www.carbondesignsystem.com/building-blocks/core/components/data-table/guidelines), and [Linear Triage](https://linear.app/docs/triage). They support list/detail context, broad data tables and explicit unresolved-work queues. The selected design is an inference for this product, not a measured user-study result. No copied assets or new libraries.

## Checks not run / limits

No live Vultr calls, charged resources, publishing, model inference, sandbox execution or containment probe was performed by this reviewer. Existing history entries in other modes were observed but are not new execution evidence. No malformed-file upload, mobile viewport, screen-reader session, contrast measurement, keyboard-only end-to-end test or reduced-motion emulation was performed in this initial review. Source contains responsive and reduced-motion rules, but their presence is not browser verification. No claim of accessibility conformance, security certification or complete error-path coverage is made.

The subsequent implementation review should reproduce the matched-source case, at least three alternatives within the agreed four-alternative limit, shared-contract and joint changes, interval intelligence and case-packet verification in the real browser, then test keyboard, narrow-screen, stale-input and failure behavior. The product should not be called transformed based on screenshots alone.
