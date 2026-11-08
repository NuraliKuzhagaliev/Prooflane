# Independent methods review — initial decision evidence

Date: 2026-11-03. Agent: `v3_scientist`. Ownership: this artifact and `docs/INTELLIGENCE_METHODS.md` only. No application files edited; no dependencies installed; no cloud/model/browser execution asserted.

## Decision sent to implementation owner

1. Use exact Decimal endpoint calculations for one-at-a-time sensitivity, not derivatives at the positive-part boundary.
2. Treat a selected contract source as one shared target. A price change/range propagates to all bound invoices; independent duplicate contract cells would misrepresent the evidence dependency.
3. Total ranges are exact under the independent **source-target** box because every term moves in the same direction for each shared contract price. This is a set assumption, not statistical independence.
4. Interval overlap cannot establish a priority reversal for rows sharing a contract. Start with sufficient dominance certificates; optionally calculate exact pairwise bounds using contract endpoints and the two price breakpoints.
5. Never sum OAT deltas for general joint scenarios. The sample's quantity/contract joint change is a concrete counterexample.
6. Rank target spans with the declared ranges visible. No inferred probabilities, savings, causal claims, or expected value.
7. A useful optional addition is guaranteed/possible interval-width reduction when one source fact is resolved. It has exact formulas, but user benefit remains a hypothesis.

The implementation owner confirmed the joined input schemas, exact vendor/item eligibility with inclusive dates, explicit eligible choices for ambiguity, and contract-target propagation. The full specification and caveats are in `docs/INTELLIGENCE_METHODS.md`.

## Source inspection

Read `AGENTS.md`; only root AGENTS instructions were found in the scoped file search. Applied `hub-research` and `hub-innovation`, including `references/evidence.md` and `references/opportunities.md`. Inspected existing analysis, comparison, receipts, provider, related tests, the scenario contract, and the synthetic sample. Existing tests were read, not claimed as rerun.

Primary sources read through the web tool on 2026-11-03:

