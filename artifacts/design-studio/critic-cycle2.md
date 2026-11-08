# Audit Folio — independent cycle 2 review

Date: 2026-11-05, Asia/Qyzylorda. Reviewer: Design Critic + QA. This reviewer owns this report only and made no application changes. Cycle 1 observations remain historical evidence in `critic-cycle1.md`.

## Verdict

**The selected Audit Folio concept is fulfilled in the reviewed implementation.** The current interface has one document spine, ruled registers, a finding with an adjacent scope annotation, and a selected-record margin. Source identity now connects into Proof, including an explicit exclusion record. The actual320px and390px captures show deliberate narrow-screen compositions rather than a scaled desktop dashboard. No additional material defect was found in the bounded evidence inspected for this cycle.

This is not the old generic SaaS rail/card frame with new colors. Its familiar table/detail mechanics are appropriate to invoice review. Product identity comes from source decisions, original/normalized references, the preserved baseline and its evidence path. It does not depend on decorative paper, a large marketing cover, invented graph relationships or a collection of equal metric cards.

The outcome supports a good completed redesign, not a10/10 claim or a completed accessibility certification. Motion and accessibility retain specific testing limits below.

## Who performed what

**This reviewer's own cycle 1:** operated the real Chrome application through CUA, resolved the fictional source ambiguity/exclusion, ran reference baseline768/7110/7of8, ranges148..1993, alternatives368/568, and verified the actual downloaded case packet in browser and CLI. Reproduced the included/excluded source→Proof failures and the contrast problem. That browser later became unavailable; the tiled mobile capture and unrun320px check were explicitly not accepted as successful visual evidence.

**Root's actual cycle 2, reported to the reviewer:** used a newly available in-app browser through CUA against localhost. Created case `374834a3-9900-43e7-b406-543ff8c48be8`; observed baseline768/7110/7of8; retested original invoice8→normalized7 for INV507; retested excluded INV506/source7 as no calculated amount; repeated two-range148..1993 and invalid-range recovery; checked Archive Escape/focus return; ran legacy1480→1160, delta−320 and return to the preserved case. Root measured desktop1440×1100, tablet900×1000, mobile390×844 and320×844. Reported document scroll widths1425/885/375/305 respectively fit the scrollbar-reduced client areas. Root also reported actual export download, byte-for-byte preservation in `browser-case-cycle2.json`, and a successful CLI check.

**This reviewer's independent cycle 2 work:** opened and visually inspected all six raw JPEG files listed below with the image-viewing tool; read current source for the four fixes, source disclosure and mobile labels; read the saved16-test Node result and packet-verification artifact; independently ran the existing CLI checker against `browser-case-cycle2.json`. **I did not operate the second browser** and do not present root's interactions as my own. Static images cannot establish focus behavior, timing, keyboard action or absence of every possible responsive failure.

## Actual image review

| Raw file | What is directly visible | Assessment |
|---|---|---|
| `cycle2-desktop1440.jpg` | Loaded ledger with768,7/8scope, subordinate billed/mode line, one chapter spine, broad register and INV507 margin note. Export text is light on oxblood. | Coherent document hierarchy, with no persistent rail or card grid. The note separates original source8, C3row5 and normalized7. Moderate JPEG softness limits tiny-text scrutiny. |
| `cycle2-tablet900.jpg` | Case title wraps, chapter navigation remains a single line, finding/scope retain distinct hierarchy and register uses full available width. | The wide desktop margin does not become an illegibly narrow column. This crop does not show the lower selected note, so its placement is supported by source/cycle1 geometry, not claimed from this crop. Moderate JPEG softness is a capture property. |
| `cycle2-mobile390.jpg` | Two real assumption tools with wrapped names; joint148..1993 interval; C1 and INV501 quantity sensitivity with exact endpoint amounts and low/high marker legend. | Clean, legible mobile data representation. Selected C1 has an annotation rule/background, while other tracks remain quiet. This is a selection state, not a return to repeated dashboard cards. Printed exact amounts prevent dependence on chart geometry or hover. |
| `cycle2-mobile320.jpg` | Wordmark and utilities wrap into an intentional header; long case title wraps; scope/mode remain explicit; export link wraps without clipping; numbered chapters use four columns; ledger heading, action and768 remain readable. | A deliberate document sequence, with readable controls. At this narrow width the source register follows below the first screen; that is a space tradeoff rather than accidental desktop shrinking. The capture is clean and does not have cycle1's tiling. |
| `cycle2-exclusion-desktop.jpg` | “INV506 / outside the calculated scope,” original source7, stated reason, “No contract price applied,” “Not calculated; excluded.” Packet disclosure remains alongside it. | The former silent stale-row behavior now has a truthful exclusion surface. No zero or unrelated invoice amount is substituted for an excluded calculation. Moderate capture softness limits fine type inspection. |
| `cycle2-legacy.jpg` | Original1480→scenario1160, delta−320, reference/fixed-rule provenance, download comparison control and retained single-CSV review. | The legacy comparison is visibly functional and remains distinct from the newer multi-source case. This image alone does not prove the download was activated or checked. |

