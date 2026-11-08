# Prooflane case workbench

> Historical v3 proposal. The visual prescriptions below (permanent rail, card layout, sans-only identity) were superseded on 2026-11-05 by the user's Design Studio brief and [Audit Folio direction](design-studio/REFERENCES_AND_CONCEPTS.md). Retain source, receipt and state invariants; the old page composition is not a continuing constraint.

Design decision and implementation brief, 2026-11-03. This document specifies the next interface; it does not claim these features are implemented. Baseline observations are recorded in `artifacts/transformation-review/design-initial.md`. The agreed API and limits in `docs/WORKBENCH_CONTRACT.md` take precedence over illustrative layouts and module recommendations below.

## Product direction

Prooflane should feel like a compact analytical instrument for investigating a financial discrepancy. The organizing object is a **review case**: source invoices, their contract matches, a frozen baseline, named alternative assumptions, and the evidence needed to inspect the result later.

The central question is: **Which supplied rows explain this variance, how sensitive is it to a stated assumption, and what evidence travels with the conclusion?**

The current product can execute a trustworthy small calculation, but its interface is still a long introductory page. A large headline, a permanent upload form, and a decorative empty state compete with the work. Adding more cards beneath them would compound the problem. Replace that layout with a workbench whose controls follow the case lifecycle.

### Preserve these invariants

- Baselines remain immutable. Source changes create a new baseline; alternative assumptions create separate runs linked to the original baseline hash.
- Existing single-CSV scenarios preserve their one-cell contract. New case alternatives may change up to 12 distinct targets; a shared contract target changes every bound invoice row. Every alternative uses the original baseline and execution mode. No chaining or quiet mode fallback; joint effects must be recalculated rather than summed from isolated changes.
- Reference calculation, fixed sandbox recipe, and model-generated sandbox execution remain visibly distinct.
- Unverified output never enters comparison charts, aggregate numbers, packets presented as complete, or result tables.
- Decimal arithmetic and the existing receipt verifier remain authoritative. Browser drawing code cannot manufacture verified values.
- A receipt binds content for integrity; it does not authenticate a contract, issuer, host, or the truth of a proposed assumption.
- Containment evidence is an independently requested diagnostic. A healthy Docker indicator is not a passed containment test.

## Information architecture options

| Concept | Strength | Cost / failure mode | Decision |
|---|---|---|---|
| Guided dossier: Import → Match → Review → Compare → Export | Easy first-run orientation; each stage can validate its prerequisites | Frequent backward navigation during investigation; hides relationships between evidence and assumptions; becomes a wizard for a task that is iterative | Use only for the initial import progression |
| Case workbench: persistent case header, scoped navigation, analytical canvas, contextual inspector | Keeps baseline identity, coverage, outstanding work and selected evidence connected; supports repeat analysis and multiple alternatives | Requires explicit selection/state rules and careful small-screen adaptation | **Selected** |
| Spreadsheet cockpit: dense editable grid with formula/scenario panels | Efficient row scanning and bulk data work | Encourages editing evidence in place, obscures baseline immutability, and implies spreadsheet-scale editing not supported by the fixed calculation contract | Use table conventions; do not adopt spreadsheet editing |

The selected workbench combines a compact case overview with task-specific views. Import is an input stage, not a permanent third of the screen. Source evidence is a contextual inspector, not a succession of blocking dialogs. A comparison is a named analytical object, not another indistinguishable filename in run history.

## Workspace layout

At a 1440 × 900 desktop viewport:

1. **Left rail, 204–220 px:** Prooflane wordmark; `New case`; current case views; recent cases. Footer shows this-browser retention scope and a compact runtime entry. Use an explicit chevron/menu to collapse the rail; do not add decorative slogans.
2. **Case header, 72–88 px:** breadcrumb, editable case title, case state, baseline mode, source coverage, and `Download case packet`. A second compact line shows baseline creation time and shortened run ID with a copy control. Full identities live in Evidence.
3. **Case navigation, 40–44 px:** `Sources` with unresolved count, `Overview`, `Explore` with alternative count, `Evidence`, matching the agreed implementation contract. `Execution` is a subview of Evidence. The legacy single-CSV review remains reachable through a clearly labelled separate view.
4. **Analytical canvas:** 24 px outer padding; 16–24 px gutters; four-column metric strip; a main analytical surface and selected-record inspector. Tables receive the most width.
5. **Inspector, 320–360 px when open:** selected row, match, alternative or receipt. It can be closed or expanded. Selection does not replace the overview or reset filters.

