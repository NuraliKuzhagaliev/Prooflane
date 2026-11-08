# Prooflane — UX, interaction and instruction audit

5 ноября 2026, Asia/Qyzylorda. Read-only review of the current application source and two existing screenshots from this repository. No application edits, browser interaction, new runtime tests, user study or adjacent-project inspection were performed by this reviewer. The reviewer owns this document only. Other agents are working in the repository.

## What the product asks a person to do

The object is a review case, not a collection of metrics. The person connects invoices to supplied contract records, resolves ambiguity, freezes a baseline, challenges assumptions and hands the resulting evidence to another reviewer. The useful action is to follow a disputed price from its source into its consequences. Design should make that chain perceptible.

The supported model is intentionally bounded: two exact-schema CSV sources, explicit selections or exclusions, immutable baseline, shared contract targets, up to four executed alternatives with up to twelve joint changes, and up to twenty-four declared ranges. Reference, fixed-code Docker and live-provider execution have different meanings. A redesign cannot erase these distinctions or turn draft inputs into verified output.

## Instruction and capability audit

| Source | Actual effect | Design implication |
|---|---|---|
| User's current design mission | Requires structural divergence, three distinct concepts, real implementation and observed browser evaluation | Current art direction is explicitly open for replacement. Preserving the current sidebar or cards would not satisfy the request. |
| AGENTS.md | Preserves stack, current-project scope, credentials, execution isolation, provenance, truthful evidence and budget | It does not prescribe a color system, sidebar, cards, header, font or page composition. |
| project-bootstrap | Discovers actual capabilities, preserves architecture and existing instructions; distinguishes structural verification from product validation | “Preserve architecture” means Python/FastAPI, vanilla JS, API contracts and data. It does not mean preserve CSS composition. |
| hub-engineering | Requires file ownership, acceptance criteria, actual integration and honest checks | Helps deliver the redesign. It is not a visual design system. |
| hub-innovation | Requires evidence-backed opportunities and discriminating tests, avoids novelty without user value | Supports task-specific interactions. It does not authorize unrelated functionality. |
| docs/WORKSPACE_DESIGN.md | Previous proposal explicitly mandates a204–220px left rail, persistent case header, duplicate view navigation, four metrics and320–360px inspector | This is the strongest local source of template inertia. Mark its visual prescription superseded; retain its mathematical, evidence and API invariants. |
| Historical design review and screenshots | Evidence about a previous version, its observed defects and then-selected solution | Evidence should inform risks. A previous selection of “workbench” is not a permanent rule that every later redesign must repeat. |
| Existing DOM IDs and handlers | A concrete implementation interface | IDs can move to a new composition. Maintaining their existence does not require retaining their old wrappers or styling. |

No nested AGENTS.md was found by `rg --files web docs -g AGENTS.md`. This review read root guidance and the three selected skills above; it did not mechanically invoke unrelated 3D, voice, hosting or image-generation workflows.

The current session exposes the existing engineering/research skills, local source-edit/test tools, web research and browser/computer-use capabilities. That proves availability of tool entry points, not a completed browser or authenticated design-service session. There is no `Creative Director`, `Product UX Designer` or `Interaction Designer` named agent type in the current callable role enum; those are responsibilities that can be assigned to available roles. A generic agent can perform an actual independent bounded review, as this one does. A configured agent file alone is not an invocation.

Canva/Sites/Higgsfield-style tools exist in the broader catalog, but their presence does not establish authentication or justify rebuilding the current application on another platform. The current request can be delivered in the existing vanilla frontend. A 3D skill is not relevant solely because the user asked for an outstanding interface.

Cross-project comparison: **NOT_PERFORMED**. AGENTS.md limits work to this project and explicitly says not to change adjacent projects; no neighboring repository was enumerated or inspected. The actual comparison here is between `artifacts/transformation-review/before-initial.jpg` and `artifacts/transformation-review/design-v3/cycle2/09-native-overview-1762x1175.jpg`, both belonging to Prooflane. Claims about other user projects would be unsupported.

## Why the current output still feels templated

The historical cream/green version and current blue version differ in color, font treatment and functional depth. Their organizing frame is recognizably related: dark left rail, logo and history, a broad light canvas, boxed forms/results and repeated bordered containers. The blue version replaces the earlier hero with a more efficient analytical layout, but does not establish a new product-specific spatial grammar.