These are real root-generated captures of the implemented local application. They are not concept drawings and were not edited by this reviewer. Differences in revision/range counts between them represent different tested states, not a claim that all six images are one simultaneous state.

## Resolution of cycle 1 findings

| Cycle1 recommendation | Current source and independent evidence | Status |
|---|---|---|
| Included and excluded source continuity | `sourceFocus()` looks up the original invoice record and its actual binding; it returns source8→normalized7 and returns an excluded identity without inventing a calculation row. `selectSourceRecord()` carries this into Proof. The explicit Source→Proof action uses the same function. Root reported real retest; exclusion image shows the new state. | **Resolved within the reviewed scope.** Root performed the behavioral retest; this reviewer corroborated source and actual output images. |
| Primary anchor contrast | `.folio-shell a.wb-primary` now explicitly uses the light sheet color, resolving the previous selector specificity problem. Root reported actual computed RGB255/253/249 on127/38/49. Light export/download text is directly visible in the desktop and exclusion captures. | **Resolved.** No whole-interface contrast/compliance claim follows from fixing these links. |
| Range field invalid state | `saveBound()` writes `aria-invalid` on both range controls from validation and clears it on a valid submission. Existing local error description and saved calculation remain. Root reported invalidtrue and correctedfalse with148..1993 preserved. | **Resolved for the reported invalid→valid submission route.** Full assistive-technology behavior was not tested. |
| Inspect source-row accessible identity | Current action name explicitly obtains original invoice row from `bindingFor(row.row)` and separately names normalized row. For INV507 that is8and7, rather than incorrectly calling normalized7 a source row. The margin note visibly has the correct distinction. Root reported real accessible-name retest. | **Resolved within the reviewed scope.** Source-binding test result is supporting evidence, not a substitute for root's browser observation. |

Two additional bounded improvements are justified by the existing work. The source-file spread now collapses after reconciliation so the decision queue is not repeatedly displaced by unchanged inputs; clearing/editing sources reopens it. Essential narrow-screen tool/chapter labels use12px and wrap instead of shrinking. I reviewed their source; the mobile tool/chapter readability is also visible in the clean captures. I did not independently operate the new source-spread disclosure in cycle2.

The remaining cycle1 proposals to restore cards, recombine all analytical tools or add a decorative zero-range state were correctly declined. They do not resolve an observed task failure. No additional feature expansion is requested by this review.

## Functional and automated evidence

I independently ran:

```powershell
.venv/Scripts/python.exe scripts/verify_receipt.py artifacts/design-studio/browser-case-cycle2.json
```

Result: exit0, `passed:true`, case `374834a3-9900-43e7-b406-543ff8c48be8`, source counts8total/6matched/1selected/1excluded/0unresolved; interval148..1993, width1845. All six verifier groups passed. **This packet has0alternatives.** Its alternative check group must not be advertised as a fresh two-alternative cycle2 test. The independently operated cycle1 packet had2alternatives and passed after the actual368/568 executions. This CLI check establishes the provided artifact's consistency, not an independent attestation that its bytes came from a particular runtime; the cycle2 browser-download origin is root's evidence.

I read `js-cycle2.txt`:16tests pass, including source identity after a preceding exclusion, missing-binding refusal, navigation/modal boundaries and the existing formatting/model cases. This reviewer did not rerun that Node suite. Root reported the existing async/failure probe passed and the155-test Python suite passed earlier; neither is relabeled as my independent test execution or as proof of current cloud access.

Root's cycle2 report and the legacy image support1480→1160/−320and return preserving the new case. A legacy comparison-packet download/check is not claimed from that image. Actual multi-source case export/check is separately evidenced above.

## Final subjective scores,1–10

Scores are professional judgments grounded in the observations above. They are not measured user-study results. Higher cycle2scores reflect resolved coherence and legibility gates, not a requirement to increase every score.