Keep the case header and view navigation visible. Use one main page scroller by default. A table may own vertical scrolling only with an explicit fixed height and a sticky header; avoid nested scrollbars in the rail, table, inspector and page all at once.

```text
┌─────────────┬───────────────────────────────────────────────────────────┐
│ Prooflane   │ Operations / Cases / November supplier review           │
│ + New case  │ November supplier review        Reference complete       │
│             │ 24 invoice rows · 24 matched       Download case packet  │
│ Overview    ├───────────────────────────────────────────────────────────┤
│ Match    0  │ Overview   Match sources   Alternatives 4   Evidence     │
│ Alt.     4  ├─────────────────────────────────────┬─────────────────────┤
│ Evidence    │ Variance  Flagged  Coverage  Billed │ Selected source     │
│             ├─────────────────────────────────────┤ INV-2402 / row 3    │
│ Cases       │ Sensitivity to contract price       │ Atlas Industrial    │
│ • November  │  plot + numeric assumption input    │ Invoice ↔ Contract  │
│ • Sample    │  baseline marker / tested markers   │                     │
│             ├─────────────────────────────────────┤ Original values     │
│             │ Named alternatives / signed deltas  │ Calculation         │
│             ├─────────────────────────────────────┤ Evidence links      │
│ Session     │ Findings table / search + filters   │ Test assumption     │
└─────────────┴─────────────────────────────────────┴─────────────────────┘
```

This is a responsive layout contract, not a requirement to squeeze all content into one screen. At 1440 × 900, the case identity, mode, coverage, next action, meaningful portion of the plot and at least the first actionable rows must be visible without scrolling past introductory copy.

## View 1: import and contract matching

### Start a case

Empty state is a real work surface with two compact import slots: `Invoice rows` and `Contract prices`. Each has a short schema hint, accepted format, limit, and `Choose CSV` / `Paste CSV`. Use a small text link for `Use fictional sample case`. The sample is labelled fictional before and after loading.

Retain the existing six-column CSV as a clearly named input path: `CSV with embedded contract prices`. It does not represent matching against a separate contract. Existing receipts and saved runs remain accessible.

After import, replace the upload slots with source file chips showing filename, row count, parse status, and an `Inspect source` control. A changed file marks the draft as changed and invalidates any pending matching result. It must not mutate a prior case's baseline or retain its completed status.

### Match workspace

Use a compact queue/table at left and a comparison inspector at right. Default to unresolved rows when any exist. Table columns: invoice / source row, vendor, explicit match key, billed unit price, selected contract price, match state. Search is textual and scoped to imported rows; status filters include `All`, `Unresolved`, `Ambiguous`, `Matched`, and `Embedded` as applicable.

The agreed invoice schema is `invoice_id,vendor,item_id,invoice_date,quantity,unit_price,notes`; the contract schema is `contract_id,vendor,item_id,valid_from,valid_to,contract_price`. Matching uses exact trimmed case-sensitive vendor/item values plus inclusive date containment. Expose that rule beside the matching queue and in the packet. Do not silently infer keys from notes or treat fuzzy similarity as a confirmed contract match.

Match states are distinct:

| State | Meaning | UI / baseline behavior |
|---|---|---|
| Exact match | One eligible contract row for the documented key | Show both source row references and applied price |
| Unmatched | No eligible contract row | Amber issue; select a valid source or correct the import |
| Ambiguous | More than one eligible row | Show candidates side by side; require explicit choice |
| Manually selected | User selected a particular candidate | Show the selected contract row and record the decision; do not rename it exact |
| Embedded price | Contract price arrived in the legacy invoice CSV | Neutral state; no external contract link implied |
| Invalid source | Required structure or value is invalid | Inline parse error with source and row; do not run |

