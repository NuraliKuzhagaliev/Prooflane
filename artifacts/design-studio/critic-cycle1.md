# Audit Folio — independent cycle 1

Reviewer: Design Critic + QA. Date: 2026-11-05, Asia/Qyzylorda. The reviewer changed no application source. Root and the frontend implementer owned those files. This report separates this reviewer's actual UI checks, supporting source inspection and untested conditions.

## Verdict

The implemented desktop interface realizes the selected B direction substantially. It is a ruled review document with one chapter spine, facing source registers, a typographic finding/scope relationship and a selected-record margin annotation. It does not retain the former permanent rail, four peer KPI cards or repeated rounded panels. Warm paper and serif type overlap with historical Prooflane, but the organizing composition has changed. This is more than a palette substitution.

The strongest objection is behavioral: selecting a record in Sources does not carry it into Proof. An annotated dossier loses part of its reason for existing when its source chapter and proof chapter silently refer to different invoices. This prevents approval of cycle 1. Primary export links also have visibly weak text contrast. The exact calculation and packet paths tested here work.

## Review conditions and actual evidence

- Read root AGENTS.md, the UX/process audit including independent concept comparison, References/Concepts, relevant current HTML/CSS/JS and the actual redesigned page. Other projects were not inspected.
- All browser actions used the documented CUA interface. Own Chrome tab `1495970327`, URL `http://127.0.0.1:8765/`; the root's existing tab was not controlled.
- Synthetic sample only: 8 invoices. No provider calls, paid resources, deployment or publication.
- Viewports were measured from the page, rather than inferred from the capability request: desktop **1440×960 CSS px**; tablet **900×800**; mobile **391×800**. On those measured states document scroll width did not exceed client width. The capability required calibration because its requested dimensions and Chrome's reported CSS dimensions differed.
- The browser screenshot backend repeatedly timed out on an initial capture; a fresh state observation and a subsequent supported capture returned bytes. These are actual captures, without image editing. Tablet screenshots are scaled by the backend. The mobile capture is visibly tiled/repeated: **it is a capture limitation, not evidence of a product rendering defect**.
- A later documented attempt to set the 320px test state failed with the browser unavailable. **320px was NOT_RUN.** The reviewer stopped UI control. A temporary viewport override may need resetting when root regains the browser; the runtime could no longer accept that cleanup action.
- Real touch hardware, full screen-reader operation, OS reduced-motion switching, visual-impairment user testing, 500-row browser rendering, rejected/rehashed packet UI and the legacy 1480→1160 path were **NOT_RUN by this reviewer**. Root's other tests are not presented as this reviewer's work.

## Actual functional path

1. Used “Try the fictional review.” The UI exposed 8 source rows, 6 exact matches and 2 unresolved rows.
2. Explicitly selected **C2R / contract row 4** for **INV504 / invoice source row 5**. Explicitly excluded **INV506 / invoice source row 7**, reason: “No supplied contract supports this synthetic invoice.”
3. Created reference case `e7708c3e-fbb4-4995-9d1b-cfcd069c8b24`, baseline run prefix `0cc32a1f-1d8`. Observed **$768.00** positive price variance, **$7,110.00** billed and **7 of 8** in scope. Status said **Reference complete**, with trusted fixed rules/no model or sandbox disclosure. Unavailable sandbox/Vultr modes were disabled.
4. Reloaded the page and reopened the persisted case from Archive. Archive opened as a modal dialog; Escape closed it and DOM inspection confirmed focus returned to `wb-rail-toggle`, with `open=false`.
5. In Sources selected **INV507**; inspector showed original invoice **row 8**, **C3 / contract row 5**. Clicking chapter **04 Proof** instead showed **INV501 / normalized row 2**. This is the included-source continuity failure.
6. Manually choosing INV507 in Proof correctly displayed original invoice **row 8**, C3 **row 5**, normalized input **record 7**, baseline row variance **$0.00**. Thus the underlying distinction is available and the inspector can render it correctly.
7. Later selected excluded **INV506** in Sources and observed its row 7/reason. Proof silently retained previously selected **INV507**, with no excluded-source explanation. This is the same continuity fault with a more misleading boundary case.
8. Ledger's contextual route worked: Inspect **INV504 / source row 5**, then “Follow the evidence path” opened **INV504 / C2R row 4** and focused `wb-evidence-heading`. This should not be confused with the failed Sources chapter route.
9. In Ranges declared shared **C1 [65,85]**. Context explicitly listed **INV501, INV502, INV508**. Returned interval **$148.00–$1,193.00**. Added **INV501 / normalized record 2 quantity [20,80]**; returned joint interval **$148.00–$1,993.00**, width **$1,845.00**. Evidence priority minimum reductions were **$645.00** and **$0.00**, with “up to” bounds kept separate.
10. Submitted invalid quantity range **90..80**. Local and global text explained that the range must include the original and low must not exceed high. Saved **148..1993** results remained. Low field referenced `folio-range-error` through `aria-describedby`, but `aria-invalid` was absent.
11. Switched through the real Ranges/Executed alternatives subviews. Named **C1 at 80** executed to **$368.00**. Named **Joint C1 and quantity**, C1=80 plus INV501 quantity=80, executed to **$568.00**. Both were labeled Reference complete; original **$768.00** remained fixed.
12. Downloaded the actual packet through the browser's export link. Browser returned `C:\Users\nural\Downloads\prooflane-case-e7708c3e-fbb4-4995-9d1b-cfcd069c8b24.json` (23,371 bytes). This is the browser's configured download location; the reviewer did not create a project/cache there.
13. Ran `.venv/Scripts/python.exe scripts/verify_receipt.py 'C:/Users/nural/Downloads/prooflane-case-e7708c3e-fbb4-4995-9d1b-cfcd069c8b24.json'`: exit **0**, `passed:true`, six check groups, 2 alternatives, interval **148..1993**.
14. Through the documented file chooser selected that actual downloaded packet, then activated browser Verify packet. It passed all six check groups. The upload-to-this-server/no-code-execution/offline-CLI disclosure was visible before the action. Successful check text explicitly denied issuer authentication/runtime attestation/contract truth.

