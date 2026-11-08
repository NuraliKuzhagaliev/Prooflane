# Workbench v3 — independent design / browser cycle 1

Review date: 2026-11-04, Asia/Qyzylorda. Target: `http://127.0.0.1:8765/`. Reviewer changed no application source. Backend was restarted by the root agent to commit `b1bd9a4` during a safe pause; the same SQLite case survived. UI changes remained in the shared working tree, so this is a stateful review of the observed implementation, not a final immutable-revision sign-off.

## Verdict

The new interface is a substantive functional transformation. Separate contract matching, a scoped case baseline, shared-contract sensitivity, named joint alternatives, a dependency inspector and a verifiable case packet were exercised in the actual browser. The tested reference path produced the expected arithmetic and preserved provenance. It is no longer just the earlier upload-and-results page.

One reproducible mobile visual defect remains open in this cycle: SVG chart text becomes effectively unreadable when the complete chart is scaled into a phone viewport. The root agent reports a replacement mobile HTML chart; that fix is **not yet visually retested in this cycle**. Legacy, source-file race recovery, the two-range demonstration, 320 px width and final mobile retest are assigned to cycle 2.

## Browser access and viewport evidence

- A direct new IAB tab failed with `Browser is not available: iab`.
- Read-only inventory exposed Chrome extension browser 1. A new dedicated Chrome tab was created at the explicit local URL. Its title and URL were confirmed by the browser tool; screenshot capture succeeded. No blocked native fallback, native app automation, terminal-driven browser, or user-existing tab was used.
- A requested viewport of 1440 × 900 initially measured 1920 × 1200 CSS px because the browser reported devicePixelRatio ≈ 0.75. The documented viewport capability was calibrated once to 1080 × 675; read-only DOM measurement then confirmed **1440 × 900**.
- Mobile capability request 300 × 630 measured **400 × 840 CSS px**, devicePixelRatio ≈ 0.75. `document.documentElement.scrollWidth` was 380, below the 400 px viewport; no horizontal page overflow was observed. Data tables intentionally scroll inside their containers.
- Browser screenshot output includes unused padded area outside the overridden page viewport in some captures. Filenames identify the **measured CSS viewport**, not a claim that the JPEG itself has those pixel dimensions. Images were captured by the browser API, not rendered from source or reconstructed.

## Actual functional trace

Case: `f1d79ae5-5272-41d2-8d7a-88051be8079a`, named `Design audit cycle 1 — synthetic`.

| Step | Actual browser action | Observed result |
|---|---|---|
| Empty state | Open dedicated local tab | Two source slots, source/overview/explore/evidence navigation, disabled match action until inputs exist |
| Sample | Click `Use fictional sample` | 8 invoices; 6 exact matches; 2 unresolved; overlapping C2/C2R and unmatched Helix row visible |
| Match | Choose C2R for invoice source row 5 / INV504 | Explicitly selected state; one unresolved row remains |
| Error recovery | Attempt exclusion without a reason | Visible error requiring 3–200 characters; focus moved to reason field |
| Exclusion | Exclude invoice source row 7 / INV506 with `No eligible supplied contract; excluded from this review.` | 0 unresolved, 1 excluded; create-baseline action enabled for 7 rows |
| Reference baseline | Create named case | Positive variance **768.00**, total billed **7110.00**, 5 flagged, coverage **7/8**, exclusion scope explicit, `Reference complete` |
| Source trace | Inspect overview row INV501 | Invoice source 2 → C1 contract source 2 → normalized record 2; original quantity 40, billed 85, contract 72, variance 520 |
| Shared range | C1 low 65, high 85 | Joint total interval **148.00–1193.00**, width **1045.00**; shared target affects INV501, INV502, INV508 |
| Alternative 1 | `C1 negotiated price`, C1 = 80 | **368.00**, signed delta **−400.00**, Reference complete |
| Alternative 2 | `C1 price + larger quantity`, C1 = 80 and normalized row 2 quantity = 80 | **568.00**, signed delta **−200.00**; 3 distinct changed rows, jointly recalculated; billed 10510.00, delta +3400.00 |
| Alternative 3 | `C1 upper-bound price`, C1 = 85 | **148.00**, delta **−620.00**, 3 flagged; all three alternatives coexist with the original 768.00 baseline |
| Dependency explorer | Open Evidence | Invoice, contract, normalized row, baseline, alternatives and integrity nodes with selectable detail; full actual source facts exposed |
| Download | Click case packet download | Browser saved the real 27,424-byte packet shown below |
| Browser verification | Choose the downloaded JSON through file chooser and click Verify | Six checks pass, scope states no issuer authentication, runtime attestation or proof of contract truth |
| Tamper | Change packet `name` in pasted JSON without updating hash | Prior success disappears immediately; verification rejects the packet and states no code executed |
| Restore | Paste the unchanged original packet and verify | Verification passes again |
| History | Reload and reopen own case from Recent cases | Baseline, declared C1 range and three alternatives remain available; mobile history can be expanded |

Actual packet path: `C:/Users/nural/Downloads/prooflane-case-f1d79ae5-5272-41d2-8d7a-88051be8079a.json`.

Actual CLI command:

```powershell
.venv/Scripts/python.exe scripts/verify_receipt.py 'C:/Users/nural/Downloads/prooflane-case-f1d79ae5-5272-41d2-8d7a-88051be8079a.json'
```