Observable causes in the current source:

1. **The prior design document became a composition recipe.** It selected a left rail and four-card strip before visual exploration. Subsequent work implemented that frame competently rather than questioning it.
2. **Navigation is duplicated.** `.wb-rail-nav` and `.wb-tabs` expose the same four `data-wb-view` destinations. They consume space and make the frame resemble a general administration product.
3. **Cards equalize unlike information.** `renderOverview()` emits four `.wb-metric` objects for variance, flagged count, coverage and billed amount. Coverage is a boundary on the claim; variance is the current finding. Peer-level cards conceal that difference in purpose.
4. **The same container rhythm is used for unrelated acts.** Upload, source queue, assumption editing, sensitivity, priority, robustness, alternatives and verification largely use `.wb-card`, a heading and an inset body. Their task semantics are stronger than their visual distinctions.
5. **The generic component skin sets the identity.** Current CSS starts with `.wb-shell` as a216px rail grid, Segoe/Arial, muted blue text, six-pixel form/button radii and repeated cool borders. Those defaults establish a familiar product template before content-specific typography and data relationships do.
6. **Loaded Explore is vertically accumulated.** Sensitivity/editor, next facts/robustness, then alternatives/form are stacked. With many ranges, a tall chart can displace execution and comparison far below the fold.
7. **Generic technical furniture competes with evidence.** Breadcrumb, run identity, mode, four view buttons and per-section kickers repeat hierarchical framing. The actual invoice→contract relation is small `I:n → C:n` text in a table until the inspector is opened.
8. **Interaction mostly changes panels.** Source selection and analysis targets already have meaningful state, but the prominent interaction grammar remains tabs, dropdowns, buttons and disclosure panels. The visual frame does not visibly express a price connection, a shared dependency or a preserved original.

These are source/screenshot findings, not measured user-efficiency results. The current source contains useful accessibility and failure-state work that should be preserved.

## Eight UX opportunities and discriminating acceptance

| Opportunity | Evidence / consequence | Proposed test |
|---|---|---|
| One navigational spine | Same four destinations in rail and tabs | At desktop, tablet and mobile there is one primary wayfinding system; history is a separate deliberate archive action. Every view is keyboard-reachable. |
| Give scope a different semantic treatment from totals | Coverage and variance are peer cards | A first-time reviewer can identify included/excluded scope beside the conclusion without interpreting four equal metrics. Do not invent a user-study pass; review it in the actual screenshot and later with people. |
| Bring the source relation into the main composition | Current source link is small notation; details live in a side panel | Selecting INV507 must show original invoice row8→contract C3 row5→normalized row7, visibly and without losing the row selection. |
| Keep alternative comparison near its draft | Alternatives come after multiple long analytical blocks | A loaded case with three ranges and two alternatives exposes comparison and the next execution action without scrolling through the full sensitivity list.24-range behavior has a deliberate bounded layout. |
| Explain shared impact at the action | Targets show affected rows in several separated places | Selecting shared C1 reveals all three bound invoices before execution. Range display and alternative draft must not imply independent per-row prices. |
| Make errors local to the work | `error()` updates top-level `wb-error` and live announcement; it does not focus or scroll to the invalid field | An invalid range entered near the bottom is visibly explained near the control, retains valid saved results, and associates the error with the field. Global status may accompany it. |
| Improve touch and selected-row affordance | Table navigation uses a small invoice link and a separate arrow; much row surface is inert | The intended row action has a clear and comfortable target; touch does not require hitting a tiny arrow. Keyboard focus has the same result and no pointer-only dependency. |
| Use one contextual selection language | Source row, baseline row, range target and evidence row have separate state | A deliberate transition from a row to its assumption or proof carries that row and explicitly presents the selected shared target. Unrelated unsaved alternative choices are not silently overwritten. |

## Mandatory integration contract

The current code uses imperative DOM lookup. Layout can be replaced, but removing a referenced node or putting permanent controls inside a renderer-owned slot will break initialization or erase controls on the next render.

`web/workbench.js` contains85 unique direct `$('literal-id')` references, plus IDs reached through arrays, helper functions and template strings. This is not the total DOM count. The safest structural method is to retain every existing ID exactly once, then move the nodes into the new frame. Duplicate hidden copies are not a preservation strategy.