## Concrete improvement candidates

Severity describes consequence, not development cost. “Retain” means the proposed change is not justified by this observation; it is not an assertion that no future user study could change the decision.

| Candidate | Evidence and consequence | Severity | Recommendation for cycle 2 |
|---|---|---|---|
| Carry a selected source into Proof and explain an excluded source | Actual INV507 source8→Proof INV501; excluded INV506→Proof stale INV507. The source/proof relationship is the interaction thesis. | P1 | **Fix.** Map original invoice identity to normalized binding. For exclusion, explicitly show the excluded state/reason or redirect with a clear explanation, rather than showing a stale unrelated invoice. Retest both cases. |
| Make primary export-link text as legible as primary buttons | Desktop ledger and verified-packet captures show dark text on oxblood export/download links, whereas Verify has light text. Source confirms `.folio-shell a { color:inherit }` outranks `.wb-primary`. | P2 | **Fix.** Correct primary anchor color and verify computed contrast in the real page. Do not lighten all text/actions indiscriminately. |
| Expose invalid-range semantics on the fields | Actual 90..80 error is local and described, preserves saved results, but low `aria-invalid` is absent. The error is otherwise useful. | P2 | **Fix narrowly.** Set/clear invalid state for the relevant range controls; retain the local explanation and saved result. Confirm recovery after a corrected valid submission. |
| Distinguish original source row in the accessible Inspect name | Supporting source inspection: rendered action says `source row ${row.row}`, where `row.row` is normalized. INV507 is known from the actual Proof inspector to be source8/normalized7. The normal inspector gets this right. | P2 | **Fix and browser-retest.** Use the source binding for the source-row name or explicitly call it normalized. The misleading INV507 action name was not directly inspected in this browser run, so source evidence must not be inflated into a completed UI regression. |
| Replace a zero-range degenerate interval with a specialized empty state | On first Ranges view the page shows 768..768, 0 declared ranges and an explanatory starting prompt. A specialized “fixed inputs” state could reduce terminology. | P3 | **Retain for now.** Existing explicit zero count plus next-action prompt makes the result mathematically and operationally clear. No observed failure justifies another state or decorative empty illustration. |
| Recombine Ranges and Alternatives to expose everything at once | Actual two subviews keep the executed comparison and draft near each other instead of following the whole sensitivity list. The supplied original stays visible in both. | P3 | **Retain the split.** Recombining would restore the old long analytical stack. Retest keyboard arrows/Home/End and mobile fit in cycle 2. |
| Turn finding/scope back into compact metric cards | Actual desktop ledger gives $768 typographic priority and gives 7/8 inclusion an adjacent explicit note, with billed/flagged/mode in a subordinate ruled line. | P3 | **Retain.** Current hierarchy distinguishes conclusion from its boundary and is central to divergence. A card strip would weaken that distinction without resolving an observed task problem. |
| Add an explicit horizontal-scroll hint and selected-note return cue on mobile | Actual DOM at391px had no page overflow; tables are intentionally wider and notes stack below the register. Capture backend prevented trustworthy mobile visual inspection. | P2 if undiscoverable | **Verify before editing.** Keep contained table scrolling; in cycle 2 inspect whether a visible hint exists and whether keyboard/touch can reach Inspect and return to the chosen row. No screenshot-tiling “fix” belongs in application CSS. |