Selecting a row shows the invoice and candidate contract values in aligned columns. The `Use this contract row` action records a choice, it does not certify legal applicability. Include item key, source filename, source row, currency and price; include effective dates only if the schema actually supports and evaluates them.

Block baseline creation until all required rows are resolved or explicitly excluded with a reason. The agreed contract supports exclusions, so the overview, action label and packet must show excluded counts from the first implementation. Do not silently drop unmatched rows or fill a missing contract price with zero. Never label a matched-subset total as total exposure for the complete invoice file.

The footer action reads `Create baseline · 24 matched rows` when ready, or `Resolve 2 source matches` when blocked. Keep the mode selector adjacent to this action. It collapses to a read-only mode chip after baseline creation.

## View 2: case overview

The overview should answer five questions quickly: what data is included; what positive variance exists; what rows require attention; which assumptions materially affect it; and whether the evidence is complete.

- Header: case title, mode-specific completion label, baseline timestamp and packet action.
- Metric strip: `Positive variance`, `Flagged rows`, `Source coverage`, `Total billed`. Each value has a short scope label. Never call variance recoverable savings.
- Open-work strip: unresolved matching issues, failed alternative runs, or unavailable source records. This is actionable and disappears when empty; it is not a generic warning banner.
- Main chart: sensitivity for a selected finding, with the baseline amount visible beside it.
- Compact alternatives preview: named runs and signed deltas with `Compare all`.
- Findings table: sorted by largest variance by default, with `All source rows` available for sensitivity on currently unflagged rows. Show invoice ID, vendor, quantity, billed price, contract price, variance and evidence action when space permits.

Clicking a finding selects it and populates the right inspector. Use a visible selected-row state and a textual inspector heading. The inspector repeats the exact calculation `(billed − contract, floored at 0) × quantity`, identifies invoice and contract source rows, and offers `Test this assumption`. Details do not float above and obscure the table on desktop.

## View 3: sensitivity and named alternatives

### Sensitivity plot

A sensitivity plot is a decision tool, not a decorative vendor bar chart. It answers: **If this one quantity or unit price changes, how does the case's positive variance change?**

Controls: select an API-provided target, show its affected rows, and enter numeric low/high bounds that include the baseline value. A shared contract target shows its contract ID and every bound invoice; row quantity/unit-price targets show their source identity. A slider may supplement numeric inputs; it cannot be the only input. Quantity remains a positive integer; currency retains the server's precision/range rules. Support up to 24 bounded targets and a visible `Restore fixed inputs` action.

Plot semantics:

- Horizontal axis: the selected input with unit, for example `Contract price · USD`.
- Vertical axis: either case total positive variance or selected-row variance, explicitly labelled. Default to case total so unaffected rows remain part of the context.
- Baseline: ink marker, dotted reference line, explicit amount.
- Current draft: hollow marker with `Preview · not executed`.
- Verified alternative: filled blue marker labelled by alternative name. Reference-mode points use `Reference complete`, not an independent-verification badge.
- Kink/break-even: show only if within the plotted range and mathematically meaningful. Never suggest a negative positive-variance total below zero.
- Numeric data table or accessible text accompanies the plot, including baseline, proposed input, result scope and signed delta.

The agreed `/api/cases/{id}/bounds` endpoint supplies trusted interval-analysis results in `case.intelligence`, without model or sandbox execution. Use that returned analysis for the range/impact plot and a ranked `Evidence to check next` list. Show each bounded target's low/high impact and affected rows. A shared contract is one variable; do not draw it as independent uncertainty on each invoice. Joint ranges come from joint recalculation, never a sum of isolated deltas. The earlier axis-based sensitivity view is an optional presentation only where actual returned points support it; do not invent a curve from unavailable data. Label all interval results `Trusted estimate · not an executed alternative`. Browser drawing may position provided numbers, but cannot manufacture verified amounts. Moving a slider must never invoke model inference or create a sandbox run.

