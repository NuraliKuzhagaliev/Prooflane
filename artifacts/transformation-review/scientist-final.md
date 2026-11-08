# Functional science audit — cycle 1

Date: 2026-11-04. Reviewer: `v3_scientist`. Scope: implemented `prooflane/intelligence.py`, `reconciliation.py`, and `case_evidence.py`, plus the saved reference/sandbox case packets. This is the first functional science audit; it is not a claim that the requested second final review cycle has occurred.

**Result:** no remaining mathematical/certificate defect found in the tested scope. One concrete provenance-consistency defect was reproduced, reported, fixed by the implementation owner, and retested. The exact source-target bounds, one-at-a-time results, next-fact range reduction, strict leader margin, and grouped scenario arithmetic matched an independent integer-cent oracle.

Only this report and `tests/test_intelligence_oracle.py` were authored by this reviewer in this cycle. No application code, provider configuration, infrastructure, or other agent's files were edited. No commit was made.

## Finding SCI-01 — contradictory baseline case identity

Severity: P2. Status: **resolved and regression verified**.

The original `derive_case` rejected alternative baselines but did not check a joined-source baseline's declared case identity. A synthetic internally consistent receipt with `case_context={"kind":"baseline","case_id":"different-case"}` was accepted inside a packet whose outer `case_id` was `case-under-review`. `make_case_packet` and `check_case_packet` both accepted it. This contradicts the packet's own declared lineage even though its arithmetic is correct; it is separate from source authentication.

Observed before the fix, via a PowerShell here-string piped to `.venv/Scripts/python.exe -`:

```text
{'packet_case_id': 'case-under-review',
 'declared_baseline_case_id': 'different-case',
 'verification': True}
```

The implementation owner added the joined-source baseline-context check at `prooflane/case_evidence.py:17`. The independent regression `test_case_packet_checks_math_against_independent_receipt_and_declared_baseline_identity` now checks all three cases: correct joined identity accepted, contradictory joined identity rejected, and reuse of an older original receipt as embedded evidence still accepted. That regression passed.

## Independent mathematical verification

The oracle uses Python integer cents and enumerates complete feasible assignments. Expected results do not call the engine's `_box`, `_leader`, Decimal summarizer, sensitivity, or residual-width formulas. It invokes the actual public engine functions to obtain the results under test.

The two parameterized exhaustive tests cover **216 boxes**: 108 with a shared contract and 108 with independent contract sources. Each box contains two source invoice records, including duplicate invoice IDs and both contract-date endpoints. Quantities range over `[1,1]` or `[1,3]`; billed-price cents over `[0,0]`, `[0,2]`, or `[2,3]`; contract-price cents over `[0,0]`, `[0,2]`, or `[1,3]`. Every supported integer/cent value within each selected interval is enumerated, not just corners.

| Claim tested | Independent comparison | Result |
|---|---|---|
| Tight joint total and row bounds | Actual minimum/maximum over all feasible assignments | PASS, 216 boxes |
| Positive-record flags | All/any feasible row values positive | PASS, 216 boxes |
| OAT endpoint totals and span | Full baseline vector with exactly one target changed | PASS, every target in all boxes |
| Guaranteed/possible next-fact width reduction | Partition complete feasible assignments by **every** possible resolved target value, then compare maximum/minimum remaining widths | PASS, every target in all boxes, including interior values |
| Exact minimum leader margin | Minimum candidate-minus-competitor difference across all assignments | PASS, 216 boxes |
| Strict-leader correctness and completeness | Exhaustive existence of a row strictly above the other at every feasible assignment | PASS, 216 boxes |
| Shared-price kink | A(q3,p.03), B(q1,p.05), c[.00,.04]: actual minimum margin -.02 at interior c=.03; endpoints alone give wrong minimum -.01 | PASS |
| Hidden interaction | Quantity OAT span zero at baseline, but shared contract change activates it; joint total 1.02 rather than a sum of separate deltas | PASS |
| Cap semantics | 25 targets available; 24 declared ranges accepted; 25 rejected; a shared target affects all bound rows | PASS |
| Maximum accepted amounts | One range shared by 500 rows at q999999 and p99999999.99 matches unbounded integer-cent products exactly | PASS |
| Internal packet lineage | Independent cents-derived receipt accepted; contradictory joined case identity rejected after SCI-01 fix | PASS |