| Area | Nodes / behavior to retain |
|---|---|
| Shell and status | `case-workbench`, `wb-main`, `wb-home`, `wb-new`, `wb-title`, `wb-subtitle`, `wb-mode`, `wb-packet`, `wb-identity`, `wb-notice`, `wb-error`, `wb-progress`, `wb-progress-text`, `announcement` |
| View contract | `wb-view-sources`, `wb-view-overview`, `wb-view-explore`, `wb-view-evidence`; `wb-sources-heading`, `wb-overview-heading`, `wb-explore-heading`, `wb-evidence-heading`; primary buttons retain `data-wb-view` values `sources`, `overview`, `explore`, `evidence` |
| History and controls | `wb-case-list`, `wb-cases-empty`, `wb-history-error`, `wb-refresh`, `wb-rail-toggle`, `wb-source-count`, `wb-alt-count`, `wb-tab-source-count`, `wb-tab-alt-count`, `wb-runtime` |
| Source input | `wb-import`, `wb-name`, `wb-invoice-file`, `wb-invoices`, `wb-invoice-file-label`, `wb-contract-file`, `wb-contracts`, `wb-contract-file-label`, `wb-draft-label`, `wb-sample`, `wb-match`, `wb-source-empty` |
| Matching | `wb-match-workspace`, `wb-coverage`, `wb-match-search`, `wb-match-filter`, `wb-matches-body`, `wb-matches-empty`, `wb-match-inspector`, `wb-saved-sources` |
| Baseline creation | `wb-create-footer`, `wb-execution-mode` with reference/sandbox/vultr option values, `wb-mode-help`, `wb-token-wrap`, `wb-operator-token`, `wb-create` |
| Baseline review | `wb-metrics`, `wb-overview-signals`, `wb-row-count`, `wb-row-search`, `wb-row-filter`, `wb-rows-body`, `wb-rows-empty`, `wb-row-inspector` |
| Ranges | `wb-range-summary`, `wb-range-target`, `wb-target-context`, `wb-bound-low`, `wb-bound-high`, `wb-save-bound`, `wb-remove-bound`, `wb-reset-bounds`, `wb-tornado`, `wb-sensitivity-body`, `wb-next-facts`, `wb-leader`, `wb-break-even` |
| Alternatives | `wb-alternative-capacity`, `wb-alternatives-body`, `wb-alternative-inspector`, `wb-alternative-form`, `wb-alternative-name`, `wb-change-capacity`, `wb-change-target`, `wb-change-value`, `wb-add-change`, `wb-change-original`, `wb-draft-changes`, `wb-alternative-token-wrap`, `wb-alternative-token`, `wb-alternative-mode`, `wb-run-alternative`, `wb-alternatives-full` |
| Evidence | `wb-evidence-case`, `wb-evidence-row`, `wb-dependency-path`, `wb-evidence-inspector`, `wb-packet-contents`, `wb-packet-secondary`, `wb-execution-record`, `wb-environment` |
| Packet verification | `wb-verify-form`, `wb-packet-file`, `wb-packet-file-label`, `wb-packet-json`, `wb-verify`, `wb-verify-result` |
| Legacy bridge | `legacy-workspace`, `wb-legacy`, `wb-return`, `wb-promote-run`, `.skip-link`, `workspace`, `trust-boundary`; all pre-existing `app.js`/`scenario.js` nodes and `finding-dialog` remain present |

`wb-exclusion-reason` is created dynamically inside the match inspector; do not create another static node with that ID. Matching candidate selection and exclusion controls are generated with `data-mutating`, which integrates them into the busy guard.

### Render-slot boundaries

Treat these as leaf content hosts. Their children are replaced in normal operation:

- `wb-case-list`, `wb-identity`, `wb-coverage`, `wb-matches-body`, `wb-match-inspector`.
- `wb-metrics`, `wb-overview-signals`, `wb-rows-body`, `wb-row-inspector`.
- `wb-range-summary`, `wb-range-target`, `wb-change-target`, `wb-target-context`, `wb-tornado`, `wb-sensitivity-body`, `wb-next-facts`, `wb-leader`, `wb-break-even`.
- `wb-draft-changes`, `wb-alternatives-body`, `wb-alternative-inspector`.
- `wb-evidence-row`, `wb-dependency-path`, `wb-evidence-inspector`, `wb-execution-record`, `wb-verify-result`.