Use SVG for the plot with an accessible name and description; no chart library is needed. Labels should be readable without hovering. Keyboard focus exposes the same point information as hover, and a table view provides every numeric value. Preserve the plot bounds while comparing alternatives; silently rescaling the Y axis exaggerates differences.

### Alternatives matrix

The agreed limit is four **named** alternatives plus the original baseline, yielding five comparable options. Each alternative is independently executed against the original baseline with up to 12 distinct targets. The names are short user-authored labels, not generated claims about which contract is correct. Show a changes editor with target, original value, proposed value and affected-row count; a shared contract target expands to its bound rows. Reject duplicate/overlapping targets and explain them inline.

Example names for the fictional sample, shown only after actual values are entered or deliberately loaded as drafts. The first three retain simple legacy examples; new source-matched cases should use the API-provided shared contract targets:

| Name | One changed assumption | Initial state |
|---|---|---|
| Supplied baseline | No change | Existing completed run |
| Atlas negotiated price | INV-2402 contract price → 80.00 | Draft until run |
| Atlas billed-price correction | INV-2402 billed unit price → 72.00 | Draft until run |
| Atlas reduced quantity | INV-2402 quantity → 30 | Draft until run |
| Northstar contract adjustment | A separately selected Northstar contract-price cell | Draft until value supplied and run |

No fabricated totals, confidence percentages, labels such as `best`, or pre-verified sample alternatives. A draft may show a clearly marked preview; completion status requires a real run.

Use a matrix with baseline pinned at the start and alternatives as rows on ordinary screens. Columns: name, target/affected-row count, changes summary, total positive variance, signed delta, flagged rows, state, inspect. Expand the changes summary to inspect all targets. This scales better than narrow cards. Offer side-by-side detail for a selected pair, not multiple full receipt cards. Include a multi-target example, such as a shared contract price plus one quantity assumption, and clearly show the jointly recalculated result.

Draft rows support `Run`, editing the name and changes, and removing unsaved draft targets. Completed rows support `Inspect` and existing evidence downloads. Do not expose rename/delete actions for persisted alternatives until an API exists for them. Keep the original mode fixed, make failed alternatives visibly failed, and allow other completed alternatives to remain usable.

Draft edits invalidate only that draft's preview/result binding. They never relabel an old successful run with new assumption values. A completed alternative is immutable; `Duplicate as draft` is the safe editing operation if capacity remains. Show `4 of 4 alternatives` when full. On a stale case revision (409), retain the draft, refresh case state and explain that it must be reviewed before resubmission.

## View 4: evidence and dependencies

Use a deterministic dependency path with selection and detail, not a force-directed graph. The graph should explain lineage, never imply probabilistic causality.

`Invoice source row → Contract source row / embedded price → Normalized input cell → Baseline calculation → Alternative change → Verified output → Receipt / case packet`

The visual path uses small connected nodes with labels, icons and status text. It has an equivalent nested list for screen readers and narrow screens. Selecting a node highlights the connected row, field and result. Use real hashes or source identities returned by the API; do not invent link badges from DOM state.

The inspector contains source facts, declared match decision, exact formula, mode, checks, and links to input/code/output evidence. Raw code and full hashes remain one disclosure away, with copy controls. Show full identities when opened; abbreviations elsewhere are display-only.

Execution events preserve actual event order and results. Reference mode explicitly says no model and no sandbox. Sandbox recipe mode says fixed Python; model-generated mode says the actual requested/returned model and executed attempt evidence when available. Failed attempts and cleanup uncertainty remain visible.

Containment lives in an `Environment checks` section: `Not run`, `Running`, `Passed probes`, `Failed`, or `Unavailable`, with timestamp and individual results. Do not turn the whole application into a green shield after one diagnostic. Existing probes and fail-closed behavior are preserved.

## Case packet

