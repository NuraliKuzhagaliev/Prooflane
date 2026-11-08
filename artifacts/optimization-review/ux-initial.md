# Prooflane independent initial UX review

Reviewed 2026-11-03 against the locally running application at http://127.0.0.1:8765/ and the pre-transformation `web/index.html`, `web/app.js`, `web/styles.css`. This is observed product behavior and source inspection, not user research. Source files were not changed by this reviewer.

## Decision

Preserve the existing source-row inspection, exact arithmetic and transparent execution evidence. Address input/result coherence and mobile navigation before adding a flagship comparison flow. An immutable baseline plus a clearly hypothetical, separately executed scenario is a coherent extension of the current product. It turns a static finding into an actionable investigation while retaining the existing evidence chain.

## Confirmed findings

### P1 — Changed inputs retain a misleading verified result

- Trigger: load the synthetic sample, run Sandbox recipe, then replace the CSV text with a single zero-variance row.
- Observed: input changes to `edited-invoices.csv`, 96 bytes, containing `UX-1,Example,1,1.00,1.00,no variance`; the adjacent result still says **Result verified**, **$1,480.00**, **6 of 24 rows**, with the old receipt available. The old filename exists in small result metadata, but there is no current-input mismatch warning.
- Consequence: an analyst can mistake old verified output for the current draft. The same ambiguity arises when reopening history while the form contains a different CSV or execution mode.
- Evidence: `ux/stale-result.jpg`; `web/app.js:106` (`setCsv` changes input state only); history-open rendering leaves the draft intact.
- Minimum fix: represent the result as an immutable named run and show a conspicuous "Inputs changed — rerun to analyze this draft" state whenever relevant draft fields differ. Do not imply the old receipt verifies the new draft. A comparison editor should explicitly distinguish baseline, scenario draft, and executed scenario.
- Acceptance: changing CSV, question or mode after completion visibly marks mismatch; restoring exact values clears it; downloads remain explicitly linked to the named prior run. Opening a historical run also makes its input/mode relationship unambiguous.

### P2 — Saved runs disappear on phones

- Trigger: resize the actual page from 1440×1000 to 390×844 with multiple saved runs.
- Observed: all recent-run controls and both navigation links disappear from the accessibility tree and rendered UI. There is no mobile alternative.
- Evidence: `ux/mobile-top.jpg`; `web/styles.css:7` hides `.history-section,.primary-nav` below 700px.
- Consequence: mobile users cannot reopen prior evidence or reach history, a core part of this product.
- Minimum fix: compact history drawer/disclosure reachable from the mobile header, with the same run actions and keyboard accessibility. Navigation may collapse, but its capabilities should remain available.
- Acceptance: at 390px and 320px, open a prior run, inspect a finding and download its receipt without changing viewport size.

### P2 — UI accepts questions the API rejects without explaining the limit

- Trigger: enter 601 characters into the question field and run reference mode with a valid one-row CSV.
- Observed: submission proceeds, then a generic error says "Invalid input. Check field types, allowed sizes and UTF-8 text." It does not identify the question or 600-character limit.
- Evidence: `web/index.html:60` has `maxlength=2000`; `prooflane/app.py:48` has `max_length=600`; `prooflane/app.py:82` returns the generic 422. Browser reproduction completed.
- Minimum fix: align the visible limit and client validation with the API, add a remaining-character counter if the field stays editable, and preserve useful field-level server error detail.
- Acceptance: 600 characters accepted; 601 cannot silently reach a generic error; error focus/announcement identifies the question.

### P3 — Reduced-motion preference is bypassed on history open

- Source-confirmed, not OS-preference runtime-tested: `web/app.js:330` uses `scrollIntoView({behavior:'smooth'})`, while CSS attempts to honor `prefers-reduced-motion`.
- Consequence: the user preference is not applied consistently to programmatic motion.
- Fix/acceptance: choose `auto` when reduced motion is requested; verify both preference states when opening history.

## Product clarity and design opportunities

