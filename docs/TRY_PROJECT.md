# Try Prooflane

Start on the [product homepage](https://45.76.92.198/) or open [the review workspace directly](https://45.76.92.198/app). The homepage has a local integer-cent illustration; it does not run AI or create a case. Use fictional data for the demo. The [recorded live walkthrough](../submission/agent-rush/video-v2/prooflane-live-demo.mp4) shows the actual workspace, including a real VSI run; it was recorded before the separate homepage was added.

For an immediate introduction, choose **Open a reviewed example**. It is explicitly Reference mode and makes no model call. To execute a new review, choose **Try the fictional review**, or select [case-invoices.csv](../examples/case-invoices.csv) and [case-contracts.csv](../examples/case-contracts.csv), then **Reconcile sources**.

1. Inspect INV504: two contracts overlap. Compare the source prices and select C2R explicitly.
2. Inspect INV506: no supplied contract is active on its invoice date. Enter an exclusion reason and record it. Seven of eight rows are now included; the excluded USD250 billed amount is not savings.
3. Create a baseline. **Reference** is trusted arithmetic, **Sandbox recipe** runs the fixed recipe in actual Docker, and **Vultr agent** generates Python through VSI before Docker execution. Live mode requires an authorized operator token. Never enter an inference API key in the browser.
4. The fixture should show USD768.00 positive price variance, five flagged rows and USD7,110 billed in scope. Select INV501 to inspect quantity 40, billed price 85 and contract price 72: `40 × (85 − 72) = 520`.
5. Select C1 to review its three linked invoices. In **Assumptions**, C1 at USD82.60 ties INV501 and INV503 for first priority; one cent further makes INV503 first. All other fields remain at their baseline values.
6. Optionally execute C1=80 as an alternative (USD368), or jointly set C1=80 and INV501 quantity=80 (USD568). These are named alternatives from the same original baseline, not a chain of overwritten results.
7. In **Proof**, follow a source dependency, inspect executed Python and actual request IDs, and run the containment check. Download the review CSV, brief or full packet. Verify a packet in the browser or offline with `python scripts/verify_receipt.py PACKET.json`.

An exported packet includes sources. Browser verification sends them to this server; offline CLI verification does not. Verification proves supplied-content consistency and fixed arithmetic, not supplier identity, contract truth, runtime authenticity or recovered money.

If a request times out, use the recovery interface; do not repeatedly click a charged POST. Reload stores only navigation and operation identities, not credentials or raw files. Cookies establish temporary ownership; clearing them loses access. Logical retention is 24 hours with activity-triggered cleanup.

Keyboard support includes chapter tabs, row inspectors with focus return, and Escape from Archive. Responsive layouts have been exercised at desktop, tablet and narrow widths. Physical touch, full screen-reader listening and system-level reduced-motion validation are not claimed. [Testing record](../TESTING.md).