The primary export becomes `Download case packet`; existing single receipt and comparison downloads remain available under Evidence.

The case packet is a structured JSON artifact first. It contains:

- Versioned manifest: case title, creation time, source scope and execution mode.
- Original source imports or exact canonical source material permitted by the case schema, with content hashes.
- Explicit matching rules, source-row mapping, unresolved/excluded state if that is supported, and manual choices.
- Baseline receipt unchanged.
- Named completed alternatives, their unchanged receipts, and baseline identity/hash links.
- Recomputed signed comparisons and a packet integrity hash.
- Draft and failed alternatives represented as such, without success figures or receipt claims.
- A plain-language boundary: arithmetic and integrity do not establish source truth, issuer authenticity or contractual liability.

The offline verifier must check every embedded receipt and comparison, canonical source/mapping consistency, baseline identity, alternative linkage and packet hash. Do not just hash a JSON export and call it verified. A readable summary file is optional; it cannot replace the machine-verifiable packet.

Before download show a compact completeness summary: `Baseline + 4 completed alternatives · 2 source files · 24 matches` or `Drafts excluded from completed comparisons`. No modal is needed for a normal download. Use a meaningful filename derived from the case title plus a safe case ID.

## Visual identity and density

Direction: **precise, calm, analytical**. Retire the warm editorial/serif hero, italic slogan, stacked overlarge cards and decorative receipt illustration. Preserve the Prooflane name and a restrained line-based mark.

Suggested tokens, to be contrast-tested in the rendered implementation:

| Role | Token |
|---|---|
| Canvas | `#F4F6FA` |
| Surface | `#FFFFFF` |
| Rail | `#111827` |
| Primary text | `#172033` |
| Secondary text | `#526079` |
| Dividers | `#D9E0EA` |
| Primary action / selected analytical mark | `#2457E6` |
| Selected surface | `#EDF2FF` |
| Positive completion state | `#16724A` on `#EAF7F0` |
| Attention / unresolved | `#8A4B05` on `#FFF5DD` |
| Failure | `#B42336` on `#FFF0F2` |

One blue accent anchors action and selection. Green means a specific completed check, not commercial savings. Amber means missing information or attention, not an unverified amount that can be treated as trustworthy. Numerical increases/decreases use a sign and text; they are not automatically good/bad.

Use system sans (`Segoe UI`, Arial, sans-serif), tabular numbers for all money/counts, and a monospace face only for source IDs, hashes and code. No new font download or asset dependency. Case title 24–28 px/600; section title 16–18 px/600; body/control 14 px; secondary 12–13 px; amounts 26–32 px. Avoid 8–10 px uppercase captions for essential content.

Spacing scale 4/8/12/16/24/32. Table rows 40–44 px for one-line content, 52–56 px for two lines. Controls minimum 36 px desktop, 44 px touch. Corners 6–8 px, 1 px borders, near-zero shadows except raised inspector or dialogs. Use separators and shared surfaces instead of a card around every paragraph.

## Motion, responsive behavior and accessibility

- Motion signals state: 120–160 ms opacity/background transition for selection, at most 180 ms for inspector reveal. No staggered card entrances, animated number counters, moving gradient, particle background or decorative loading sequence.
- A running action shows its actual stage if the API supplies one, otherwise an honest `Running…` with elapsed wait. Do not animate a fake pipeline of successful checks.
- Respect `prefers-reduced-motion`: no smooth scroll or slide motion; show the same state immediately. Preserve focus and avoid shifting large blocks when data arrives.
- At 1100–1280 px, inspector opens as a drawer with explicit close and return-focus behavior; main table retains usable width.
- At 768–1099 px, rail becomes compact; case navigation stays accessible. A selected row opens a full-width detail panel rather than shrinking the table to unusable columns.
- At 390 px, use a compact case header and menu, stack metrics in two columns, and render alternatives as row cards with identical labels. A table may scroll horizontally inside a labelled region; the page itself must not overflow horizontally. All case views and history remain reachable.
- Semantic landmarks, one H1 per view, native buttons and form labels. Tables use captions and correct header scope; sortable headers expose `aria-sort`. Do not apply ARIA grid semantics without implementing its keyboard model.
- Selection is not focus. Maintain a clear focus ring, selected-row style and text label. Escape closes a drawer/dialog and returns focus to the opener. Case-view switches move focus to the view title; background refreshes do not steal it.
- Status changes use concise `aria-live` announcements. Errors use an inline message associated by `aria-describedby`; submission errors focus the error summary or first invalid control. Do not rely on toast-only feedback.
- Graph and plot affordances must work with keyboard and have equivalent textual/table evidence. Color is never the sole indicator of state or series.
- Validate text contrast, control boundaries and focus at real sizes. Test 200% zoom and narrow widths; do not claim conformance from token selection alone.