Exit code 0, `passed: true`, 3 alternatives, counts total 8 / matched 6 / selected 1 / excluded 1 / unresolved 0. Range low 148.00, high 1193.00, width 1045.00. Checks passed: source reconciliation and explicit exclusions; baseline receipt/source CSV; all alternative arithmetic/parent links; declared changes/shared-contract propagation; exact ranges/sensitivity/review priorities; case hash/all comparisons.

The shared browser session contained another agent's earlier case. This reviewer created and used the separately named case above and did not count other agents' history entries as evidence.

## Findings and retests

### V3-D1 — Mobile sensitivity chart scales text below usable size

- Severity: medium. Dimension: visual usability / mobile. Confidence: high. Status: **open pending cycle-2 visual retest**.
- Location: mobile rendering of `#wb-tornado` in `web/workbench.js` / `web/workbench.css`.
- Trigger: Explore with at least one declared range, measured 400 × 840 CSS px viewport.
- Evidence: `design-v3/08-explore-mobile-400x840.jpg`; read-only DOM reports SVG width 319.78 px and viewBox `0 0 630 141`. Internal labels are 9–11 px, so whole-chart scaling yields approximately 4.6–5.6 px effective font sizes; observed text bounds are 6–8 px tall.
- Consequence: axis amounts, target and endpoint labels cannot be comfortably read. The exact-values table provides a functional fallback but requires separate disclosure and horizontal scrolling.
- Reproduction: load own case → Explore → view the C1 bar at the measured mobile width.
- Minimal correction: a mobile chart with unscaled HTML labels and exact endpoint values, or a labelled scrollable chart whose typography does not shrink.
- Acceptance: at 400 and 320 px widths, target and endpoint values are readable, match the server, remain keyboard operable and cause no page overflow.
- Root agent reports a fixed-size HTML mobile chart has now been implemented. That report is not treated as visual verification here.

### V3-D2 — Long case title produced horizontal rail scrolling

- Severity: low. Dimension: visual polish. Confidence: high. Status: **fixed_verified**.
- Initial evidence: `design-v3/01-initial-desktop.jpg` and `02-matching-1440x900.jpg` show a horizontal scrollbar below the long recent-case name.
- Retest: after the UI worker's min-width/overflow/ellipsis patch and page reload, the same title is truncated in the desktop rail without the horizontal scrollbar; full accessible title and tooltip remain available. See `04-range-desktop.jpg`.

## Visual and interaction assessment

- The desktop baseline uses the width effectively: compact case identity, explicit coverage, four useful metrics, findings and adjacent evidence. It provides a clear before/after distinction from the initial design.
- The matching screen exposes genuine ambiguity and exclusions rather than fabricating a match percentage. Reference-mode completion no longer carries the generic independently-verified implication of the old page.
- The alternatives matrix makes all three completed results comparable, and its detail identifies shared target propagation and joint arithmetic.
- On mobile, overview metrics wrap, all case sections remain reachable and Recent cases is accessible. The SVG label issue above is the material visual regression observed.
- Keyboard checks performed: Tab from Overview reached Explore with `:focus-visible = true`; Enter opened Explore; Space expanded the exact-values disclosure; Tab from the assumption selector reached the low-value input with visible focus. This is a targeted check, not a complete keyboard-only user journey.
- Read-only DOM confirmed the chart target itself has `role=button`, tabindex 0 and a descriptive label. Its actual keyboard activation is deferred to cycle 2.

## Screenshot inventory

| Artifact | Evidence |
|---|---|
| `design-v3/01-initial-desktop.jpg` | Initial v3 source workspace and original rail overflow |
| `design-v3/02-matching-1440x900.jpg` | Real unresolved source-matching state |
| `design-v3/03-baseline-1440x900.jpg` | Actual baseline and source inspector |
| `design-v3/04-range-desktop.jpg` | Shared C1 sensitivity and evidence-priority output; rail fix visible |
| `design-v3/05-alternatives-desktop.jpg` | Joint alternative detail and immutable execution identity |
| `design-v3/06-packet-verified-desktop.jpg` | Uploaded packet's passed verification |
| `design-v3/07-overview-mobile-400x840.jpg` | Actual mobile overview |
| `design-v3/08-explore-mobile-400x840.jpg` | Reproduced small SVG text and exact-values fallback |

## Limits and remaining cycle-2 checks

No model calls, cloud provisioning, external service writes, paid resources, sandbox runs or containment probes were performed in this review. The root's backend/API/VM test reports are separate evidence and not represented as browser results.

Reduced-motion runtime emulation was unavailable in the documented browser capabilities (viewport and management only; tab capability was pageAssets). The live query was `prefers-reduced-motion: reduce = false`. Source contains a reduced-motion CSS override, but the reduced-motion runtime is **NOT_RUN**. No native fallback or unsupported browser setting injection was attempted.

Cycle 2 must inspect the new mobile chart at 400 and 320 px, two-range analysis, target activation, actual source-file upload and draft invalidation, preserved legacy baseline/scenario flow, final desktop evidence, and any new defects. The source-file read-order race was independently reported and fixed by the engineering/root agents; it was not reproduced in this browser cycle. Screen-reader, formal contrast measurement and 200% zoom testing were not performed.
