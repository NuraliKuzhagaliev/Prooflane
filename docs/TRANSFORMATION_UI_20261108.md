# Prooflane UI decisions — 8 November 2026

This document records the frontend worker's decisions and source/tests. Browser observations belong to the independent reviewer and root evidence, not to this source review. No interviews, screen-reader listening or physical-touch tests were conducted by this worker.

## Research and art direction

The existing product already had a deliberate folio identity: pale blue paper, dark ink, teal emphasis, serif document headings and monospaced evidence references. Replacing its palette again would not resolve the remaining interaction problems. Three compositional directions were considered:

| Direction | Composition and navigation | Information model and interaction | Tradeoff |
|---|---|---|---|
| Ledger folio | Existing register beside a source annotation | Row selection, then inspection | Calm but leaves unresolved work buried in a filtered table |
| Exception desk — selected | A spatial source-decision queue, comparative alternative summaries, three grouped proof stages | Show the unfinished decision first; keep the original register and explicit source inspection | Adds focused hierarchy while preserving the actual review workflow |
| Verification tunnel | Full-width sequential source, calculation and receipt steps | Reveal one stage at a time | Suitable for reading proof, but slows comparison and returning to source decisions |

Selected direction uses the actual invoice-review work rather than a generic dashboard. Native controls, tables and details remain. No new animation is introduced: changes are explained through visible selection, progress, status and focus.

### Sources that affected the implementation