| Dimension | Score | Observable basis |
|---|---:|---|
| Originality | **8** | The document spine, ruled source register, scope annotation and selected-record margin establish a product-specific structure. This does not claim a new invention in table/detail interfaces. |
| Art direction | **8** | Paper/ink/oxblood, crisp rules and a consistent editorial system extend across sources, ledger, sensitivity and proof. Corrected export text resolves the prominent cycle1 finish defect. No faux stamps/textures or decorative gradients are needed. |
| Typography and composition | **8** | Expressive result/headings, mono references and neutral controls carry distinct jobs. Clean320/390captures demonstrate real wrapping and readable core labels. Desktop/tablet JPEG softness and untested extreme-length values limit any perfect-finish claim. |
| UX clarity | **8** | Explicit exclusions, original/normalized references, scope beside finding, fixed original and separate range/alternative states match the review task. Source→Proof now preserves the identity or explicitly explains exclusion. |
| Meaningful interactivity | **8** | This reviewer's cycle1 operated real source decisions, exact shared/joint assumptions and packet checks. Root's cycle2retimed the corrected continuity, range recovery and legacy bridge. No fake chart interaction or invented execution result is used. |
| Motion quality | **6** | Motion is scoped to selection annotation, real pending work and reading transitions; no amount count-up implies false intermediate results. Still images cannot prove timing, perceived smoothness or reduced-motion runtime behavior. Score remains bounded rather than crediting CSS alone. |
| Responsiveness | **8** | Actual1440/900/390/320layouts, root's measured geometry and clean mobile captures support deliberate reflow.390sensitivity exposes exact values;320chapter ordinals stack. This does not establish every device, zoom level or large-source state. |
| Accessibility | **7** | Observed Archive Escape/focus return, native control semantics, textual states, local described errors and corrected invalid/source-identity semantics are substantive. Full screen-reader, touch hardware and runtime reduced-motion checks remain unperformed. There is no blanket WCAG claim. |
| Product identity | **8** | Source reconciliation, preserved original, explicit scope and a receipt-linked paper trail determine the layout and interaction. The exclusion record strengthens identity by showing a boundary rather than styling a trust claim. |
| Overall | **8** | A coherent, materially different interface with independently exercised core paths, bounded corrections and honest provenance. Remaining limits affect evaluation completeness rather than demonstrating an additional material defect. |

## Remaining limits

- This independent reviewer did not operate the second browser; cycle2behavioral statements above remain attributed to root, with image/source/CLI corroboration explicitly distinguished.
- Full screen-reader operation, touch hardware, OS reduced-motion switching and a timed motion recording remain NOT_RUN. Roving tool-tab Arrow/Home/End behavior has focused automated evidence, but no actual cycle2keyboard sequence was supplied to this reviewer.
- The six images do not expose every mobile table column, all24ranges, all4alternatives,500source rows or every error state. Mobile contained table-scroll discoverability is therefore not independently closed by this image set. No page overflow was reported at the four measured widths.
- The legacy download control is visible; this review does not infer activation/verification from its presence.
- No live model, Docker-generated-code execution or Vultr integration was tested in these UI cycles. Reference provenance remains explicit. Cloud/model gates do not become PASS through design review.

No further application edits are requested by this bounded second review. The preserved reports, raw captures and actual packet artifacts make the result reviewable while keeping those limits visible.

## Late evidence reported by root

After this report was completed, root supplied additional actual-browser observations through CUA. This reviewer did not operate that browser or independently repeat these actions:

- A malformed invoice header was rejected with the exact expected-column explanation. “Try the fictional review” restored8rows/2unresolved decisions.
- The new source-input disclosure collapsed after matching and reopened for editing.
- Root found that opening an archived case left an old sample message in the live announcement region. Root corrected the loaded-case announcement, reloaded and observed `#announcement` as “Saved case opened. 7 included invoices. Reference complete.” This closes that specific reported stale-announcement problem; it does not establish full screen-reader behavior.
- Actual keyboard operation of the assumption tools succeeded: ArrowRight selected/focused Executed alternatives with its panel visible; Home selected Ranges; End selected Executed alternatives; ArrowLeft returned to Ranges. Root reported the corresponding selected state and panel visibility for each step. Thus the earlier limit about no supplied actual tool-tab keyboard sequence is superseded by this attributed evidence; the distinction between root's operation and this reviewer's independent work remains.

These bounded observations strengthen error recovery, progressive disclosure and keyboard evidence. They do not change the scores or remove the limits on touch hardware, full screen-reader operation, reduced-motion runtime, large-source rendering, live model/Docker/Vultr execution or legacy comparison-packet download. Root explicitly confirmed that the legacy download was not performed in this cycle.
