# Live Vultr AI verification — 9 November 2026

Two distinct successful public-browser runs are retained. The latest was recorded for the updated demonstration; it is not a Reference or fixed-recipe substitution.

## New recorded run

- Site: [public HTTPS application](https://45.76.92.198/).
- Case: `18615e14-2242-4f83-9034-3a5afa96479d`; run: `80e94339-3715-4832-baf0-fed3c6b5cc38`.
- Model: `deepseek-v4.1-flash-1017`.
- Generation request: `chatcmpl-5c3c7b38-9dbb-4177-8141-644840bc922c`.
- Guidance request: `chatcmpl-4a182d04-ca35-4c91-bf6e-4894aa9b1d28`.
- Actual result: seven of eight fictional invoice rows, one reasoned exclusion, five positive findings, USD768.00 positive variance, USD7,110.00 billed in scope.
- Docker: exit0, cleanup confirmed,128MiB/0.5CPU/32PIDs,network none,read-only root,UID65534,no host mounts or injected credentials.
- Independent output verification passed; downloaded [case packet](../artifacts/live-demo-v2/live-case-packet.json) passed all seven browser/CLI groups. Five fresh containment probes passed during the movie.

The browser selected C2R for the overlapping contract and excluded INV506 with an explicit reason before creating the baseline. The new movie shows execution start, waiting and result, actual code/request IDs, containment and packet verification. [Edit/production record](../submission/agent-rush/video-v2/PRODUCTION.md).

## Earlier run and failure history

The earlier successful run was `93ccc09e-5289-402d-b7b8-41be8c8e958e`, also7/8 rows, USD768 and two model calls, with exit0/cleanup true. [Earlier browser image](../artifacts/live-ai-20261109/live-proof.jpg).

The first earlier live response was incomplete and correctly refused before Docker. Investigation found default reasoning consumed the bounded DeepSeek response allocation. The provider now explicitly disables that default for the plan/guidance JSON requests. Token ceilings remained4096/1024, no alternate provider or Reference fallback was used, and the successful retest retained actual request IDs. The failure was not deleted or counted as a pass.

The guidance step is a bounded model choice of focus and next review action after arithmetic verification. The server supplies checked values. It is not a free-form model narrative or a second arithmetic authority. Raw CSV is not automatically included in model prompts; the user question can still contain supplied information.

The API key stayed on the server. The user explicitly authorized temporary operator-token transfer for entering their own site; the restricted local file was removed and credentials were entered off-record. Secret values were never included in evidence. Regressions and their environment limits are in [TESTING](../TESTING.md).

These observations prove the documented calls and supported calculation worked in those runs. They do not establish universal model reliability, live repair quality, a cryptographic runtime attestation or correctness of real-world contracts.
