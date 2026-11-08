# Workbench v3 implementation contract

Preserve existing six-column review/scenario APIs. New case workbench is additive. Cases and runs are session-owned, expire after24h; references do not extend retention. All computed findings are supplied-data signals, never contract truth or recovered savings.

## Source reconciliation

Invoice CSV exact columns: `invoice_id,vendor,item_id,invoice_date,quantity,unit_price,notes`.
Contract CSV exact columns: `contract_id,vendor,item_id,valid_from,valid_to,contract_price`.
USD only. Each source <=128KiB,1..500records. ISO dates, inclusive intervals, unique contract IDs. Exact trimmed case-sensitive vendor/item match and date containment. No fuzzy match. Multiple candidates require explicit selection of an eligible contract ID. Missing matches require source correction or explicit exclusion reason; no silent drop. At most5,000 eligible invoice–contract links; excessive overlaps are rejected before a large report is returned. Create/match JSON bodies <=2MiB to allow two escaped CSV files; source byte limits remain128KiB each.

`POST /api/cases/match {invoices_csv,contracts_csv,selections:{"2":"C1"},exclusions:{"4":"Outside review scope"}}` returns reconciliation report: `ready,counts:{total,matched,selected,unresolved,excluded},records:[{invoice_row,invoice_id,vendor,item_id,invoice_date,status,candidates:[{contract_id,contract_row,contract_price,valid_from,valid_to}],chosen_contract_id,reason}],canonical_csv,bindings:[{row,invoice_row,contract_id,contract_row}]`. row=canonical CSV record number, source numbers start2. `canonical_csv` only available when ready, no unresolved; excludes explicitly logged.

`GET /api/cases/sample` returns `{invoices_csv,contracts_csv,name}` synthetic case with shared contracts, one overlap and one unmatched invoice. `reconcile(...)` is pure deterministic module used by API and offline verification.

## Cases and alternatives

`GET /api/cases` -> `{cases:[{id,name,created_at,baseline_run_id,mode,variant_count,revision}]}`.
`POST /api/cases` accepts `{name,mode,operator_token,invoices_csv,contracts_csv,selections,exclusions}` OR `{name,baseline_run_id}` from existing original verified review; no mixing. On success `{case:<state>}`. Normalization produces canonical six-column CSV then executes existing pipeline in chosen mode. Failures do not create a case. No model fallback.
`GET /api/cases/{id}` -> `{case:<state>}`. State: `id,name,created_at,revision,baseline:<run>,source:{kind:'contracts'|'embedded',counts,records,bindings},targets:[{id,label,field,rows,before,contract_id?,invoice_id?}],bounds:[{target,low,high}],intelligence:<analysis>,variants:[{id,name,changes:[{target,value}],run:<run>,delta,changed_rows}],limits:{max_variants:4,max_changes:12,max_bounds:24}`.

Targets: shared `contract:C1` changes contract_price on every invoice bound to C1; other fields `row:3:quantity` or `row:3:unit_price`. Embedded original also has `row:3:contract_price`. Source prices remain original evidence; proposed targets are labelled assumptions. No sums of OAT deltas for joint changes: recalculate jointly.

`POST /api/cases/{id}/variants {revision,name,changes:[{target,value}],operator_token}` -> updated `{case}`. Max4 immutable named alternatives, each up to12distinct targets. Inherit baseline execution mode and check current live gate/token; always same original baseline. Reject numeric no-op, duplicates/overlap, invalid ranges, stale revision409. Failure returns failed run and preserves baseline; no false verified variant.
`POST /api/cases/{id}/bounds {revision,bounds:[{target,low,high}]}` -> updated `{case}`. Bounds max24; include baseline value; fields obey CSV numeric constraints. Pure trusted interval analysis, no model or sandbox call. Each shared contract is one variable, not duplicate row cells. Empty array restores fixed inputs. Labels explicitly distinguish estimates from executed alternatives.

## Review aids and recovery, 8 November

Match responses and case state include deterministic `review_insights`: `coverage` with total/included/excluded/unresolved billed USD amounts, `rival_contracts` with conditional per-invoice variance for every eligible overlap candidate, `duplicate_groups` with source row IDs sharing invoice ID/vendor/item/date/quantity/billed price (notes may differ), and baseline `groups` by shared contract with original billed/variance totals and exact source/normalized row sets. Signals do not change selections or exclusions and do not establish duplicate payment or contract validity. A shared group action filters all its rows, including zero variance. Embedded-price cases retain independent row price groups.

Owned `GET /api/cases/{id}/handoff.csv` exports all source rows with exclusions and blank excluded variance. Textual spreadsheet-formula prefixes are neutralized; numeric cells follow the validated schema. `GET /api/cases/{id}/brief.md` exports a readable unsigned summary including source-quality concerns and hypothetical alternatives. Both retain no-store and same-session access. Neither is a substitute for the independently reconstructed JSON packet.

Optional UUID `request_id` on create/variant binds endpoint, explicit field presence and canonical input values excluding credentials. Same ID/meaning replays the existing case/run; a pending operation returns202, changed meaning409. `GET /api/operations/{id}` is owned, status-only and starts no work. Records store IDs/digests/status, not source bodies or tokens;24h TTL and quotas. Startup of the single application worker reconciles committed results or records interrupted, never automatically reruns. Related case writes retain revision CAS and locks; unrelated case writes may proceed. Browser deadlines abort waiting only, not the server operation; pending IDs hydrate before interaction and prevent new execution until checked.

Evidence JSON rejects duplicate object keys and non-finite constants in both API and CLI. The browser sends raw uploaded JSON rather than normalizing away ambiguous keys. Case packet schema/priority semantics below stay compatible.

## Evidence semantics

Case state now also supplies `priority_switch`. It varies only the original unique leading invoice's contract-price target in whole cents from 0 to 99,999,999.99, propagating a shared target to every bound invoice. Other fields stay at their original values, regardless of declared bounds or executed alternatives. It returns the inclusive strict-priority interval and, for each available direction, the last strict price, first changed price, and next-cent witness. A changed state may be a tie or no positive variance; it is not necessarily a new unique leader. Original ties, zero positive variance, and a single included invoice have explicit unavailable states. The UI prepares an alternative draft; the user still adds and executes the change.

`GET /api/cases/{id}/packet` downloads `prooflane.case.v1`: source evidence (raw two files or embedded CSV, decisions), baseline receipt, named variant receipts/changes, bounds and exact intelligence results, root hash. Offline verifier reconstructs source join and every changed CSV, verifies all receipts, then recalculates intelligence. No arbitrary code execution, runtime attestation or issuer signature.

New exports include optional top-level `priority_switch`, covered by `case_sha256` and independently reconstructed from the baseline and source bindings. The updated verifier accepts historical v1 packets without that field (six check groups) and checks the additional claim when present (seven groups). Historical verifiers may reject the extension; use the updated CLI for new exports. Removing the field makes no priority-boundary claim. A hash alone does not authenticate an issuer.
`POST /api/verify-packet` accepts packet JSON, max8MiB, returns `{passed,checks,scope,...}` or `{passed:false,error}` for invalid artifact. It does not import cases or execute code; packets include their source data. Rate/body limits apply. Existing `scripts/verify_receipt.py` accepts old receipts/comparisons and new case packets.

New UI main views: Sources (match resolution), Overview (coverage/review queue), Explore (range plot, next evidence to check, named alternatives), Evidence (source links and packet verification). Preserve old single CSV review, existing history, receipts, source dialog, containment in an accessible legacy view. Motion respects reduced motion. Reference status says reference complete; independent verification only for actual sandbox/code output.
