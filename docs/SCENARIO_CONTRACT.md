# Scenario contract (implementation interface)

Flagship: one original review → one changed numeric assumption → separate run through the same execution mode → independently verified comparison packet. Scenario is hypothetical, never a correction/payment/savings claim. Original receipt/run is never mutated. Scenario-on-scenario is rejected; return to original baseline for another alternative.

`GET /api/runs/{id}/source` (same browser session) returns `{baseline_run_id, baseline_receipt_sha256, mode, rows:[{row,invoice_id,vendor,quantity,unit_price,contract_price}]}`. Verified original runs only; owner mismatch/missing receipt gives404; scenario baseline gives422.

`POST /api/runs/{id}/scenario` with existing `X-Prooflane-Request:1` and same-origin JSON:

```json
{"baseline_receipt_sha256":"64 hex chars", "row":3, "field":"contract_price", "value":"80.00", "operator_token":""}
```

Fields allowed: `quantity`, `unit_price`, `contract_price`. Exactly one numeric change; existing parse_csv bounds apply. Wrong baseline hash gives409; invalid input/no numeric change gives422. Execution mode is inherited from baseline, never silently downgraded. Vultr mode requires explicit token and existing provider gates. Baseline contents/price values are not added to model prompt.

Response is regular run shape plus `lineage:{schema:'prooflane.scenario.v1',baseline_run_id,baseline_receipt_sha256,change:{row,field,before,after}}`. A successful scenario also has `comparison:{scope,baseline:{run_id,receipt_sha256,mode,row_count,flagged_count,total_billed,total_variance},scenario:{same fields},delta:{total_variance,total_billed,flagged_count},change:{row,field,before,after,invoice_id,vendor,before_variance,after_variance,variance_delta},unchanged_records}`. Signed money values are decimal strings. A failed scenario is a failed run, has no comparison and cannot export a bundle; original stays available.

`GET /api/runs/{scenario_id}/comparison` downloads `prooflane.comparison.v1` JSON with `{schema,baseline:<full receipt>,scenario:<full receipt>,comparison,bundle_sha256}`. Ownership checked for both stored receipts. This is a downloadable artifact, not an additional server mutation. If baseline expired,404; already downloaded bundle remains verifiable without server/data retention.

`python scripts/verify_receipt.py FILE.json` recognizes original receipts and comparison bundles. It recomputes both CSVs, checks the parent link, exactly the declared source-cell change, and all deltas. Rehashing an undeclared edit must fail. Hashes do not authenticate sender or prove Docker/Vultr execution.

Demo: synthetic sample original `$1,480.00` → row3 `contract_price:72.00→80.00` → `$1,160.00`; delta `-$320.00`, billed unchanged `$34,353.00`; row3 variance `$520→$200`, other23records unchanged. Return to baseline still shows1480.
