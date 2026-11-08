# Workbench v3 — independent design / browser cycle 2

Review date: 2026-11-04, Asia/Qyzylorda. Local target: `http://127.0.0.1:8765/`. Reviewer owned this report and screenshots only; no application source was changed. Cycle 2 initially exercised the shared working tree. The final endpoint retest and native desktop captures followed a reload of frozen source commit **0342f5c**. This report distinguishes those browser observations from other agents' backend and VM tests.

## Verdict

**Pass for the reviewed reference-mode journey; no material new browser/design blocker found.** The cycle-1 mobile readability defect is fixed and visually verified at measured 400 and 320 CSS px widths. Import, source reconciliation, immutable baseline, two interacting ranges, three named alternatives, evidence, downloaded-packet verification, history and the preserved legacy path were exercised in the real browser across the two cycles.

This is a substantive workspace transformation: an unresolved source decision can be followed into a baseline row, a shared contract assumption, a joint alternative and a downloadable evidence packet. The desktop overview and adjacent inspector support review without repeated navigation. Explore distinguishes a trusted range estimate from an executed alternative, and verification discloses that uploaded source data goes to the server. These distinctions materially improve the product's credibility.

The verdict does not certify live model execution, cloud integration, full accessibility compliance, asynchronous file-read race ordering in a browser, or a production security posture. Those limits are explicit below.

## Browser and viewport evidence

The dedicated Chrome extension tab from cycle 1 was reused; its local URL was verified. No native fallback, terminal-driven browser, user-existing tab or unsupported browser instrumentation was used. The direct IAB attempt had been unavailable in cycle 1. This reviewer closed only the dedicated review tab after resetting the temporary viewport override.

| Documented capability request | Actual read-only DOM measurement | Result |
|---|---|---|
| 1080 × 675 | 1440 × 900 CSS px; DPR approximately 0.75 | Desktop review |
| 300 × 630 | 400 × 840 CSS px; document scrollWidth 380 | Mobile fixed chart and error/history checks; no page overflow |
| 240 × 630 | 320 × 840 CSS px; document scrollWidth 300 | Narrow mobile chart; no page overflow |
| Viewport reset | **1762 × 1175 CSS px; DPR 1.125; document scrollWidth 1741** | Final clean native Explore and Overview captures, scrollY 0 |

The calibrated-viewport screenshots retain blank backing-surface padding returned by the browser. They have not been cropped, composited or reconstructed. Their filenames record measured CSS viewports, not JPEG pixel dimensions. The final native screenshots have no such blank outer padding and are suitable as product previews.

## Actual cycle-2 functional trace

Saved reviewer case: `f1d79ae5-5272-41d2-8d7a-88051be8079a`, `Design audit cycle 1 — synthetic`. The selected C2R contract and source-row-7 exclusion from cycle 1 remain attached. Baseline remains **768.00 variance / 7110.00 billed / 7 of 8 included / 5 flagged**. Its three alternatives remain **368.00**, **568.00**, and **148.00**. The joint alternative changes C1 to 80 and normalized row 2 quantity to 80; the shared contract propagates across three distinct rows.

