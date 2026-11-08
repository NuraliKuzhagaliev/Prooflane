# Audit Folio — frontend implementation evidence

Date: 5 November 2026. Implementer owned only frontend code and the focused navigation tests. Root owns fonts, licenses, backend, integration and browser verification. App ownership was released after the initial coherent implementation and the first observed toolbar correction; no browser interaction was performed by this implementer.

## What changed

- Replaced the permanent rail and duplicate tab navigation with one numbered chapter spine: Sources, Ledger, Assumptions, Proof. Case history moved into a native Archive dialog with close/Escape behavior and focus return.
- Rebuilt the entry as two facing, ruled source registers. Upload/paste and reconciliation are the first work surface; no decorative hero or financial placeholder values were added.
- Changed the loaded conclusion hierarchy from four equal metric cards to a primary variance statement, a separate scope annotation and a subordinate bookkeeping line. Included and excluded scope remains explicit.
- Styled invoice/contract source decisions and ledger rows as a register beside an annotation margin. The selected invoice can carry its row identity to assumptions and proof. Returning from Proof synchronizes the ledger selection with the inspected row.
- Split Assumptions into Ranges and Executed alternatives so a long range list cannot bury the alternative workflow. The original completed baseline is a shared anchor above both tools; saved analysis and draft changes remain independent of tab selection.
- Used actual returned sensitivity endpoints in keyboard-operable ruled tracks. Exact printed amounts remain authoritative. Low/high endpoint direction is preserved, including the reverse price relationship. No monetary count-up animation or invented points were introduced.
- Reframed Proof as a source-to-receipt chain and export record. Existing server-upload disclosure, runtime provenance, code, receipt and packet verification remain visible in relevant disclosure sections.
- Applied the same document geometry to the retained single-file workflow: its former permanent sidebar is an optional history disclosure; old event and ID contracts are preserved.

Typography uses the root-provided same-origin Newsreader and IBM Plex Mono regular files, with system sans for controls. Font faces use swap. Neutral paper, ink rules and oxblood annotation replace the blue component lattice; no decorative gradients or shadows were added. Selection motion is limited to the annotation, and busy motion represents an actual pending request. The reduced-motion media rule removes both.

## Files changed by implementer

`web/index.html`, `web/workbench.css`, `web/workbench.js`, `tests/test_studio.mjs`.

No backend, provider, database, stored user data or runtime dependency was changed. Existing `app.js`, `scenario.js`, `styles.css`, model/format modules and all legacy event names remain intact. Fonts and licensing were handled separately by root.

## Actual checks

```powershell
node --check web/workbench.js
node --check web/app.js
node --check web/scenario.js
node --test tests/test_format.mjs tests/test_workbench.mjs tests/test_studio.mjs
node artifacts/transformation-review/principal-ui-probe.mjs
```

- 14 Node tests PASS: 12 existing formatting/model cases and two new tests executing the actual navigation/modal functions with a controlled DOM boundary.
- The existing independent source-function race/failure probe exits0 with all groups passing. Its output is saved in `artifacts/design-studio/async-regression.json`.
- Static check: all237 original IDs retained,249 unique IDs after the additions, no missing direct workbench ID references, UTF-8 title/CSV labels intact. `frontend-static.json` records file sizes and scope.

The new tests verify that switching assumption tools exposes one panel/one roving tab while preserving the saved analysis and unexecuted changes; the modal test verifies that a busy request cannot be interrupted and that the opener is captured before native modal focus. They do not claim a real keyboard/browser test.

## Failures and corrections retained in the work record

A large initial stylesheet write exceeded the Windows command-length limit before execution. The complete stylesheet was written in smaller operations; no partial success was claimed.

A subsequent HTML transform accidentally used the Windows default cp1251 read encoding before writing UTF-8. Root observed mojibake in the actual page title and labels. The one known decode pass was reversed; subsequent file reads/writes explicitly use UTF-8. The expected title and CSV label are asserted, and root was asked to reload. This issue affected HTML; the JavaScript transformation used explicit UTF-8 throughout.

Root then observed the source search shrinking while the filter stretched. The toolbar received explicit flex sizing and min-width rules for its search field and a bounded filter width at desktop/mobile sizes. This correction awaits the root/critic's actual render retest; it is not self-certified by the CSS change.

## Remaining review boundary

Real desktop/tablet/mobile screenshots, keyboard/touch operation, file chooser, actual requests, packet downloads and legacy end-to-end checks belong to root/independent critic. No such run is claimed here. Runtime reduced-motion preference and complete accessibility compliance are not proven by the media rule.

A specific self-review candidate sent to root: essential mobile assumption/primary chapter labels were initially too small in the first CSS iteration (10–11px); increase them to at least12px and use stacked ordinals if320px width requires it. Root owns this next correction after handoff. A second candidate is progressive disclosure of the source spread after matching so the decision queue is not unnecessarily displaced below it.
