# Independent final UX review — cycle 2

Date: 2026-11-03. Target: restarted local server at http://127.0.0.1:8765/. Separate temporary Chrome tab; the user's in-app browser tab was not touched. Product source was read only. This cycle began after source freeze and the context-copy fix.

## Result

**PASS for the exercised local workflow. No new product defect reproduced.** The remaining P3 copy mismatch from cycle1 is fixed: the context placeholder now reads **Save context with this review; the calculation stays the same.**

The independent walkthrough used real native file selection and a fresh local Docker baseline/scenario after the server restart. It did not rely on the sample button, a fabricated response or a prior run to demonstrate execution. Inference and cloud deployment remain outside this result.

## Actual walkthrough

1. Opened the file picker through the visible upload control and selected `examples/evaluation/invalid-price-precision.csv` using the documented file-chooser API. The application displayed its filename and119-byte size.
2. Submitted reference mode. The application rejected the data with **Record 2: unit_price must be nonnegative USD with at most 2 decimals.** The invalid row contains `1.001`, so the error identifies both location and rule accurately.
3. Opened the native file picker again and selected `examples/invoices.csv`, containing the fictional invoices. The old error cleared and the new filename/1,428-byte size appeared.
4. Selected **Sandbox recipe**, added context `Final independent UX audit — uploaded synthetic example.`, and ran the review. Baseline `c85dc3c4-38e1-4ea9-93ae-815927d1bb7d` returned verified: 24 rows, 6 findings, $1,480 variance and $34,353 billed. The actual execution record reported Docker, exit0 and confirmed cleanup.
5. Opened INV-2402/source row3. The dialog displayed quantity40, billed85, contract72 and `(85−72)×40 = 520`. Escape returned focus to the initiating invoice button. Reopened the dialog and chose **Test an assumption on this row**; row3 was selected and Proposed value received focus.
6. Entered80 and ran the separate scenario. Run `ea30e302-dafc-4d35-84a6-6966d417b1e7` showed original1480 → scenario1160, change−320; changed row520→200; 23 unchanged records; both execution modes sandbox. The scenario remains explicitly hypothetical, with the original preserved.
7. Downloaded the comparison packet through its real browser download link. **Return to original baseline** restored the original run ID, $1,480, uploaded CSV and exact saved review context.
8. At measured mobile CSS391×844, opened the new comparison from recent-run history. The same new scenario ID and1480→1160/−320 figures appeared. Navigation and history remain available. The history disclosure closed on click and reopened with Enter.
9. The Execution & trust link changed the browser hash to `#trust-boundary`. No live inference request was sent. The unavailable Vultr option remained disabled with its configuration explanation.

## Download verification

Downloaded artifact copied without modification to:

`artifacts/optimization-review/ux-cycle2/comparison-uploaded-invoices.json`

Command:

```text
.venv/Scripts/python.exe scripts/verify_receipt.py artifacts/optimization-review/ux-cycle2/comparison-uploaded-invoices.json
```

Observed exit0, `passed:true` for:

- Both receipt hashes and arithmetic.
- Baseline identity and hash.
- Exactly one declared source assumption.
- Same execution mode.
- Every signed delta.

Verified baseline receipt hash: `552bdb38cfe133a2bdd69f26ff4e86851070785127853ffc56ee546708c90ee8`.

Verified scenario receipt hash: `392607cbed1f80178e825626de59b66c4918e9d71f554b15d2e9f199ab740830`.

The verifier's scope remains artifact integrity and arithmetic, not authentication of issuer/runtime or truth of the assumption.

## Visual evidence

- `ux-cycle2/desktop-comparison.jpg` is the clearest desktop result capture. It includes source identity, hypothetical status, before/after totals, signed delta, row effect and packet action. The measured CSS viewport was1440×960. The browser screenshot backend adds scaled blank margins, so the raw image pixel dimensions differ from that viewport.
- `ux-cycle2/desktop-comparison.png` is an additional screenshot-clip capture of comparison facts and download; the capture starts below the panel heading and should not be the lead image.
- `ux-cycle2/mobile-history.jpg` shows available mobile navigation and scrollable recent runs.
- `ux-cycle2/mobile-comparison-full.png` shows the entire real mobile comparison and evidence flow. Measured CSS viewport391×844 with document scrollWidth371 plus the20px browser scrollbar; no horizontal page overflow. The difference from requested390px comes from preserving Chrome's75% zoom and the viewport tool's integer dimensions.

The full-page screenshot backend displays a skip-link overlay during capture, as in cycle1. This is not claimed as a new product defect; prior read-only inspection confirmed the unfocused skip link is positioned outside the viewport. No DOM/style mutation or image fabrication was used to produce these screenshots.

The comparison hierarchy is clear: named assumption, original/result figures, signed change, supporting facts, scope statement and downloads. The unchanged original is reachable directly. The narrow layout preserves these actions and labels without replacing them with an unavailable mobile subset.

## Frozen source identities

SHA-256 as read during this cycle:

| File | SHA-256 |
|---|---|
| web/index.html | `1BDD13C19A456C57523C013285D407E085575F04ECF73AEEAD42596ACC3E08A0` |
| web/app.js | `E439DD4DC9C90213CABA50725298CD8459AC6E587005AC76DAAC4253B353BF7C` |
| web/scenario.js | `4FC5B0BA7D7451373C30F9A4F3A1480DA7758063D59AA818CEE1A4EEA2BB64DF` |
| web/styles.css | `EC7BA263DDDEA65CB8001BABED2679DDEAA8A7454DBD0907CEF13AE975D1DBD8` |

## Limits and cleanup

- Browser console error/warning collection returned `[]` during this cycle.
- Native file selection, invalid-input recovery, real fixed-Docker execution, source inspection, assumption execution, comparison download/verification, return/history, mobile disclosure and keyboard Escape/focus were actually exercised.
- Cycle1 separately checked stale CSV/context/mode binding,600/601-character boundaries, no-op assumption rejection and a changed row reaching zero. Those observations are recorded in `ux-cycle1.md`; they are not represented as fresh cycle2 tests.
- Live VSI, Vultr VM deployment, drag/drop, OS reduced-motion preference toggling, comprehensive contrast measurement and full screen-reader traversal were not run. Reduced-motion handling was source-checked in cycle1.
- Temporary viewport override reset and temporary audit tab closed. Existing user tabs and history were not deleted or modified. The synthetic local audit runs remain in ordinary application history.