| Check | Actual interaction and observed result |
|---|---|
| Two interacting ranges | Retained C1 **65..85**, added normalized row 2 quantity **20..80**. Browser shows exact joint total **148.00..1993.00**, width **1845.00**, original 768.00. |
| One-at-a-time effects | C1 endpoints **1193.00 / 148.00**, span1045, 3 rows. Quantity endpoints **508.00 / 1288.00**, span780, 1 row. The chart explains that endpoint effects cannot be added to calculate joint changes. |
| Evidence priority | C1 guaranteed width reduction **645.00**, possible **1845.00**. Quantity guaranteed **0.00**, possible **1200.00**. Strict leader is not certified; minimum pairwise margin −96.00, nearest challenger INV503. |
| Mobile target activation | Activated the C1 HTML chart button with Enter. Assumption target became C1; low65/high85 appeared; focus moved to the range selector. |
| Invalid mobile range | Submitted C1 low90/high85. Visible alert: range must include the original and low must not exceed high. Existing saved148..1993 analysis remained visible. Correcting low65 and updating cleared the alert and preserved the result. This accepted resubmission advanced the case from revision6 to revision7 without changing its assumptions. |
| Actual invoice/contract upload | Used browser file chooser for `D:/projects/vultre/examples/case-invoices.csv` (682 bytes) and `case-contracts.csv` (281 bytes). Match returned8total/6exact/2unresolved. |
| Source edit invalidation | Selected C2R, then edited INV501's vendor from `Atlas` to `atlas` in the invoice textarea. Old matching workspace and create-baseline action disappeared immediately. Rematch returned5exact/0selected/3unresolved, including lowercase-atlas mismatch and the old C2R ambiguity. No stale manual match survived. |
| Malformed-source recovery | Changed the invoice header from `invoice_id` to `unexpected_id`. A visible required-columns error appeared. Restoring the original text and matching recovered6exact/2unresolved. |
| Unsaved draft reset | Created an unexecuted alternative draft named `Unexecuted audit draft` with C1=82. New case hid the old active-case views. After upload/edit checks, reopening the saved reviewer case from Recent cases showed an empty alternative name/change list and preserved both saved ranges. |
| Mobile history | Expanded Recent cases after a reload at400px and reopened the reviewer case. Its baseline,3alternatives and2ranges returned. |
| Source identity after exclusion | Evidence selection `INV507 · Meridian · normalized row 7` showed **invoice original row8**, C3 contract row5 and normalized row7. The excluded row does not silently renumber the original source identity. |
| Verification disclosure | Evidence states that the packet and included source data are uploaded to this server; no code executes; CLI is available for offline verification. |
| Final packet | Downloaded the real two-range packet, chose it through the browser file chooser and verified it. All6checks passed. CLI independently passed as recorded below. |
| Legacy preserved | Single CSV review → synthetic sample → Reference run returned **1480.00**,24rows/6flagged, billed34353.00. INV-2402/source3 displayed quantity40, billed85, contract72, variance520. Changing that contract assumption to80 and running comparison returned **1160.00**, delta−320.00,23unchanged. Downloaded comparison passed CLI verification. `← Case workbench` restored the saved v3 case and hid the legacy shell. |

Cycle 1 separately verified baseline creation, required exclusion reasons, all three alternative executions, real packet download, tampered-packet rejection, immediate removal of a stale verification success, restoration/reverification and targeted keyboard navigation. See `design-cycle1.md`; these are not invented repeat tests in cycle 2.

## Download and CLI evidence

Final two-range case download, saved at revision6 before the same-range recovery resubmission:

```powershell
.venv/Scripts/python.exe scripts/verify_receipt.py 'C:/Users/nural/Downloads/prooflane-case-f1d79ae5-5272-41d2-8d7a-88051be8079a (1).json'
```

Actual exit0, `passed: true`;3alternatives; counts8total/6matched/1selected/1excluded/0unresolved; bounds148.00..1993.00, width1845.00. Six checks passed: source reconciliation/exclusions; baseline receipt/source CSV; all alternative arithmetic/parent links; declared changes/shared-contract propagation; exact ranges/sensitivity/review priorities; case hash/all comparisons. The browser also showed6checksPASS after uploading this file. Hash verification does not authenticate the issuer, attest the runtime or establish the supplied contracts' truth.

Legacy baseline ID: `1b469e9b-ce55-49c1-bb85-a4a88532dfcc`. Legacy scenario ID: `c014dab8-8a3a-4b6c-978f-6d82feeeeffb`.

```powershell
.venv/Scripts/python.exe scripts/verify_receipt.py 'C:/Users/nural/Downloads/prooflane-comparison-c014dab8-8a3a-4b6c-978f-6d82feeeeffb.json'
```