Do not nest navigation, a persistent selector or a new action inside these slots. Place permanent controls in siblings. Rendered `tbody` slots must remain table bodies; selects must remain selects; forms remain forms with their current submit semantics. `text()` writes `textContent`, so static decorative child spans inside its target will disappear. `renderHeader()` replaces `wb-mode.className`; use ID/parent selectors or deliberately adapt the renderer for a new visual treatment.

The initial mobile statement `document.querySelector('.wb-case-history').open = false` requires a real matching details element if left unchanged. If history becomes a dialog/drawer, change this statement and its semantics deliberately rather than removing the element and causing a startup exception. The current `wb-rail-toggle` handler toggles `nav-collapsed` on the shell and changes aria-label/expanded/text. A new archive toggle needs its own coherent behavior, focus return and Escape handling.

## Critical state and event dependencies

### Initialization and same-origin session

1. `app.js` defines `window.prooflaneSessionReady` and begins health initialization; this establishes the shared owner cookie.
2. The workbench registers its handlers, renders empty views, then awaits that promise or the `prooflane:session-ready` event.
3. Workbench health comes from `window.prooflaneHealth` or `prooflane:health`, followed by `refreshCases()`.

Starting case/history requests before the shared initialization can produce competing first-session cookies. Keep the script order and ready gate. Every JSON mutation retains credentials `same-origin`, `Content-Type: application/json` and `X-Prooflane-Request:1`.

### Source editing and immutable baseline

- `sourceRequests` and `sourceLoading` are per source type. A newer selection must win when old file reads finish late. Invoice and contract reads must still complete independently.
- Paste/edit, reset, sample, open-case and case acceptance invalidate pending reads appropriately. Match/create stay disabled while a read is pending.
- `invalidateSources()` clears match results, selections, exclusions and synthetic status. A source edit cannot leave an old ready-to-create baseline.
- Matching only publishes the returned report. Unresolved rows require an eligible selection or explicit reasoned exclusion; selection and exclusion for one row are mutually exclusive.
- Once `state.active` exists, source evidence is frozen. Editing source evidence means a new case, never a quiet mutation of the original.

### Saved case acceptance

`acceptCase()` first fetches baseline source rows, then commits active case identity and rows together. If that fetch fails, the previous case must remain internally consistent. With reset, it clears alternative draft, selected targets/rows and filters. Row identity distinguishes invoice original record, normalized record and contract record; do not display one number as if it were the other.

### Ranges and alternatives

- Range state belongs to `active.bounds`; the draft low/high is not a saved result. Returned `active.intelligence` is authoritative for totals and priorities.
- Shared target IDs such as `contract:C1` represent one linked variable. Browser chart geometry may position returned numbers, but cannot create new verified amounts.
- `mutateCase()` sends the current revision.409 reloads latest saved data and preserves the range draft for review. A200response with `failed_run` is still failure: retain draft, show actual failure and do not append a completed alternative.
- `state.changes` belongs to the unexecuted alternative draft. Each executed alternative starts from the original baseline, not from the selected alternative. Baseline mode is inherited and token is cleared after each attempt.
- `completionLabel()` distinguishes Reference complete from Independently verified. Never style a draft, pending interval or failed run as completed execution.

### Evidence and verification

- The dependency inspector follows the selected baseline row and its original source binding. It is not an editable provenance graph.
- `packetRequest` invalidates old file reads and responses. Editing/pasting a packet hides any prior success immediately. An old successful response cannot validate new text.
- Browser verification uploads the packet and included source data to this server; CLI is the offline option. Preserve this disclosure wherever the new verifier is placed.
- `showLegacy()` and `returnWorkbench()` toggle the shells and update the skip-link target. The saved workbench state survives a visit to the old path.
- `prooflane:promote-run` creates an embedded-price case from a qualifying original; `prooflane:open-run` lets failure inspection open the actual run in legacy. Keep event names and payload shapes (`detail.id`, optional `detail.name`).

## Interaction thesis and divergent design axes

**Thesis: follow a price, preserve the original.** The primary gesture should reveal which source supports a price, which invoices share it and which saved alternatives change its consequence. Motion should explain the connection or preserved original. It should not decorate arrival on every screen.

Three defensibly different axes to test, independent of palette:

| Axis | Document-first review folio | Evidence atlas | Comparative instrument |
|---|---|---|---|
| Main composition | One dossier/spread, ruled ledger, annotations in a margin | Spatial network of real invoice/contract connections with on-demand inspector | Wide common-scale comparison tracks and scenario columns |
| Navigation | Numbered document spine and deliberate archive | Focus/zoom plus breadcrumb back to case; list fallback | Baseline/alternative switch and tool modes in one command strip |
| Primary interaction | Select a cited record; its annotation opens beside it | Follow one real edge; expand shared dependency | Pin original, compare executed alternatives; edit a separate draft |
| Data emphasis | Exact source rows and coverage | Relationship multiplicity and original-source identity | Signed changes, conditional ranges and invariant baseline |
| Main risk | Becoming another tall form if document sections all remain expanded | Accessibility, graph scale and adding a rendering dependency | Resembling a generic trading dashboard or overstating quantitative certainty |
| Useful motion | A margin annotation connects to selected source; original anchor stays | Real path highlights as focus changes; no physics decoration | Shared baseline stays fixed as alternative/range changes |

These are distinct architectures, not three styled versions of one card grid. Product fit should be assessed by the same task: resolve C2R and exclusion, identify7/8scope, follow C1's three bound invoices, distinguish original768/shared368/joint568, set two ranges148..1993 and export a verifiable packet. Novelty alone cannot outweigh readability and accurate scope.

A document-first design appears feasible without a new framework and can express the existing evidence model particularly well. That is a recommendation, not a completed concept selection or user-validation result. The director's independently researched concepts and actual prototypes should be compared before implementation.

## Acceptance and regression boundaries for the implementation

1. Desktop, tablet and mobile: one primary navigation system; scope, original mode and next action are visible; no clipped content or page-level horizontal overflow. Wide numeric tables may have clearly contained horizontal scrolling.
2. Exact-ID source flow: real file selection, matching, required C2R choice, reasoned exclusion, baseline creation and original/normalized row distinction remain correct.
3. Loaded product: baseline768/7110/7of8; C1=80 gives368; joint C1=80+row2quantity80 gives568. Two ranges give148..1993, with information-reduction minima645 and0. Do not present the larger minimum as greater utility for every possible answer.
4. Keyboard: every row action, navigation action, chart target and disclosure is reachable and activated with its proper native semantics. New dialogs return focus and close with Escape. Selected and focused states are distinct.
5. Touch: controls remain comfortably targetable; no essential hover-only information; no drag-only task. If dragging is added, numeric inputs and keyboard alternatives remain available.
6. Reduced motion: contextual animations switch to immediate state changes under `prefers-reduced-motion:reduce`; target and source identity remain clear without animation. Runtime verification must be distinguished from CSS review.
7. Failure recovery: invalid range retains valid saved analysis; failed alternative retains draft; stale revision keeps a coherent case; failed source fetch cannot mix identities; errors appear near the active work and are announced.
8. Async correctness: delayed old source/packet reads and old verification replies cannot overwrite new inputs, success labels or a different opened case. Source edits invalidate prior source decisions.
9. Verification: actual downloaded case packet passes CLI and browser checker; a modified/rehashed inconsistent packet fails; browser upload disclosure remains visible.
10. Legacy: original1480→single-scenario1160→download verification and return to the new frame remain functional. The new design must not create duplicate IDs or unintentionally style hidden legacy nodes.
11. Performance: no new library is required by these recommended interactions; record actual page/assets size and large-source rendering. Avoid binding repeated listeners on every render or forcing layout for every row during animation.
12. Evidence: capture real desktop/tablet/mobile screenshots and repeat the main path. Evaluate at least five concrete improvement candidates from the actual result; implement only justified ones. Source review, old screenshots and generated prototypes are not a substitute for this final browser pass.

## Exact scope of this audit

Observed: source functions, markup, current CSS, the actual earlier design brief, current selected skills and two archived screenshots. Not observed: the redesigned implementation, present browser runtime, human comprehension, other user projects or authenticated external design tools. No independent visual quality score for a design that does not yet exist is claimed here.

## Independent comparison of the three delivered concept sheets

