# Engineering decisions

Updated 9 November 2026; historical choices are retained with their current consequences.

| Decision | Reason and tradeoff | Revisit when |
| --- | --- | --- |
| Narrow price-variance review | A fixed, independently checkable arithmetic contract and a concrete AP workflow. A free-form question cannot expand the supported computation. | New tasks have formal contracts and independent oracles. |
| FastAPI, vanilla JS and SQLite | One deployable same-origin application, no production Node build/runtime, bounded persistence. | Collaboration, multiple replicas or a durable queue is needed. |
| Independent Decimal verification | The generated program is not the authority for arithmetic. Every finding and total is checked. | Extending the verifier with separately tested contracts. |
| Bounded model guidance after verification | VSI selects a focus and next step; the server inserts checked values. This replaced a solely deterministic explanation without permitting invented totals. | A broader grounded narrative contract has evidence and tests. |
| No automatic raw-CSV transfer to VSI | The model knows the schema, count and question and writes for `/tmp/input.csv`. The offline container processes actual values. Questions can still disclose data. | A specific task needs data-aware generation with explicit consent. |
| Fixed Docker profile on a dedicated VM | Available, demonstrable isolation. Shared kernel and privileged daemon are residual risks. | Hostile public workloads justify a broker, rootless runtime, gVisor or microVM validation. |
| No host execution fallback | Missing/unconfirmed Docker controls fail closed. Reference mode is separately labelled trusted code. | Do not relax this for demo convenience. |
| At most one repair | Bounds delay and credit consumption. Generic feedback omits CSV and stderr; retries require confirmed cleanup. | Real repair-rate and quality measurements justify a change. |
| Separate attempt records | Successful repair cannot hide previous code, output or errors. | Versioning an expanded execution contract. |
| Persistent quarantine | Cleanup failure and project-labelled leftovers block execution after restart. Unknown leftovers are not deleted automatically. | A tested lifecycle supervisor and real crash experiments exist. |
| Unsigned portable receipts | Easy offline checking; no issuer authentication or runtime attestation. | A real consumer and key/trust-management design justify signatures. |
| Operator gate for live calls | Protects the existing allowance. Reference/fixed Docker remain publicly usable without a provider key. | A safe judge-access or account/budget design is agreed. |
| One worker | Limits, semaphore and locks are process-local. | A shared limiter/queue is implemented and tested. |
| Explicit source decisions and shared variables | Ambiguity is visible; one contract change affects all bound invoices. | Domain research supports additional matching or contracts. |
| Deterministic priority boundaries | Whole-cent witnesses help identify the next source to review; no probability or legal claim. | A different supported arithmetic contract needs new math. |

The actual model ID and existing VM were verified rather than invented. No new paid resource or subscription was created during final demo production. Inference live gates changed from NOT_RUN only after real tests; historical reports retain their original dates and limitations.