Actual exit0, `passed: true`; five checks passed for receipt arithmetic, baseline identity, the one-cell change, same-mode comparison and all deltas. No extra model or sandbox execution was used for these reference flows.

## Finding disposition and visual assessment

**V3-D1 — Mobile chart text: fixed_verified.** At400 and320px, HTML cards replace the scaled SVG. Read-only computed typography is target14px, endpoint13px, span12px; the rendered screenshots confirm readable exact amounts. At400px the card width is approximately319.78px. The chart buttons remain keyboard operable and no page-level horizontal overflow was observed. Tables retain intentional internal scrolling.

The final frozen-source endpoint retest at400px also verifies the legend semantics. C1 has hollow left/high-input and filled right/low-input endpoints because price increases reduce variance. Quantity has filled left/low-input and hollow right/high-input endpoints. Both cards retain exact printed totals, so meaning is not conveyed by color alone. Final screenshot `07-final-endpoints-400x840.jpg` shows both bars and visible keyboard focus.

**V3-D2 — Long case title in the rail: fixed_verified**, preserved from cycle1. Native final screenshots show title truncation without a horizontal rail scrollbar; the full accessible title remains available.

No new medium/high visual defect was found. There is minor copy polish remaining (`1 rows`, `1 explicit selections`); it does not obscure scope or arithmetic. The legacy shell retains its older visual density and a cosmetic history-rail overflow in the comparison capture. These are not claimed as transformed v3 layout defects or release blockers.

## Fresh screenshot inventory

All paths below are relative to `artifacts/transformation-review/design-v3/cycle2/`.

| File | What it proves |
|---|---|
| `01-fixed-chart-400x840.jpg` | Readable two-range HTML sensitivity cards at400CSSpx |
| `02-fixed-chart-320x840.jpg` | Narrow mobile card typography at320CSSpx |
| `03-two-range-desktop-1440x900.jpg` | Joint bounds and range/editor layout at measured desktop size |
| `04-uploaded-sources-desktop.jpg` | Actual local invoice/contract file selection and matching |
| `05-legacy-comparison.jpg` | Preserved1480→1160 legacy comparison |
| `06-source-dependency-desktop.jpg` | Original-row vs normalized-row evidence mapping |
| `07-final-endpoints-400x840.jpg` | Frozen-source endpoint directions, exact values and focus visibility |
| `08-native-explore-1762x1175.jpg` | Clean native desktop Explore preview;2ranges, evidence priority and provenance |
| `09-native-overview-1762x1175.jpg` | Clean native overview preview;768/7110/7of8 and adjacent source inspector |

## Proof limits

- Runtime reduced-motion emulation is **NOT_RUN**. The documented browser exposes viewport and management capabilities, and the tab exposes pageAssets; no media-emulation capability was available. Live `prefers-reduced-motion: reduce` was false. Source-level review found the reduce-motion CSS override in `web/styles.css` and `web/workbench.css`, plus auto/smooth selection in `web/workbench.js`. This is code verification, not a runtime claim.
- Actual file chooser, normal file reads, source edits, paste, new-case/history draft reset and matching recovery were tested. The independently reported out-of-order file-read race and request-token fix were **not reproduced with concurrent reads in this browser**. Engineering's VM ordering tests remain separate evidence.
- Keyboard checks are targeted, not a full keyboard-only journey. No screen-reader audit, formal contrast measurement,200%zoom audit or physical-touch-device test was performed.
- Three alternatives and a two-target joint alternative were exercised. The12-change limit and broader combination space were not browser stress-tested here.
- No live cloud/model calls, sandbox execution, containment probes, provisioning, payments or external publication occurred. Backend test totals from other agents are not included as this reviewer's browser proof.
- The native screenshot viewport was reset and the review tab closed. User-existing tabs were left untouched. No further browser work is in progress.