1. **Make the supported task explicit.** The prominent freeform "What should we investigate?" and "One question. A traceable result." suggest broad analysis, but the implemented contract is fixed positive unit-price variance. The helper sentence is accurate yet subordinate. A visible review plan — compare billed unit prices to supplied contract prices, cite rows, verify with Decimal — should lead. Keep optional notes separate from a promise of flexible computation.
2. **Reduce unavailable-mode dead ends.** Source inspection shows that `updateMode` labels unavailable Docker/VSI states, but `updateRunButton` only checks busy/CSV. The Vultr option remains selectable even when not configured. Make availability visible on each option and prevent a run that the known health state cannot execute; preserve an explanation of how to enable it. No live inference request was made in this review.
3. **Lead with the user decision, then expose execution details progressively.** Current result has good hierarchy and useful vendor totals, but detailed code/containment metadata should support the analysis rather than compete with the main path. Preserve its honest provenance and the distinction between reference, fixed sandbox recipe and generated code.
4. **Increase reading comfort.** The desktop workspace uses many 9–11px labels and metadata strings. The source detail dialog is coherent, but its facts could be larger. Treat readability as an opportunity, not a claimed WCAG contrast failure; no complete contrast audit was performed.
5. **Keep the calm visual identity.** The cream surface, deep green sidebar, restrained accents and serif headline already establish a distinctive finance/evidence workspace. A transformation should strengthen interaction and information hierarchy rather than replace it with unrelated ornament.

## Recommended flagship: test a contract assumption

Placement: extend the existing source-finding detail rather than invent a separate disconnected chat. Preserve read-only original values, then offer **Test an assumption**. A scenario editor selects the record and field, shows original → proposed value, and names the immutable baseline. A live draft preview must be explicitly labeled unexecuted. **Run comparison** executes through the same selected mode, then displays independently verified before/after totals and row-linked differences.

Concrete first-30-seconds story, using only synthetic data:

1. Load the synthetic invoices and run an available mode. Baseline: $1,480 positive price variance, 6 flagged lines.
2. Open `INV-2402`, source record 3: 40 × ($85 − $72) = $520.
3. Test a proposed contract price of $80. Original baseline remains unchanged; the scenario changes only that source assumption.
4. Execute the comparison. Scenario row variance is $200; portfolio variance is $1,160; change is −$320.
5. Download a comparison packet containing both receipts and the explicit change. Label it as a hypothetical scenario based on supplied data, not confirmed savings, a contractual determination, or proof of invoice error.

The result should answer three questions at a glance: **What changed? What effect did it have? What independently verifies each result?** Show baseline and scenario run IDs, same-mode provenance, changed record/field, and both input hashes where appropriate. Reject ambiguous joins and multiple records that cannot be uniquely reconciled. A scenario that resolves the selected finding to zero must still show the changed row and its zero result, not drop it from the comparison.

## Browser checks performed

| Check | Result | Actual evidence |
|---|---|---|
| Synthetic sample load and real Docker run | PASS | Run `a4876303-267d-4da4-b15b-3d431f1719fa`; 24 rows, 6 findings, $1,480 variance, $34,353 billed; UI reports removed container |
| Paste/change input | FAIL coherence | Current draft changes while old result remains verified; screenshot |
| 601-character question | FAIL usability | API generic validation error reached from accepted UI value |
| History reopen on desktop | PASS | Existing sample run reopened with its findings/provenance |
| Source detail and formula | PASS | INV-2402, record3, qty40, unit85, contract72, variance520; `ux/source-detail.jpg` |
| Dialog Escape/focus | PASS | Escape closes dialog and returns focus to the initiating invoice button |
| Receipt download | PASS | Actual browser download copied to `ux/sandbox-receipt.json` |
| Downloaded receipt independent CLI verification | PASS | `.venv/Scripts/python.exe scripts/verify_receipt.py artifacts/optimization-review/ux/sandbox-receipt.json`; all five arithmetic checks pass, exit0 |
| Containment check button | PASS for reported probes | Network egress failure, read-only root denial, inference-key absence, UID65534, cleanup; elapsed1293.6ms reported by this actual run |
| Mobile 390×844 | FAIL capability parity | History/navigation absent from UI and accessibility tree |
| Browser console warnings/errors | PASS observed window | Captured log returned `[]` |
| Native file chooser/drag-and-drop | NOT_RUN this audit | Source inspected; do not claim browser upload coverage |
| Live Vultr inference / cloud deployment | NOT_RUN | Unconfigured; no paid calls or Vultr account actions |
| Full screen-reader, OS reduced-motion, contrast audit | NOT_RUN | Keyboard Escape/focus and source-level reduced-motion inspection only |

Viewport override was reset and the temporary audit tab closed after the checks. Existing user/history data was not deleted. Synthetic audit runs remain as ordinary local history records.