- [Python 3.13 Decimal documentation](https://docs.python.org/3.13/library/decimal.html): precision and string construction.
- [Saltelli and Annoni, 2010, original paper](https://www.andreasaltelli.eu/file/repository/PublishedPageNumbers.pdf): OAT interaction limitations.
- [Bertsimas and Sim, 2004, author-hosted original paper](https://www.mit.edu/~dbertsim/papers/melvyn/The-Price-Of-Robustness-OR52.pdf): uncertainty-set conservatism.
- [W3C PROV Primer](https://www.w3.org/TR/prov-primer/): evidence entities and derivations.
- [RFC 8785](https://www.rfc-editor.org/rfc/rfc8785.html): canonical representation for repeatable hashing/signing.

Source findings support design boundaries. The Prooflane formulas and counterexamples are direct derivations, not claims that the papers implemented this product. No published source was redistributed.

## Executed independent mathematical oracle

Environment: project `.venv/Scripts/python.exe`, PowerShell, working directory `D:/projects/vultre`. Input: `examples/invoices.csv` and synthetic small numeric cases. Command exit code: **0**. This imports only Python stdlib; it does not call `prooflane.summarize`, the app, Docker, or a provider.

Exact command body executed, piped as a PowerShell here-string to `.venv/Scripts/python.exe -`:

```python
import csv, io, itertools, json
from pathlib import Path
from decimal import Decimal, localcontext
D = Decimal
with localcontext() as ctx:
    ctx.prec = 28
    rows = list(csv.DictReader(io.StringIO(Path('examples/invoices.csv').read_text(encoding='utf-8-sig'))))
    def v(q,p,c): return D(q)*max(D(p)-D(c),D(0))
    baseline = sum(v(r['quantity'],r['unit_price'],r['contract_price']) for r in rows)
    billed = sum(D(r['quantity'])*D(r['unit_price']) for r in rows)
    original = v('40','85','72')
    sample = {'baseline':str(baseline),'billed':str(billed),'row3':str(original),
              'contract80':str(baseline-original+v('40','85','80')),
              'contract85':str(baseline-original+v('40','85','85')),
              'quantity80':str(baseline-original+v('80','85','72')),
              'joint_quantity80_contract80':str(baseline-original+v('80','85','80'))}
    assert sample == {'baseline':'1480.00','billed':'34353.00','row3':'520','contract80':'1160.00','contract85':'960.00','quantity80':'2000.00','joint_quantity80_contract80':'1360.00'}
    def group(c): return v('40','85',c)+v('10','82',c)
    assert [group(x) for x in ['72','80','70','90','78.40','78.39']] == list(map(D,['620','220','720','0','300.00','300.50']))
    # Finite-grid countercheck of the grouped monotone-bound and shared-price pair formulas.
    boxes = 0
    for qi,qj,pi,pj,cr in itertools.product([(1,1),(1,3)],[(1,1),(1,3)],[(0,0),(0,2),(2,3)],[(0,0),(0,2),(2,3)],[(0,0),(0,2),(1,3)]):
        feasible = [(v(a,b,c),v(d,e,c)) for a in range(qi[0],qi[1]+1) for b in range(pi[0],pi[1]+1) for d in range(qj[0],qj[1]+1) for e in range(pj[0],pj[1]+1) for c in range(cr[0],cr[1]+1)]
        lower = v(qi[0],pi[0],cr[1])+v(qj[0],pj[0],cr[1])
        upper = v(qi[1],pi[1],cr[0])+v(qj[1],pj[1],cr[0])
        assert (lower,upper)==(min(a+b for a,b in feasible),max(a+b for a,b in feasible))
        low_points = set(cr)|{x for x in [pi[0],pj[1]] if cr[0]<=x<=cr[1]}
        high_points = set(cr)|{x for x in [pi[1],pj[0]] if cr[0]<=x<=cr[1]}
        dlo=min(v(qi[0],pi[0],c)-v(qj[1],pj[1],c) for c in low_points)
        dhi=max(v(qi[1],pi[1],c)-v(qj[0],pj[0],c) for c in high_points)
        assert (dlo,dhi)==(min(a-b for a,b in feasible),max(a-b for a,b in feasible))
        boxes+=1
    print(json.dumps({'python_arithmetic_oracle':'PASS','sample':sample,'group_C1_at72':str(group('72')),'group_C1_at80':str(group('80')),'bounded_shared_contract_boxes_checked':boxes,'scope':'Independent mathematical oracle only; no new application/browser/cloud claim'},indent=2))
```

Captured output:

```json
{
  "python_arithmetic_oracle": "PASS",
  "sample": {
    "baseline": "1480.00",
    "billed": "34353.00",
    "row3": "520",
    "contract80": "1160.00",
    "contract85": "960.00",
    "quantity80": "2000.00",
    "joint_quantity80_contract80": "1360.00"
  },
  "group_C1_at72": "620",
  "group_C1_at80": "220",
  "bounded_shared_contract_boxes_checked": 108,
  "scope": "Independent mathematical oracle only; no new application/browser/cloud claim"
}
```

The 108 boxes enumerate tiny integer-valued target sets, including zero prices, constant and varying quantities, shared-price dependence, and hinge crossings. This is a finite countercheck in addition to the monotonicity/piecewise-linearity proofs. It is not a benchmark, production coverage estimate, or substitute for testing the implementation on accepted cent-valued inputs and API flows.

## Specific challenges retained

- A fixed-formula code-generating LLM remains analytically optional. Real AI usefulness requires a new constrained task and genuine evaluation; added deterministic methods do not justify AI performance claims.
- Shared-source IDs must be unambiguous. `contract:C1` requires unique contract IDs, while duplicate invoice IDs must remain separate source records.
- A self-hashed, internally consistent packet can still describe false evidence. Hash validity and Decimal correctness cannot authenticate source truth or runtime execution.
- Pairwise feasible extrema need not be simultaneously attainable for an entire ranked list. A rank envelope must not imply an exact joint rank distribution.
- A difference interval spanning zero does not prove a legal tie because money is quantized to cents.
- OAT importance changes with declared ranges. Data collection cost, source credibility, and probability of error are not supplied, so there is no supported expected-value optimizer.

## Status and handoff

**Completed:** decision-grade methods, primary-source checks, explicit formulas/proofs, manual golden cases, independent small-grid countercheck, and implementation acceptance criteria.

**Not performed by this agent:** new application implementation/testing, browser journeys, offline-container execution, live Vultr calls, user research, provider evaluation, or package installation. Those statuses require their own actual evidence. Continue with implementation and its verification; no additional research is needed to choose the core mathematical method.
