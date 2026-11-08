# Independent UX review — final cycle 1

Date: 2026-11-03. Local target: http://127.0.0.1:8765/. Reviewer did not modify product source. Browser: dedicated temporary Chrome tab because the in-app browser was unavailable at this stage. The browser's existing 75% zoom was preserved; responsive results below use measured CSS viewport widths, not the requested physical override. Temporary viewport was reset and the audit tab closed at the end.

## Verdict

The complete source → one assumption → comparison → packet → original path works with actual local Docker execution. The original audit's material UX failures are fixed in the paths exercised. No new P1/P2 product defect was reproduced in this cycle. A minor copy mismatch remains below. This is a local UX result, not cloud/model acceptance or a comprehensive accessibility certification.

The new feature adds meaningful behavior: the user can test a numeric assumption, see its row and portfolio effects, and keep two linked receipts without replacing the original. The before/after facts, hypothetical label and same-mode statement are legible and explicit. The current visual identity remains coherent; source values, proposed values and executed results are separated appropriately.

## Reproduced end-to-end evidence

- Loaded the synthetic sample and selected **Sandbox recipe**. Original run `c0072cb5-0631-4659-b682-ce01c35e2018`: 24 records, 6 findings, $1,480.00 variance, $34,353.00 billed. The actual execution record reported Docker and confirmed removal.
- Opened `INV-2402` from findings. Detail showed source row3, quantity40, billed85, contract72, formula `(85−72)×40 = 520`. Entered the scenario from the detail action; it selected row3 and focused Proposed value.
- Entered contract80 and ran comparison. Scenario `3dd0c4de-743c-4d15-a80c-6986670758b2`: $1,480→$1,160, delta−$320; row520→200; 23 unchanged records; both modes sandbox. UI prominently says **Verified · hypothetical** and retains the assumption's source identity.
- Downloaded the real comparison packet through its link, then **Return to original baseline**. The original amount returned to $1,480 and the form restored its original CSV/mode.
- Reopened that scenario from mobile history. Source modal correctly showed contract80 and row variance200; creating a chained scenario there was disabled with a return-to-original explanation.
- At measured CSS320×844, returned to the baseline and started another row3 assumption. A no-op `72.00` was rejected with a specific error and focus on Proposed value. Contract85 executed successfully as `07f84a34-a563-4612-be0c-6a443384fd81`: original1480→scenario960, row520→0, flags6→5, 23 unchanged records. The changed row remained represented in the comparison facts even though it disappeared from positive findings.
- After completion, Tab reached **Download comparison packet**; Enter downloaded the second real packet.

Both browser downloads were copied into `ux-cycle1/comparison-80.json` and `ux-cycle1/comparison-85.json`. Each passed:

```text
.venv/Scripts/python.exe scripts/verify_receipt.py artifacts/optimization-review/ux-cycle1/comparison-80.json
.venv/Scripts/python.exe scripts/verify_receipt.py artifacts/optimization-review/ux-cycle1/comparison-85.json
```

Each verifier exited0 and reported: both receipt hashes/arithmetic, baseline identity/hash, exactly one declared assumption, same execution mode and all signed deltas passed. These prove the checked artifact relationships and arithmetic, not issuer identity or truth of the supplied contract prices.

## Prior-finding regression results

| Concern | Result | Observation |
|---|---|---|
| CSV changed after verified run | PASS | Warning says inputs changed/previous result; previous-figures note appears above totals; assumption action disabled; download relabeled **Download previous receipt** |
| Context changed after verified run | PASS | Same stale state; **Reopen saved run** restores context and binding |
| Execution mode changed after run | PASS | Switching sandbox→reference marks stale and disables assumption; switching back clears the mismatch |
| Mobile history absent | PASS | At CSS391×844 the history disclosure and both navigation links are visible; actual prior comparison successfully reopened |
| Context601 characters | PASS | Automation fill can bypass native maxlength, but submit stops locally with **Review context must be 600 characters or fewer** and focus at question; no generic API error |
| Context600 characters | PASS | Actual reference run `4a134f7e-f8f7-4990-932c-fe4fd57581c7` succeeds with one row, $1 billed, no variance |
| Known unavailable inference | PASS | Vultr agent is disabled and visibly labeled **Unavailable · inference is not configured** |
| Dialog Escape/focus | PASS | Escape closes scenario-source modal and returns focus to the invoice button |
| Narrow editor fit | PASS | At CSS320×844, document scrollWidth300 including the browser's20px scrollbar; editor width271.78; no page horizontal overflow observed |
| Programmatic reduced motion | Source PASS, runtime NOT_RUN | `web/app.js:46` now chooses auto/smooth based on the media query; test browser preference was false, and no supported browser preference override was exposed |

## Remaining fixable issue

### P3 — Context placeholder promises a generated review note

`web/index.html:60` says **Add context for the review note; the calculation stays the same.** In reference and sandbox modes, the review note is assembled from fixed verified figures and does not use this context (`prooflane/app.py` explanation construction). The field is stored with the run, which is useful, but users may expect their context to influence the displayed note.

Small fix: **Save context with this review; the calculation stays the same.** Keep the existing **Context does not change the calculation** help. Acceptance: visible wording accurately explains what happens in all three modes without promising an unavailable narrative function.

## Nonblocking design observations

- Main figures now use clearer sizing than the initial build. Before/after totals, signed change and original/scenario links form a coherent comparison panel. Keep the exact signed money formatting and the zero-row detail.
- On mobile the setup form remains above results and grows when CSV is expanded. History-open and comparison-complete scroll to the evidence region, so the tested flow remains usable. A future compact summary of the loaded input after success could shorten review navigation, but this is an improvement rather than a release blocker.
- The technical evidence is still inspectable through disclosures. Avoid adding further security labels or speculative promises; the current text distinguishes real sandbox execution, unconfigured inference and hypothetical results.

## Evidence artifacts and limits

- `ux-cycle1/comparison-desktop.jpg`: actual post-comparison desktop view; capture is larger than CSS viewport because of browser scaling.
- `ux-cycle1/stale-warning.jpg`: changed CSV with previous-figures warning and disabled assumption action.
- `ux-cycle1/mobile-history.jpg`: mobile history/navigation visible.
- `ux-cycle1/mobile-full.png`: full page containing mobile comparison, receipt links and remaining source findings. The screenshot mechanism temporarily exposes a skip-link overlay; read-only DOM inspection afterward confirmed the unfocused skip link's rectangle was y−60 to−15, outside view. It is not counted as a product defect.
- `ux-cycle1/mobile-comparison.jpg` and `.png` are unusable blank viewport captures from the browser screenshot path; they are retained as capture limitations, not claimed as evidence of a blank application. Full-page capture and live DOM/interaction confirmed the page remained rendered and functional.
- Captured console output included two Chrome message-channel listener errors without an application stack: **A listener indicated an asynchronous response by returning true, but the message channel closed before a response was received**. No user-visible application failure accompanied them; attribution to Prooflane was not established.
- Live VSI/cloud, native file chooser/drag/drop, OS reduced-motion toggle, full screen-reader traversal and comprehensive contrast audit were not run in this cycle. No Vultr account actions or paid model calls occurred.

Cycle 2 should recheck the frozen implementation after any fixes, including the adjusted context copy and final end-to-end download path.