This section was added after reading the actual `A-evidence-atlas.svg`, `B-audit-folio.svg`, `C-comparison-theatre.svg`, their shared gallery HTML and `REFERENCES_AND_CONCEPTS.md`. Each SVG contains an entry and a loaded composition in the same1500×820frame. The scores below are this UX reviewer's own judgments, not the director's table. The review inspected the authored vector geometry/text and specification; it did not render or operate these as browser applications. Visual quality and interaction scores therefore describe **potential supported by the concept**, not completed execution or measured usability.

| Criterion,1–10 | A / Evidence Atlas | B / Audit Folio | C / Comparison Theatre |
|---|---|---|---|
| Originality | **9** — source ports become a relationship canvas; no inherited dashboard frame | **8** — chapter spine, ruled register and margin annotation change the organizing grammar | **7** — comparison tracks are distinct from current cards, but resemble familiar quantitative consoles |
| Visual quality potential | **7** — coherent node/edge rhythm, but several boxes and long crossing distances need discipline | **8** — typographic contrast and rules organize the document; cream/serif overlap with old Prooflane remains a risk | **8** — common scales, large figures and aligned track rows are visually clear; color must not imply a recommended decision |
| Product fit | **7** — relationships are relevant, but a selected branch must not appear to explain the whole768case alone | **9** — invoices, contract citations, scope and documented decisions are the actual work objects | **6** — successful alternatives dominate; unresolved evidence risks becoming a hidden setup task |
| Usability potential | **5** — focus/zoom and graph orientation introduce new learning;500rows and mobile need a different fallback | **8** — readable register, beside-the-record note and named chapters align with inspection; layout must remain compact | **7** — comparing amounts is straightforward; starting or checking a source is less direct |
| Interaction quality potential | **8** — edge tracing can make shared dependency visible; only if real bindings drive it | **8** — one selected citation can connect ledger, note, target and proof; restrained motion has a concrete job | **8** — pinning the original and selecting paired tracks supports comparison without overwriting it |
| Technical feasibility | **5** — graph navigation, keyboard equivalent, scale and responsive behavior create a large new surface | **9** — semantic HTML, current state/API and existing renderer slots can support the new composition | **7** — the tracks are simple, but source/proof drawers and paired-comparison state require more change |

**Independent recommendation: B / Audit Folio, with conditions.** It is the best fit for the whole case lifecycle, not merely the easiest visual restyle. A would be a useful local evidence trace but an expensive primary navigation model. C is compelling for saved comparisons but gives insufficient prominence to disputed sources and exclusions. Neither should be discarded as meaningless; their useful principles can inform selected-record proof and a common baseline comparison, without importing their full frame.

B is **not approved as “make the blue dashboard beige.”** Its current sketch shares warm paper and a serif title with the historical cream/green version. That collision is real. The implementation must prove divergence through a different composition and behavior:

1. Remove the permanent dark rail and duplicate navigation. Use one chapter spine and a real Archive disclosure/dialog with focus return.
2. Make the source register and adjacent note the main surface. No four-card KPI strip; show768and7/8with distinct semantic hierarchy, including the exclusion reason's location.
3. The first screen must contain both source inputs and a direct match action within a useful desktop viewport. “Every price has a source” can introduce the work but cannot become a second large marketing hero.
4. Preserve the baseline as an anchored original and explicitly distinguish a draft, a saved alternative and a conditional range. Do not animate numeric amounts through invented intermediate values.
5. Let a selected citation be a continuity device: invoice row → contract row → affected shared target → saved alternative/proof. An annotation ornament with no linked behavior fails the concept.
6. Avoid paper clichés: no tilted documents, textures, faux stamps that imply authenticity, oversized ornamental serif or repeated rectangular “sheets” acting as the old cards.
7. Desktop ledger/note must become a deliberate reading sequence on tablet/mobile. A narrow miniature desktop spread is not responsive design. Essential labels and controls retain readable CSS sizes.
8. Selection, errors and focus must remain identifiable without animation or color. Do not use a calm visual style to hide excluded scope, failure or the upload-to-server disclosure.

Newsreader/Plex or another properly sourced local font pair can strengthen typographic identity; it does not by itself satisfy any structural condition above. The three supplied sheets are appropriately labelled static synthetic concepts. Their drawn controls are not counted as functional acceptance.

**Selection gate:** concept comparison is complete. Implementation can proceed with B under these conditions. Final originality, visual quality, motion, usability and accessibility scores require the actual implemented interface, desktop/tablet/mobile screenshots and real behavior checks. This pre-implementation comparison cannot close those gates.
