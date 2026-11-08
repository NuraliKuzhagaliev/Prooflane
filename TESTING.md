# Verification record

Updated 9 November 2026. Counts below identify distinct checks and environments. Unit/API doubles, actual HTTP/Docker, browser operation, model calls and user studies are not interchangeable.

## Landing release

The separate homepage and `/app` workspace passed 180 Python tests and 30 JavaScript tests. The added route test checks that the pages remain distinct under the same origin/security headers. Preview tests reproduce the fictional baseline, shared-price totals, the 82.59/82.60/82.61 priority boundary and invalid-price rejection. Bootstrap verification passed structurally. Restricted-loopback pytest stalled after 13 checks and was interrupted; the successful full run used permitted loopback access.

Actual public browser checks cover desktop/tablet/mobile rendering, keyboard range steps, invalid input, native FAQ disclosure, landing-to-workspace navigation and restoration of the same existing Reference case. No new AI call was needed for this page. Reduced-motion rules disable transitions and smooth scrolling; system-preference emulation, physical touch hardware and a complete screen-reader listening session were not performed for this release. [Detailed scope and artifacts](docs/LANDING_20261109.md).

## Latest live recording and regression

| Check | Observed result | Evidence |
| --- | --- | --- |
| Python regression after packet-status fix | 179 passed, one existing Starlette deprecation warning, 5.34 s | [pytest log](artifacts/live-demo-v2/pytest.txt) |
| JavaScript regression | 26 passed | [Node log](artifacts/live-demo-v2/node-tests.txt) |
| New public-browser AI case | VSI generation → real Docker → independent check → VSI guidance; 7/8 rows, USD768, 5 flagged, cleanup true | [actual packet](artifacts/live-demo-v2/live-case-packet.json) |
| Fresh containment during recording | Five observed checks passed: denied egress/root write, absent key variable, UID65534, removal | [browser observation](artifacts/live-demo-v2/containment.txt), [image](docs/images/containment.jpg) |
| New downloaded packet | Browser and offline CLI accepted seven groups | [CLI verdict](artifacts/live-demo-v2/packet-verification.json), [browser image](docs/images/verification.jpg) |
| Actual website recording | H.264/AAC 1920×1080, about 3:30; full decode without error; eight chapter frames inspected | [edit manifest](submission/agent-rush/video-v2/edit-manifest.json), [frame review](artifacts/live-demo-v2/video-review/all-chapters.jpg) |
| Audio technical levels | Mean −17.3 dB, maximum −1.4 dB; no clipping observed in measurement | [FFmpeg log](artifacts/live-demo-v2/audio-levels.txt) |

New case `18615e14-2242-4f83-9034-3a5afa96479d`, run `80e94339-3715-4832-baf0-fed3c6b5cc38`, recorded at 01:40 Kazakhstan time. Model `deepseek-v4.1-flash-1017`; generation `chatcmpl-5c3c7b38-9dbb-4177-8141-644840bc922c`, guidance `chatcmpl-4a182d04-ca35-4c91-bf6e-4894aa9b1d28`. Two actual requests; no reference substitution.

The label after successful pasted-packet verification previously remained “not verified.” The frontend now updates it to the actual verdict; changing input invalidates the old verdict as before. Its regression fixture was updated for the label helper. The first JS rerun exposed that missing fixture helper (25/26); after correction, all 26 passed. No arithmetic logic or containment control changed.

The provider key stayed on the VM. An explicitly authorized temporary local operator-token file was used off-record and deleted before recording completed. No credential is included in captures or publication.

Latest public HTTP regression after the frontend change also passed 23 actual Sandbox checks with zero model calls: [new report](artifacts/live-demo-v2/http/sandbox-review-smoke.json). Bootstrap structure verification passed separately. It first detected the translated guarded workspace guidance; the original workspace AGENTS.md was restored and an equivalent English copy reserved for publication. This preserves local instruction integrity.

## Earlier real checks retained