Commands executed from `D:/projects/vultre`, exit code 0:

```powershell
.venv/Scripts/python.exe -m pytest -q tests/test_intelligence_oracle.py
# 7 passed in 0.31s

.venv/Scripts/python.exe -m pytest -q tests/test_intelligence.py tests/test_intelligence_oracle.py tests/test_reconciliation.py tests/test_case_evidence.py
# 60 passed in 0.65s
```

These are actual local test outputs, not app/browser/cloud latency measurements. The mathematical argument explains why the endpoint shortcut is exact; the finite enumeration independently challenges its implementation. Neither establishes correctness for unsupported pricing models or undisclosed dependencies.

## Saved packet cross-check

Read actual saved `artifacts/transformation/reference-case.json` and `sandbox-case.json`. Both passed the current `check_case_packet`. A separate stdlib integer-cent routine rebuilt the exact vendor/item/date join directly from the raw invoice/contract text, applied explicit exclusions/choices, and recomputed every alternative jointly. It enumerated **all 2,001 legal cent values** of the declared C1 range 65.00–85.00 in each packet, checking actual total extrema and the leader's worst margin.

| Quantity | Reference packet | Sandbox packet |
|---|---:|---:|
| Included rows | 7 | 7 |
| Baseline variance | 768.00 | 768.00 |
| Baseline billed | 7110.00 | 7110.00 |
| Shared price 80 alternative variance / billed | 368.00 / 7110.00 | 368.00 / 7110.00 |
| Joint price-and-volume alternative variance / billed | 568.00 / 10510.00 | 568.00 / 10510.00 |
| Exact total range | [148.00,1193.00] | [148.00,1193.00] |
| Width and single-source guaranteed reduction | 1045.00 | 1045.00 |
| Candidate's exact worst margin | -96.00 | -96.00 |
| Strict leader certified | false | false |

This independently verifies the artifact's supplied-data arithmetic. Reading a packet labeled sandbox does not authenticate Docker execution; this reviewer did not run Docker or Vultr in this cycle.

The packet cross-check was executed as the following PowerShell here-string body piped to `.venv/Scripts/python.exe -` (exit 0):

```python
import csv, io, itertools, json
from collections import defaultdict
from pathlib import Path
from prooflane.case_evidence import check_case_packet

def cent(value):
    whole, _, frac = value.partition('.')
    return int(whole)*100+int(frac.ljust(2,'0'))

def decoded(text):
    return [{k:v.strip() for k,v in r.items()} for r in csv.DictReader(io.StringIO(text))]

def values(rows):
    return tuple(r['q']*max(r['p']-r['c'],0) for r in rows)

def changed(rows, changes):
    out=[dict(r) for r in rows]
    for change in changes:
        target=change['target']
        if target.startswith('contract:'):
            for r in out:
                if r['group']==target[len('contract:'):]: r['c']=cent(change['value'])
        else:
            _, ordinal, field=target.split(':',2)
            out[int(ordinal)-2][{'quantity':'q','unit_price':'p','contract_price':'c'}[field]]=int(change['value']) if field=='quantity' else cent(change['value'])
    return out

for mode in ('reference','sandbox'):
    path=Path('artifacts/transformation')/(mode+'-case.json')
    packet=json.loads(path.read_text(encoding='utf-8'))
    assert check_case_packet(packet)['passed']
    s=packet['sources']; invoices=decoded(s['invoices_csv']); contracts=decoded(s['contracts_csv']); rows=[]
    for ordinal,r in enumerate(invoices,2):
        if str(ordinal) in s['exclusions']: continue
        eligible=[c for c in contracts if (c['vendor'],c['item_id'])==(r['vendor'],r['item_id']) and c['valid_from']<=r['invoice_date']<=c['valid_to']]
        selected=s['selections'].get(str(ordinal))
        candidates=[c for c in eligible if c['contract_id']==selected] if selected else eligible
        assert len(candidates)==1
        c=candidates[0]
        rows.append({'q':int(r['quantity']),'p':cent(r['unit_price']),'c':cent(c['contract_price']),'group':c['contract_id'],'source':ordinal})
    baseline=sum(values(rows)); billed=sum(r['q']*r['p'] for r in rows)
    assert (len(rows),baseline,billed)==(7,76800,711000)
    assert baseline==cent(packet['baseline']['summary']['total_variance'])
    alternatives=[]
    for a in packet['alternatives']:
        proposed=changed(rows,a['changes']); total=sum(values(proposed)); amount=sum(r['q']*r['p'] for r in proposed)
        assert total==cent(a['receipt']['summary']['total_variance'])
        assert amount==cent(a['receipt']['summary']['total_billed'])
        alternatives.append({'name':a['name'],'variance_cents':total,'billed_cents':amount})
    bound=packet['bounds'][0]; assert len(packet['bounds'])==1 and bound['target']=='contract:C1'
    feasible=[]
    for c in range(cent(bound['low']),cent(bound['high'])+1):
        feasible.append(values(changed(rows,[{'target':'contract:C1','value':f'{c//100}.{c%100:02}'}])))
    totals=[sum(v) for v in feasible]; lo,hi=min(totals),max(totals)
    intelligence=packet['intelligence']
    assert (lo,hi)==(14800,119300)==(cent(intelligence['low']),cent(intelligence['high']))
    leader=intelligence['leader']; a=leader['candidate_row']-2
    margin=min(v[a]-v[b] for v in feasible for b in range(len(rows)) if a!=b)
    signed_margin=int(leader['minimum_margin'].replace('.',''))
    assert margin==signed_margin and leader['certified']==(margin>0)
    assert cent(intelligence['review_queue'][0]['guaranteed_width_reduction'])==hi-lo
    print(json.dumps({'packet':str(path),'check_case_packet':'PASS','independent_source_join':'PASS','baseline_variance_cents':baseline,'baseline_billed_cents':billed,'alternatives':alternatives,'every_contract_cent_enumerated':len(feasible),'exact_total_range_cents':[lo,hi],'exact_leader_margin_cents':margin,'scope':'Artifact arithmetic checked; runtime provenance not authenticated'}))
```

