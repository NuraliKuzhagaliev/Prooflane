# Submission build notes

The final Agent Rush files are under [agent-rush](agent-rush/README.md). After the video refresh, the existing editable deck was imported into an Artifact Session and updated with the team-supplied logo on all six slides. The exported PPTX passed structural package/layout validation; all six rendered slides were visually inspected. `scripts/build_submission_pdf.py` assembled the updated renders into the six-page PDF. The unchanged team-supplied 1672×941 cover replaces the earlier slide-derived cover. Native PowerPoint rendering was not tested. `scripts/build_submission.mjs` now preserves these brand assets on a future rebuild.

The current movie is built by `scripts/build_live_demo.py` from timestamped native browser recordings in the ignored project cache and eight downloaded ElevenLabs MP3 chapters. It is an actual-site recording, unlike the previous still-frame walkthrough. The plan, script, captions, rights and edit manifest are public alongside the MP4. Raw capture frames are local cache and are not needed to run the application.

The local upload ZIP is an ignored convenience copy, not an entry submission. Its contents, CRC and SHA manifest are checked during packaging. Text files are normalized to LF before hashing; `.gitattributes` pins those bytes across checkouts. Media is binary. Never include `.env`, databases, private keys, operator tokens, local caches or screenshots of credentials.

If rebuilding the video elsewhere, first collect authorized real captures and voice assets; the published script cannot invent missing recordings. Reference/Sandbox modes require no inference key. A new AI recording consumes the existing provider allowance only when explicitly authorized; no paid resource is created by the build script.