- [9 November AI browser report](docs/LIVE_AI_CHECK_20261109.md): run `93ccc09e-5289-402d-b7b8-41be8c8e958e`, two calls and seven packet groups. The first incomplete provider response was refused before execution; default reasoning was then explicitly disabled for bounded JSON and the retest passed. No token ceilings were raised and no provider fallback was used.
- [Final public HTTP smoke](artifacts/final-submission-20261109/http/sandbox-review-smoke.json): 23 checks, actual HTTPS and Docker, zero model calls. It covers packet/CSV/brief, ownership, recovery/replay and strict parsing.
- [8 November case HTTP smoke](artifacts/transformation-20261108/public-case/case-http-smoke.json): 57 Reference/Docker checks; [review smoke](artifacts/transformation-20261108/public-review/sandbox-review-smoke.json): 23 checks. Real containers, no new model calls. Repeated UUIDs return the original case/run; changed replay returns 409 and another session gets 404.
- [Priority release](artifacts/priority-release/case-http-smoke.json): 57 actual HTTP checks. Browser C1=82.60 alternative produced USD244 with the original baseline preserved; its downloaded [packet](artifacts/priority-release/browser-case-packet.json) passed seven groups.
- [4 November transformation](artifacts/transformation/case-http-smoke.json): 52 case checks and [36 legacy checks](artifacts/transformation/legacy/scenario-smoke.json), genuine HTTP/Docker without inference. Windows and Linux regressions each had 155 tests at that revision, not the current count.

Earlier Linux validation, targeted adversarial probes and independent arithmetic reviews remain in `artifacts/transformation-review/` and `artifacts/optimization-review/`. Their English summaries identify historical scope; they are not new reviews conducted for this video. [Historical verification](docs/TESTING_V2_HISTORY.md).

## Reproducible fixture values

Select source row5→C2R and explicitly exclude source row7. Seven of eight invoices remain: positive variance768.00, billed7110.00. C1=80 affects normalized rows2,3,8 and gives368.00. Joint C1=80 and row 2 quantity 80 gives568.00. Both alternatives retain the original baseline. C1 at82.59 leaves INV501 uniquely first; at82.60 INV501/INV503 tie; at82.61 INV503 leads.

C1 range[65,85] gives148.00..1193.00. Adding quantity row 2[20,80] gives148.00..1993.00, width1845.00. Confirming C1 yields minimum guaranteed narrowing645.00 and possible1845.00; quantity yields0.00 and1200.00. These are deterministic interval reductions, not expected returns.

Independent tests compare 216 complete small boxes and separate integer-cent calculations; later priority tests enumerate576 small grids. Local performance measurements use synthetic500-invoice/500-contract workloads; [before/after samples](artifacts/transformation-20261108/performance-after.json) are CPU measurements, not public latency or multi-user load tests.

## Repeat and interpret correctly

```powershell
.venv/Scripts/python.exe -m pytest -q
node --test tests/test_*.mjs
.venv/Scripts/python.exe scripts/verify_receipt.py artifacts/live-demo-v2/live-case-packet.json
.venv/Scripts/python.exe scripts/smoke_sandbox.py
.venv/Scripts/python.exe scripts/smoke_case.py --base-url https://YOUR_HOST --output-dir artifacts/cloud
```

The runtime smoke needs Linux Docker and the built image; HTTP tests need a running app and consume request quotas. They do not call the model unless a live-specific script explicitly says so. Bootstrap verification checks structure only. Windows tests need permitted loopback access: a restricted earlier run stalled after13 tests and was interrupted; it is not counted as a pass.

Recorded browser checks include real source choices, upload/recovery, alternatives, range errors, Archive Escape, focus return, reload and responsive layouts at desktop/tablet/mobile320–390px. No physical-touch test, complete screen-reader listening, system-level reduced-motion toggle, real process-SIGKILL test, public load test or independent customer study is claimed. The new movie was technically decoded and visually sampled; technical audio measurements do not constitute a listening panel.