## Error and incomplete states

| Trigger | Display | Recovery |
|---|---|---|
| No sources | Two compact import slots and sample-case action | Choose/paste valid inputs |
| Malformed CSV | File, row and specific rule; keep previous source visible as previous | Replace or edit draft input |
| Ambiguous / unmatched contract | Count in navigation, filtered issue queue, disabled baseline action with reason | Select valid match or correct sources |
| Changed input after run | `Draft differs from baseline`; retain baseline identity and values | Restore baseline inputs or create a new baseline |
| Same-value alternative | Inline `Enter a different value` | Keep focus in numeric field |
| Unsupported value | Range/precision rule with entered value retained | Edit value |
| Docker unavailable | Sandbox controls unavailable with reason | Explicitly choose reference for a new case; no fallback for an existing sandbox baseline |
| Live inference unconfigured | Unavailable mode with the real reason | No misleading setup success or AI claim |
| Failed alternative | Failed row, no successful totals, visible actual events | Duplicate/adjust draft and retry under current rules |
| Verification mismatch | Result withheld; exact failed checks | Inspect evidence; never chart the rejected result |
| Source/receipt expired | `This browser-session record expired`; preserve downloadable packet guidance | Import a new case; do not reconstruct missing original as authenticated |
| Packet incomplete | List missing/failed/draft items with the correct scope | Export available evidence clearly or complete runs |
| Network / quota failure | Localized error and retry; retain draft | Retry after indicated recovery; prevent duplicate submissions |

## Integration map

These are implementation recommendations, not assertions about existing endpoints. Agree exact new payloads with the backend owner before wiring UI. Keep the existing API semantics and security checks.

| File / area | Existing responsibility | Suggested change |
|---|---|---|
| `web/index.html` | Tall setup/result/trust page, existing IDs | Replace shell with case header, scoped views, analytical canvas and inspector. Retain reusable form and receipt controls where appropriate, with stable testable IDs |
| `web/styles.css` | Editorial palette, stacked cards, existing responsive/reduced-motion rules | Replace tokens and layout sections coherently; remove obsolete overrides rather than piling a third style layer over the old design |
| `web/app.js` | Same-origin API helper; run/draft binding; history; mode health; findings; execution/containment | Preserve API wrapper and provenance logic; make case selection, selected view, selected row and draft state explicit; adapt `renderRun`, `showFinding`, history and error display |
| `web/scenario.js` | One-cell source fetch, scenario submit and pairwise comparison | Preserve legacy behavior; implement new case alternatives in a separate module so multi-target semantics cannot accidentally weaken the old contract |
| `web/format.js` | Money/quantity display | Reuse exact-format helpers; do not duplicate monetary formatting in chart code |
| New small JS modules, only if useful | No current source-matching or case orchestration module | Separate matching view, SVG plotting and evidence rendering from API state; no new framework/library |
| `prooflane/app.py` | Run/source/scenario/comparison/receipt/health/containment endpoints | Add case/import/match/alternative/packet endpoints if implementing durable server-side cases; reuse existing owner session and limiter patterns |
| `prooflane/analysis.py` | Exact six-column parsing and Decimal rules | Keep authoritative calculation unchanged; normalize newly resolved imports into its canonical six-column input rather than accepting ambiguous fields |
| `prooflane/comparison.py` | Exactly one declared cell; same mode; two checked receipts | Preserve old checks. New case verifier independently reconstructs all declared target changes, including every row affected by a shared contract, and rejects undeclared changes |
| `prooflane/store.py` | Session-owned run records with expiry | Persist case metadata and source/matching manifest with the same ownership and bounded-retention semantics if required; do not pretend browser-only labels survive another session |
| `scripts/verify_receipt.py` | Receipt/comparison verification entrypoint | Add explicit versioned case-packet support; preserve existing formats and clear failure messages |

