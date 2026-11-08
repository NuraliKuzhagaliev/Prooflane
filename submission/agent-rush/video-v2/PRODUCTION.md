# Live demo production and asset rights

Recorded8–9 November 2026 from the actual public Prooflane application. The plan and narration were written before capture. The final edit is approximately 3:30 at 1920×1080, H.264/AAC MP4, with matching English captions and no background music. [Exact edit manifest](edit-manifest.json).

## What was actually recorded

The native browser screenshot stream captured roughly11 frames per second, each with a real timestamp. FFmpeg preserves timing and repeats captured frames for30fps output; no motion interpolation, generated UI, artificial cursor or synthetic action frames are used. Real clicks, typing, scrolling, request states and results remain visible.

The CSV file chooser completed slowly outside the bounded capture interval. That wait is omitted; chapter2 starts with the actual selected invoice/contract filenames and then shows reconciliation and explicit choices. Source/provenance inspection views have editorial cuts, including later readable views of the same case. Execution and containment retain start, waiting and completion; idle time after completed execution is shortened. Small final-frame holds fit speech and are declared in the manifest. This is an edited product recording, not a claim that the whole movie was one unbroken take.

The new recorded case is18615e14-2242-4f83-9034-3a5afa96479d. It actually called VSI twice, executed Python in Docker, independently verified768.00 across7 included rows, and confirmed cleanup. Containment and packet verification were fresh operations. [Packet](../../../artifacts/live-demo-v2/live-case-packet.json), [tests](../../../TESTING.md).

## Voice provenance and free budget

The eight MP3 chapters were generated through the user's already signed-in ElevenLabs Free account, using built-in George and Eleven Multilingual v2. No person was cloned. Existing allowance decreased from 9769 to 7012 credits: 2757 credits used. No subscription, top-up, paid video service or new cloud resource was purchased. Provider keys/account identifiers are excluded from the assets.

George output files are retained under `audio/`, paired by generation order with `script.json`. Exact wording is in `narration.en.txt`. FFmpeg normalizes speech toward −16 LUFS; measured final mean amplitude was −17.3 dB and maximum −1.4 dB. These different measures are not equated. Captions use proportional estimated timing, not forced alignment. No human listening-panel review is claimed.

Credit **elevenlabs.io** in the publication title/description and retain the final frame's attribution. [ElevenLabs billing documentation](https://elevenlabs.io/docs/overview/administration/billing), checked9 November 2026, states that Free outputs are for noncommercial use with attribution; paid plans supply commercial rights. This asset is not advertised as commercially licensed or included under the repository's MIT code license. Whether a particular organizer accepts an asset is not established by a test. Do not strip this notice when reusing the movie/audio.

Application screenshots use fictional authored inputs. Web fonts retain their supplied licenses. Segoe UI is used only to render captions; no Windows font file is redistributed. All editing/encoding is local with FFmpeg and Python; no Runway account or paid generation is needed.

## Quality evidence

The complete MP4 decoded without errors; H.264 video and AAC speech are present. Frames from all eight chapters were inspected. Model/request IDs and all three priority witnesses were recaptured at readable positions after the first draft's framing review. Updated README images are unretouched native application captures, not rendered mockups. [QA artifacts](../../../artifacts/live-demo-v2/).

Only the packet-verifier helper label changed in the deployed app during production. Its text now follows the actual verdict.179 Python /26 JavaScript tests passed after the change. No backend arithmetic, secrets, resource profile or infrastructure settings were changed.