Output for each packet reported `check_case_packet: PASS`, `independent_source_join: PASS`, `every_contract_cent_enumerated: 2001`, `exact_total_range_cents: [14800,119300]`, and `exact_leader_margin_cents: -9600`, with the alternative values in the table above.

## Claims and limitations

- Grouped extrema are tight for the declared Cartesian set of source targets; no sampling/probability interpretation is needed. Shared contract copies are correctly one variable.
- Next-fact priority measures interval narrowing after exact resolution. It is not a statistical value of information, a claim that evidence is obtainable, or a financial return.
- The leader certificate covers one candidate against all others. It does not promise an exact whole-list rank distribution; code labels strict certification correctly.
- The 24-range cap counts target declarations, including constant ones. It does not limit the number of rows affected by one shared source. Undeclared targets stay fixed.
- The exporter and verifier reuse the same `explore` implementation. Recalculation detects inconsistent packets but is not an independently implemented mathematical check; the separate integer-cent oracle provides that additional testing evidence.
- No source truth, legal applicability, causal explanation, or issuer/runtime authentication is established. Live Vultr usefulness remains outside this review. No new scientific novelty claim is justified.
- This cycle did not run browser, API HTTP, full repository, or deployment tests. Those checks have separate owners/evidence. The next final audit cycle must inspect any subsequent changes rather than reuse this report as a second review.

## Reviewed content hashes

SHA-256 captured after the tests and SCI-01 fix, using `Get-FileHash -Algorithm SHA256`:

| File | SHA-256 |
|---|---|
| `prooflane/intelligence.py` | `B793CCD575C89E9F047DC4594314FB0D343BAF45577F8D18B15C83CCB0CEE14D` |
| `prooflane/reconciliation.py` | `E1ED253E77E85E89D92BACE19D8A5843546B9EDB52B6D68633296DBC80CD5B5C` |
| `prooflane/case_evidence.py` | `91F8BC3DEC194BCB9B4F9CC2FEAE11D0D68B7C2B47380F35575C358D4B56AA93` |
| `tests/test_intelligence_oracle.py` | `16BE2FA324FD1A4E4C9E063FBB0C077E90FEB05D5A9470C732BDB5BB9644517D` |
| `artifacts/transformation/reference-case.json` | `7DB2031AB00D85D80CCE6F0AEAADBF2C1A8A4764CAF72BA6BAD7D12FC20A84AB` |
| `artifacts/transformation/sandbox-case.json` | `A208B4BCF0D6DAFE65634782ED4F8A42361AA1280807880FEC98822628A0BD36` |
