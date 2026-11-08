# Frontend transformation evidence

Implemented 2026-11-03 in `web/index.html`, `web/styles.css`, `web/app.js`, `web/scenario.js`, `web/format.js`, and `tests/test_format.mjs`.

## Delivered behavior

- A finding dialog opens the assumption editor on its exact source row. The general entry supports every source row through the authenticated source endpoint, including older saved runs.
- Exactly one quantity, billed unit price, or contract price can be proposed. The editor shows the original row's quantity and both prices, the original selected value, and the proposed value explicitly marked unexecuted. Same-value changes are rejected locally; the server remains authoritative.
- Scenario execution inherits the original mode. A verified result shows original/scenario variance, exact signed change, changed-row variance, billed totals, flagged counts, unchanged records, and mode. Zeroed findings remain visible in the comparison.
- Original receipt, scenario receipt, and portable comparison packet are downloadable. Receipt identities are inspectable. Scenario results are labeled hypothetical and make no savings, correction, liability or execution-attestation claim.
- Another alternative starts from the original baseline; a scenario cannot open the assumption editor.
- Saved reviews restore their actual receipt CSV, review context, and mode. Changing CSV/context/mode marks the visible result previous, adds an explicit warning above the figures, disables assumption actions, and labels the old receipt. Reopening restores the exact saved inputs.
- Fixed task framing replaces open-ended investigation promises. Optional context is limited to 600 characters in HTML and client validation.
- Unconfigured inference and unavailable Docker modes are disabled with visible reasons. Main submission respects readiness. Vultr-only operator token stays request-scoped.
- Mobile navigation and recent runs remain available in a native disclosure. Programmatic scrolling observes reduced-motion preference.
- Enlarged body/supporting typography, deliberate comparison hierarchy, and responsive layout retain the cream/green visual identity.

## Actual checks

| Check | Outcome |
|---|---|
| `node --test tests/test_format.mjs` | PASS, 6 tests; signed, zero, malformed and above-safe-integer exact cent values |
| `node --check web/app.js`; `node --check web/scenario.js` | PASS |
| `git diff --check -- web tests/test_format.mjs` | PASS; only Git CRLF normalization notice |
| Browser synthetic reference original → finding INV-2402 → contract72→80 → comparison | PASS; baseline `7ebebed8-8d9c-40ca-ab63-716b8d2e8407`, scenario `c8941887-497b-45f7-b9e0-87474a6460e9`;1480→1160,−320;row520→200;23unchanged |
| Browser comparison packet download | PASS; copied actual download to `frontend/reference-comparison.json` |
| `.venv/Scripts/python.exe scripts/verify_receipt.py artifacts/optimization-review/frontend/reference-comparison.json` | PASS; both hashes/arithmetic, parent identity, single change, same mode, every signed delta |
| Older saved Docker baseline → contract72→85 scenario | PASS; baseline `a4876303-267d-4da4-b15b-3d431f1719fa`, scenario `53b6776d-4c50-47fd-9689-a741fe485e8d`;1480→960,−520;changed row520→0 remains explicit;6→5flags;actualDocker elapsed1555.03ms and cleanup confirmed |
| Return to baseline | PASS; original1480 and original72 restored |
| CSV, context, and mode changed after review | PASS independently; stale warning and disabled assumption action; reopen clears mismatch |
| 600-character bound | HTMLmaxlength600 and clientguard inspected; read actualDOMattribute600. Boundary submit not executed in this implementation check |
| Mobile390px history open, prior run, finding modal, comparison | PASS observed through actual browser actions and screenshots |
| Mobile320px initial collapsed history disclosure → expand → saved run | PASS; capabilities remain available |
| 320px comparison horizontal overflow | PASS; actualDOM scrollwidth305 equals clientwidth305 (scrollbarexcluded) |
| Browser console | No warning/error entries observed in captured window |

Screenshots: `frontend/reference-comparison.png`, `frontend/mobile-source.png`, `frontend/mobile-comparison.png`, `frontend/stale-context.png`. The stale-context shot is scrolled below the top warning; its disabled action is visible. Accessibility evidence separately confirmed the warning, and a subsequent refinement adds another warning immediately above figures.

Temporary browser viewport reset and implementation tab closed. Synthetic browser test runs remain in ordinary local history. No live Vultr, paid action, cloud deploy, native file-picker/drag-drop, full screen reader/contrast audit, or runtime OS reduced-motion emulation was performed by this implementation agent. Independent UX review follows separately.