- [Carbon data table guidelines](https://www.carbondesignsystem.com/building-blocks/core/components/data-table/guidelines): retain the register and its search/filter tools for lookup; use a different display where comparative reading has different needs. This informed keeping the desktop table and replacing sideways scrolling with labeled alternative summaries on narrow screens. No Carbon code was copied.
- [W3C Error Identification](https://www.w3.org/WAI/WCAG22/Understanding/error-identification): retain the server's error description and identify a repair path in text. This informed the source-repair region and explicit edit actions, rather than silently discarding files.
- [GOV.UK error summary](https://design-system.service.gov.uk/components/error-summary/): make the error actionable and move focus to the repair context. This informed the import error heading and buttons opening the relevant CSV editor. The application is not asserted to conform to the GOV.UK component specification.
- [W3C disclosure pattern](https://www.w3.org/WAI/ARIA/apg/patterns/disclosure/): native expandable guidance avoids inventing a custom interaction. This informed a closed field-guide `details` element and retained source editors.
- [W3C keyboard interface guidance](https://www.w3.org/WAI/ARIA/apg/practices/keyboard-interface/): align pointer selection with predictable keyboard focus. This informed navigation from queue items and proof nodes into their current inspector, plus returning to source-search after clearing a contract filter.

Sources accessed 8 November 2026. They provide design/accessibility guidance, not evidence of improved task completion for Prooflane. No source supplies market-uniqueness claims.

### System specification

- Colors preserved: paper `#eff4f5`, white `#fbfdfe`, ink `#172d36`, muted `#4b6069`, rule `#beced2`, teal `#176365`; amber marks unresolved source decisions and unreviewed signals, not fraud.
- Typography: existing Newsreader document headings; existing sans body; IBM Plex Mono for short field/evidence labels. New queue invoice references use serif 24px; section headings 25–32px; explanatory text 12–14px with 1.6–1.7 line height.
- Layout: ruled sections rather than repeated rounded cards. Source queue splits context from unfinished decisions; Proof uses three stages containing two selectable nodes each; mobile alternatives become independently readable summaries.
- Responsive: queue and first-use context stack below900px; field guide, contract groups and alternative summaries become single-column below700px. New controls retain at least44px interaction height through the existing coarse-pointer rules.
- Motion: no new keyframes, timers for visual animation or shared-layout effects. Existing reduced-motion/forced-color rules still apply. Blob-download revocation uses a cleanup timer only.

## Candidate decisions and acceptance criteria

Scores are internal prioritization on a1–5 user-benefit/contest-fit scale, not measured outcomes. Complexity/risk are relative to this repository. Each selected item belongs to one direction only; product and innovation bindings are not counted again here.

### C — Visual design and interaction

| Candidate | Benefit / fit | Complexity / risk | Decision and testability |
|---|---|---|---|
| C1 Spatial unresolved-source queue | 5 / 4 | Medium / low | Implemented. Every pending item opens its original source row. Progress counts accounted-for rows and separately states exclusions. It must never imply an excluded row was calculated. |
| C2 Responsive named-alternative summaries | 4 / 4 | Medium / low | Implemented. At narrow widths, each original/alternative exposes variance, delta, flagged rows and execution state without requiring horizontal table scrolling; its Inspect action opens the same evidence. Desktop table retained. |
| C3 Grouped Proof reading map | 4 / 5 | Medium / low | Implemented. Six existing proof nodes are grouped into supplied sources, reproducible calculation and portable evidence. Selection/focus and current detail must agree; a scope note separates consistency checks from source authentication. |
| Density toggle | 2 / 2 | Medium / medium | Deferred. Adds a control before evidence of a density problem; narrow comparisons have a more direct solution. |
| Timeline/shared-layout animation | 2 / 3 | Medium / medium | Deferred. No measured comprehension benefit; source inspection should remain immediate and reduced-motion safe. |
| Another palette/font replacement | 1 / 2 | Medium / medium | Rejected. Existing natural teal/ink system already has contrast work; changing colors would not solve navigation defects. |

### D — Comprehension and usability

| Candidate | Benefit / fit | Complexity / risk | Decision and testability |
|---|---|---|---|
| D1 Explicit reviewed fictional example | 5 / 5 | Medium / medium | Implemented. A new user can reach the genuine Reference baseline from one click. Selection of C2R and exclusion of INV506 are recorded and explained, never presented as an autonomous AI decision. The original manual fictional workflow remains. |
| D2 Import field guide, starter files and corrective context | 4 / 4 | Medium / low | Implemented. Exact schema/format rules, downloadable fictional starter CSVs, preserved source text, and buttons to open each CSV editor. Malformed input must remain rejected and repairable. |
| D3 Resume a saved review after refresh | 4 / 4 | Medium / medium | Implemented. Only case ID, chapter and assumption pane are stored in sessionStorage. Reload reopens through the session-owned API. Expired/foreign IDs fail normally; denial/malformed storage does not prevent using the app. No CSV/token/draft body persistence. |
| Modal product tour | 2 / 2 | Medium / medium | Deferred. Forces reading before the real result; the reviewed example and visible next action are more direct. |
| New keyboard shortcuts | 2 / 3 | Medium / medium | Deferred. Existing native navigation remains; introducing nonstandard commands adds discoverability/conflict risk. |
| Free-form AI assistant | 2 / 3 | High / high | Rejected for this slice. No validated scenario contract or evidence that chat improves source decisions; it adds cost and unsupported claims. |

## Other owners' capabilities bound into the UI

These are deliberately **not counted** as C/D improvements:

- Product A1/A2: download source-linked review CSV and a human-readable Markdown brief next to the portable JSON packet.
- Product A3: contract-group original totals with exact bound-row filtering, including zero-variance records, a visible group filter and reset. Labels say invoice rows because IDs can repeat.
- Innovation E1: conditional per-invoice variance for each eligible contract candidate, before choosing; it does not establish validity or change other rows.
- Innovation E2: exact-field duplicate source warnings with original-row navigation; no automatic exclusion or claim of duplicate payment.
- Innovation E3: included/excluded/unresolved billed coverage displayed separately, with no inferred variance outside scope.
- Reliability F1: request UUID on baseline/alternative execution; persistent ID-only pending metadata; status-only recovery without a second computation. While an outcome is unknown new execution is blocked until checked. Metadata is hydrated before asynchronous history/session setup, and the operation-start helper refuses replacement. Requests have AbortController deadlines (240s execution,60s verifier,20s others), with timer cleanup and no automatic POST retry. The waiting state shows actual elapsed time without inventing completed stages. No request body or secret is stored.
- Reliability F3: packet verifier sends original JSON text. Parsing and reserializing would hide duplicate keys from the strict server parser; the browser keeps a syntax precheck but preserves those keys in the request body.

## Worker verification and review fixes

- `node --check web/workbench.js`: PASS.
- `node --test tests/test_*.mjs`: **25 PASS**. New tests cover denied/malformed browser storage, private-field omission, navigation ID validation, preserving duplicate JSON keys, controlled stalled-request abort without POST retry, timeout cleanup on server errors, and synchronous hydration/operation-start guards while readiness remains unresolved. Existing focus/decimal tests remain. A first run of the new raw-body test failed because its test DOM mock omitted `append`; corrected the mock and reran the suite.
- Static check:281 unique IDs; all literal JS element IDs resolved. This is not a browser or screen-reader test.
- Independent cycle1 reviewer reproduced two defects: group aggregate action selected only its first invoice without a group view; register count still described the whole case after filtering. Fixed both: actual normalized-row filtering plus reset; the register now reports visible flagged/shown counts. Singular row grammar corrected.
- Browser sizes, screenshots, genuine HTTP flows and second independent review are recorded by root/reviewers separately. Do not treat this worker's source/test assertions as substitutes for those observations.

Known limits: reference example tests fixed rules, not a live AI call; resume depends on the same browser-session cookie and24h retention; users must download packets for durable portability; no physical-touch or screen-reader listening result is claimed here; product usefulness still needs observation with real reviewers.