The first four recommendations are bounded fixes. The remaining candidates prevent unjustified cosmetic churn and identify a responsive verification gate. Root was notified about material defects during testing; this reviewer did not implement them.

## Ten subjective scores, 1–10

These are expert judgments of the observed cycle-1 implementation, not measured usability or a claim of perfection. Mobile-capture and unrun conditions limit the applicable scores. They must be reassessed after fixes and a real second cycle.

| Dimension | Score | Observable basis and limit |
|---|---:|---|
| Originality | 8 | One numbered chapter spine, ruled registers and a selected-record annotation replace the former rail/card shell. The folio metaphor is specific, though editorial serif layouts are not intrinsically novel. |
| Art direction | 8 | Consistent paper/ink/oxblood palette, flat rules, restrained utility controls and no faux paper textures or trust stamps. Export-link legibility weakens finish. |
| Typography and composition | 8 | Newsreader headings and finding, mono source identifiers and subordinate sans controls produce meaningful hierarchy in real desktop/tablet captures. Tiny technical labels and the longest case-name/mobile state still need cycle-2 inspection. |
| UX clarity | 7 | Explicit C2R/exclusion, 7/8 scope, fixed original and local invalid-range recovery were comprehensible in the path. Stale source→proof selection is a material coherence defect. |
| Meaningful interactivity | 8 | Real matching decisions, target scope, range calculations, named joint alternatives, dependency detail and browser/CLI packet checks work. Chapter continuity is incomplete. |
| Motion quality | 6 | Selection/reading transitions are restrained; actual small-screen selection initiated document scrolling rather than numeric count-up fiction. No timed visual analysis or OS reduced-motion test was completed; source presence alone is not a runtime pass. |
| Responsiveness | 6 | Desktop and tablet composition were inspected;900px stacks the note below the register rather than keeping a miniature side column.391px DOM has no page overflow and chapter labels measured12px. Mobile visual capture was defective and320px unrun, so this is provisional. |
| Accessibility | 7 | Real Archive Escape/focus return, native inputs/buttons, row-specific controls, local error description and textual statuses were observed. Missing invalid-state semantics, a source-row accessible-name error and untested screen-reader/touch/reduced-motion paths prevent a stronger score. |
| Product identity | 8 | Source records, supplied-price boundary, annotated calculations and honest reference provenance determine the surface. The source→proof mismatch currently interrupts the product's central promise. |
| Overall | 7 | A substantial product-specific redesign with working numerical/evidence paths, but bounded correctness/contrast fixes and reliable mobile/second-cycle validation are still required. |

## Raw captures

- `critic/cycle1-01-desktop-entry.jpg` — real1440×960 CSS entry state; raw backend image has additional area/scaling.
- `critic/cycle1-02-source-decisions.jpg` — source decisions/excluded row; captured before the implementer's source-toolbar fix reload, so do not use this to claim the current search field is still collapsed.
- `critic/cycle1-03-desktop-ledger.jpg` — real loaded ledger, finding/scope hierarchy and weak primary export-link text contrast.
- `critic/cycle1-04-packet-verified.jpg` — actual browser verification result and disclosure, with download-link contrast visible.
- `critic/cycle1-05-tablet-entry.jpg` — measured900×800 CSS entry; raw supported screenshot clip, backend-scaled.
- `critic/cycle1-06-tablet-selected-note.jpg` — tablet ledger state; filename describes the selection, **not** a claim that the below-table note is in the visible crop.
- `critic/cycle1-07-mobile391-note.jpg` — defective tiled capture, retained as evidence of the capture limitation. **Do not publish it as a clean product screenshot.**

Cycle 1 is complete as a bounded review. Cycle 2 must retest the fixes, capture reliable actual mobile/320px views, exercise new tool-tab keyboard behavior and the legacy bridge, and state any remaining NOT_RUN gates honestly.