Existing endpoints that can be reused directly: `GET /api/health`, `GET /api/sample`, `GET/POST /api/runs`, `GET /api/runs/{id}`, `GET /api/runs/{id}/source`, `POST /api/runs/{id}/scenario`, `GET /api/runs/{id}/receipt`, `GET /api/runs/{id}/comparison`, `POST /api/containment`.

Agreed additive APIs are specified in `docs/WORKBENCH_CONTRACT.md`: `/api/cases/match`, `/api/cases/sample`, `GET/POST /api/cases`, `/api/cases/{id}`, `/api/cases/{id}/variants`, `/api/cases/{id}/bounds`, `/api/cases/{id}/packet`, and `POST /api/verify-packet`. Use the returned `revision` in every mutation, `limits` for UI capacity, `targets` for supported changes, and `source.bindings` for evidence edges. Packet verification is read-only and does not import the case or execute code. Its UI needs a local file/paste control, a clear result, individual checks and the scope boundary.

## Acceptance evidence

The transformation is done when the actual browser demonstrates:

1. Import two synthetic source files, see at least one genuinely ambiguous/unmatched row, resolve it with the selected source visible, and produce a baseline only after the required matches are resolved.
2. Open a case and see its identity, mode, coverage, variance and next action without an introductory hero or persistent full upload form.
3. Select a finding and trace it to both source rows or an honestly labelled embedded contract price, while preserving context in the findings table.
4. Change a supported assumption in the sensitivity view; draft preview is distinguished from a completed run and keyboard/numeric access works.
5. Create at least three named alternatives within the four-alternative limit, including a shared-contract change and a joint multi-target case. Exercise at least one rejected/invalid draft and stale-revision path; every completed alternative remains attached to the original baseline with correct jointly recalculated deltas.
6. Inspect the actual input/code/output/receipt dependency path, reference-vs-sandbox provenance and separate containment state.
7. Download a case packet through the browser and pass the offline verifier; a deliberately tampered packet fails. This must exercise matching metadata and all included alternatives, not only the outer hash.
8. Reopen a saved case, navigate by keyboard, exercise reduced motion, and inspect desktop plus narrow mobile screenshots. No inaccessible history, obscured core action, clipped numeric values or unexpected horizontal page scrolling.

Record actual commands, browser actions, screenshots and limitations. A polished screenshot alone is not evidence that matching, alternative persistence or packet verification works.

## Primary reference patterns

These references inform interaction structure, not copied assets, styles, code or claims of user research:

- [SAP Fiori page layouts and floorplans](https://www.sap.com/design-system/fiori-design-web/v1-136/page-types/floorplan-overview): list/detail relationships and side-by-side comparison. Inference for Prooflane: keep the selected evidence adjacent to the analytical context instead of opening repeated blocking dialogs.
- [IBM Carbon data-table guidelines](https://www.carbondesignsystem.com/building-blocks/core/components/data-table/guidelines): table width, consistent density, toolbar actions, progressive disclosure and detail panels. Inference for Prooflane: use a broad comparison matrix and contextual inspector rather than nesting data in small cards.
- [Linear Triage](https://linear.app/docs/triage): a dedicated inbox for reviewing incomplete incoming work before it enters the normal workflow. Inference for Prooflane: unresolved source matches should be visible work items with explicit resolution, not hidden warnings beneath an upload control.

Accessed 2026-11-03. No competitor assets downloaded and no additional UI libraries proposed.
