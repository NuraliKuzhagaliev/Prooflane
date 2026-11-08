# Prooflane demo production

This English demo is an **edited walkthrough made from real browser still captures**, with local Windows synthetic narration and English captions. It is not a continuous screen recording or a newly executed AI call. No fabricated UI, cursor movement, model responses, request IDs or containment outcomes are used.

The AI scenes display the successful saved public-browser run from 9 November 2026 (Kazakhstan time). The original generation and explanation request IDs are documented in [the live report](../../../docs/LIVE_AI_CHECK_20261109.md). The captured baseline remains immutable. Source and priority scenes inspect that same saved case.

The containment scene displays five fresh browser-triggered probes on the existing Vultr VM during final preparation. The packet scene shows the original downloaded AI packet passing the seven reconstruction groups again. No model calls or new paid resources were used to make this video.

Narration uses the installed Microsoft Zira Desktop voice locally. There is no music, cloned voice or third-party stock video. UI footage, slide graphics and fictional source data come from this repository. Existing font licenses remain in `web/fonts`.

Rebuild on this Windows workspace:

```powershell
powershell -NoProfile -File scripts/narrate_demo.ps1
# Run with the bundled Python that provides Pillow; FFmpeg is project-local.
& 'C:/Users/nural/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' scripts/build_demo_video.py
```

The project-local FFmpeg package is `imageio-ffmpeg==0.6.0` under `.cache/video-python`. Audio and intermediate frames are ignored by Git. `storyboard.json` contains the narration and exact capture crops; `video-manifest.json` records the resulting file hash, duration and chapter times. Complete decoding and a rendered-frame review are required after rebuilding.
