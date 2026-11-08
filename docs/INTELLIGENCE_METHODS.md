# Prooflane intelligence methods

Date: 2026-11-03. Scope: exact, deterministic analysis of supplied invoice and contract evidence. This is a methods specification and acceptance oracle; it does not assert that every optional method below is implemented or that cloud/model integration has run.

## Decision

Build the next analytical layer around **shared contract assumptions**: identify which source contract governs each invoice, calculate which declared assumptions change the answer most, and show whether review priorities survive the declared ranges. Keep the original evidence and every alternative immutable. This adds useful analysis without requiring a live model, a new provider, or statistical claims unsupported by data.

The core is exact arithmetic, group-aware scenarios, one-at-a-time sensitivity, and attainable total bounds over a declared set. A stronger optional extension is an exact certificate that one row outranks another even when both share an uncertain contract price. Another is the guaranteed/possible narrowing of the total interval after a source fact is resolved. Neither is a new scientific method or evidence of market differentiation.

Inspected baseline: `prooflane/analysis.py`, `comparison.py`, `receipts.py`, `provider.py`, their existing tests, `docs/SCENARIO_CONTRACT.md`, and `examples/invoices.csv`. The original engine has a fixed positive-variance formula, one-cell hypothetical scenarios, independent Decimal output checks, and hash-linked receipts. The original provider prompt fixes that same formula; review context cannot change it. Existing code and test assertions were inspected, not counted as freshly executed integration tests.

## Evidence preparation defines the calculation

The proposed matching schema is:

```text
invoices:  invoice_id,vendor,item_id,invoice_date,quantity,unit_price,notes
contracts: contract_id,vendor,item_id,valid_from,valid_to,contract_price
```

An invoice is eligible for a contract only when vendor and item ID match exactly under the declared parser normalization, and `valid_from <= invoice_date <= valid_to`. Dates must be valid calendar dates serialized as `YYYY-MM-DD`. Case folding, fuzzy text similarity, undocumented unit conversion, or an LLM guess must not silently establish eligibility. This is an intentionally narrow matching rule; it does not interpret contractual applicability, tax, currency, volume tiers, or discounts.

Require unique nonempty contract IDs if a target is addressed as `contract:C1`. Duplicate invoice IDs are not row identity: preserve raw source-record ordinals. A source record means a parsed CSV record, with the header numbered 1, not necessarily a physical line when quoted cells contain newlines.

Zero eligible contracts requires repaired input or an explicit exclusion with a reason. Multiple eligible contracts require an explicit choice of one eligible contract. Never resolve ambiguity by file order, by the lowest price, or by whichever price creates the largest finding. Display analyzed/excluded/source counts and exclusions; an analyzed-subset total is not a full-file total.

Persist a mapping from every canonical analysis record to its raw invoice record and selected raw contract record. Contract-price targets refer to the contract source and propagate to **all** invoices bound to that source. Invoice quantity and billed unit price target one source invoice. A joined invoice must not also expose an independent per-row contract-price assumption. Price-only scenarios preserve the eligibility rules and selected mapping. A changed vendor, item, or date requires a new evidence review.

## Exact model and numeric domain

For analyzed row `i`, let `g(i)` be its selected contract, `q_i` its positive integer quantity, `p_i` its billed unit price, and `c_g` the selected contract price:

```text
v_i = q_i * max(p_i - c_g(i), 0)
V   = sum_i(v_i)
B   = sum_i(q_i * p_i)
```

`V` is positive price variance under the supplied values. Negative price differences never offset positives. `B` is billed value for the specified analysis scope. Neither quantity is recovered savings, liability, fraud probability, or a payment instruction.

Use validated decimal strings or integer cents, never floating-point intermediates. Quantity remains in `1..999999`; money remains nonnegative, at most two decimal places, within the parser's eight-integer-digit bound. At most 500 analyzed rows means sums need at most 19 significant decimal digits. An explicit local Decimal precision of 28 is sufficient for the sums/products here; trapping `Inexact` during verification is a useful guard. Decimal still rounds when an operation exceeds its precision, and constructing it from a binary float preserves that float's approximation. [Python 3.13 Decimal documentation](https://docs.python.org/3.13/library/decimal.html)

Money outputs have exactly two fractional digits. Ratios, percentages, and average prices are unnecessary to these guarantees; adding them requires a separately declared rounding policy. An arithmetic verifier should use integer cents where practical to give implementation diversity, and must independently check every source row rather than only the final total.

## One-at-a-time sensitivity and review targets

Let `x0` be the verified baseline target vector. A target is either one invoice quantity, one billed price, or one shared contract price. For a user-declared target range `[l_t,u_t]`, hold every other target at its baseline value and calculate:

```text
delta_low(t)  = V(x0 with target t=l_t) - V(x0)
delta_high(t) = V(x0 with target t=u_t) - V(x0)
span(t)       = abs(V(x0 with t=u_t) - V(x0 with t=l_t))
```

Use full exact endpoint recomputation, including the `max` boundary. The response increases with quantity/billed price and decreases with contract price, so label the endpoint values as the *low/high assumption*, not automatically the low/high result.

For shared contract `g`, the span is:

```text
span(g) = sum_{i:g(i)=g} q_i *
          [max(p_i-l_g,0) - max(p_i-u_g,0)]
```

Rank review targets by descending monetary span, with a stable target-ID tie-break for presentation. Show affected source records and the actual declared range beside every score. Grouping prevents one contract evidence check from being counted as multiple independent tasks. Keep missing/ambiguous evidence in a separate prerequisite queue: an absent justified range cannot honestly be assigned a numeric influence score.

This ranking answers which *declared one-target change* has the greatest arithmetic effect. It does not measure the likelihood that a value is wrong, the cost of checking it, expected financial recovery, or a causal effect. A wider chosen range can make any target look more influential. Do not invent ranges from a generic percentage and present them as evidence. If an example preset is offered, identify it as a hypothetical preset and require its inclusion in the saved assumptions.

One-at-a-time analysis can hide interactions; the limitation is established in the sensitivity-analysis literature. Here its narrow role is an exactly computed baseline explanation, supplemented by simultaneous bounds and joint scenarios. It is not a global importance index. [Saltelli and Annoni, 2010, original paper](https://www.andreasaltelli.eu/file/repository/PublishedPageNumbers.pdf)

## Exact total bounds with shared contracts

Let each invoice quantity and billed price have a closed range, and let each contract source have one shared price range. Unspecified targets are fixed at baseline. Require `lower <= baseline <= upper`; enforce the same type/range constraints as ordinary inputs. A constant interval is allowed, but an all-constant specification conveys no sensitivity.

The admissible set is a Cartesian product **over source targets**, not over duplicate invoice copies of a contract price. This means all target combinations in the declared box are allowed; it is not an assumption about statistical independence and it supplies no probability distribution.

```text
L_i = q_i_low  * max(p_i_low  - c_g(i)_high, 0)
U_i = q_i_high * max(p_i_high - c_g(i)_low,  0)
L   = sum_i L_i
U   = sum_i U_i
```

These are attainable extrema for this declared set, including shared contracts. Proof: every row is nondecreasing in quantity and billed price, and nonincreasing in its selected contract price. The single assignment of every quantity/price to its low endpoint and every contract to its high endpoint attains all row minima simultaneously. The opposite assignment attains all maxima. Sharing a contract causes no conflict because all affected rows move in the same direction. Complexity is linear in analyzed rows, with no sampling.

The same argument gives billed bounds `sum(q_low*p_low)` and `sum(q_high*p_high)`, and positive-finding-count bounds `count(p_low>c_high)` and `count(p_high>c_low)` because all quantities are positive. Keep each metric's endpoint assignment and scope explicit.

Label the result **range under the declared assumptions**. It is not a confidence interval, prediction interval, credible interval, or empirical error bar. Actual inputs outside the declared set are not covered. Arbitrary boxes can be conservative relative to real dependencies; uncertainty-set design is a substantive modeling decision, not a free accuracy claim. The robust-optimization literature discusses this conservatism, but Prooflane is not implementing its probabilistic guarantees. [Bertsimas and Sim, 2004, sections 1–2](https://www.mit.edu/~dbertsim/papers/melvyn/The-Price-Of-Robustness-OR52.pdf)

If a future model adds coupled quantity totals, cross-contract constraints, volume pricing, or common discounts, the proof must be revisited. These formulas can then be an outer enclosure when the feasible set is contained in the box, but the extrema need not be attainable. Counterexample: one shared fact `p=c` in `[10,20]` always gives zero variance for quantity 1; treating `p` and `c` as independent gives the larger enclosure `[0,10]`.

## Priority stability is a partial order

For two rows, `L_i > U_j` is a sound sufficient certificate that row `i` has greater variance throughout the declared set. Overlap means this *marginal-interval test* does not settle the comparison. It does not prove a possible reversal, particularly when the rows share a contract.

Example: A has quantity 10 and billed price 20; B has quantity 10 and billed price 15; both use one contract price in `[10,18]`. A's interval is `[20,100]`, B's is `[0,50]`, yet A always exceeds B. The common contract cannot be simultaneously 18 for A and 10 for B.

An optional exact shared-contract pair certificate is inexpensive. To minimize `v_i-v_j`, use i's low quantity/price and j's high quantity/price, and define:

```text
D_min(c) = q_i_low*max(p_i_low-c,0) - q_j_high*max(p_j_high-c,0)
```

Evaluate it at the shared contract endpoints and at `p_i_low`/`p_j_high` when those prices lie inside the range; take the minimum. For the maximum, use i's high quantity/price and j's low quantity/price, and evaluate endpoints plus the corresponding two price breakpoints. The function is piecewise linear, so extrema occur at those points. Every breakpoint is a legal cent value. For separate independent contract targets, the exact pair bounds are simply `[L_i-U_j, U_i-L_j]`.

Interpretation of an exact difference interval `[d_min,d_max]`:

| Condition | Permitted statement |
|---|---|
| `d_min > 0` | i is strictly ahead of j for every declared combination |
| `d_min >= 0` | i is never below j; equality is not ruled out |
| `d_max < 0` | j is strictly ahead of i for every declared combination |
| `d_min < 0 < d_max` | Feasible combinations give opposite strict orders for this pair |
| Otherwise | Report the bounds; do not manufacture a strict order |

An interval straddling zero does not establish an attainable exact tie on the cent grid. For A `(q=1,p=.03)`, B `(q=3,p=.02)`, and shared `c=0,.01,.02`, differences are `-.03,-.01,+.01`; there is no legal tie.

Display certified pair relationships or distinguish a baseline ranking from unresolved comparisons. If a rank envelope is displayed, `1 + number definitely ahead` is a lower bound and `1 + number possibly ahead` is an upper bound under strict competition ranking. With shared targets, individual pairwise witnesses may require different values, so the rank endpoints are not generally attainable. Label such an envelope as a bound, not an exact rank distribution. No probabilities follow from it.

Scenario ranking also needs an explicit objective. Sorting scenarios by lower calculated variance is only an ordering of supplied assumptions. A lower quantity can reduce both variance and billed value without representing a better purchasing or payment decision. Always show billed delta, variance delta, affected rows, and scope. Do not label the first scenario the economically optimal action.

## Joint scenarios and break-even thresholds

Each scenario starts from the same immutable verified baseline. Apply all declared target edits together, propagate shared-contract changes, and recompute every affected row. Reject duplicate/conflicting edits of the same target. One batch can contain several separately named alternatives; alternatives are not sequential edits to one another.

Summing one-at-a-time deltas is only justified when the edits affect disjoint row sets, or when the relevant expression is proven additive on the entire path. It is not a general algorithm. Quantity multiplied by a changed price gap creates an interaction; the positive-part boundary creates another source of nonadditivity.

For the existing sample's record 3 `(q=40,p=85,c=72)`, baseline variance is 520. Changing quantity to 80 gives 1040; changing contract price to 80 gives 200. Their separate deltas sum to `+520-320=+200`. The joint result is 400, whose actual delta is `-120`. Summing deltas overstates the joint result by 320. Even with fixed quantity, a baseline `(1,10,9)` has variance 1: changing price to 8 and contract to 11 separately gives two deltas of -1, but the joint delta is only -1.

For a single row with positive quantity, zero positive variance starts at contract price `c=p`, or billed price `p=c`. Changing quantity alone cannot eliminate a positive gap within the supported positive-quantity domain. For a shared contract, the smallest price eliminating all currently bound rows is `max_i p_i` over that group. These are arithmetic thresholds, not suggested or authenticated contract terms.

Optional extension: a user-declared nonnegative variance cap can be inverted with integer-cent binary search on the shared contract price because group variance is monotone. Report the smallest legal price meeting the cap and verify that the previous cent fails, where a previous cent exists. Include unaffected-row variance when the cap applies to the whole review; a cap below that fixed remainder is infeasible through this contract alone. This is a deterministic decision boundary, not a negotiation recommendation.

## Optional: which fact would narrow the range?

One-at-a-time span is not the same as the benefit of resolving an uncertain source. Let `W=U-L`. For target `t`, fix it to `z` and recompute the simultaneous residual width `W_t(z)`, retaining all other ranges. For this formula, `W_t(z)` is monotone in z: nondecreasing for quantity/price and nonincreasing for a contract price, including a shared contract group. The slope follows from the nonnegative quantity bounds and each positive-part breakpoint.

Thus only the two target endpoints are needed:

```text
guaranteed_width_reduction(t) = W - max(W_t(l_t), W_t(u_t))
possible_width_reduction(t)   = W - min(W_t(l_t), W_t(u_t))
```

These quantities describe interval narrowing after learning that fact exactly, regardless of which allowed value is learned. They do not estimate the probability, cost, or expected monetary value of obtaining that evidence. The guarantee remains conditional on the declared set and correct source grouping.

Counterexample to relying on OAT alone: baseline `(q=1,p=10,c=10)`, ranges `q=[1,100]`, `p=[10,11]`, fixed `c=10`. Baseline OAT quantity span is zero, but the joint range is `[0,100]`; confirming quantity 1 narrows it to `[0,1]`. A second useful product experiment is whether such an explanation helps reviewers choose the next source to check. User benefit remains a hypothesis until observed.

## Receipt and provenance requirements

An export must contain enough evidence to reproduce eligibility, source mapping, assumptions, and every result offline:

1. Original invoice and contract bytes/text and their hashes; exact parser/matching method version.
2. Selected eligible contract for each included invoice, explicit exclusions/reasons, and raw-to-analysis record mapping.
3. Baseline receipt identity/hash and the complete declared target set, endpoint values, scenario edits, and before-values.
4. The method identifier/version, numeric/rounding domain, source grouping, and analytical scope.
5. Recomputed per-row results, group impacts, bounds, scenario deltas, and any priority certificates.
6. Honest execution provenance: these methods are trusted deterministic arithmetic with zero model calls; the baseline's execution mode is a separate fact.

A verifier must reparse the raw evidence, repeat matching and eligibility checks, reconstruct the mapping, apply only declared changes, and recalculate analytical results. Reject a bundle with recomputed outer hashes but a wrong eligible match, missing affected invoice, hidden source edit, changed range, invented exclusion, forged span, or false ranking certificate. Do not merely check hashes or rerun the export producer's trusted answer.

W3C PROV separates entities, activities, agents, and derivations; that vocabulary motivates keeping original evidence, transformed evidence, and the generating calculation distinct. Prooflane need not add RDF or claim PROV conformance to preserve that distinction. [W3C PROV Primer, 2013, sections 2–3](https://www.w3.org/TR/prov-primer/)

Hashing requires a specified serialization. The existing `canonical()` is a project JSON convention; do not call it RFC 8785 compliant without implementing that specification. Preserve its schema version and reject non-finite values. RFC 8785 explains why canonical representation is useful for repeatable cryptographic operations; it does not turn a self-hashed receipt into source authentication. [RFC 8785, 2020, sections 1 and 3](https://www.rfc-editor.org/rfc/rfc8785.html)

Hashes bind the supplied values and declared results. A person can fabricate a consistent input, output, and new hash. Arithmetic verification does not authenticate the contract, its issuer, its legal applicability, the execution host, or a model call. Missing or unavailable Vultr execution stays NOT_RUN/blocked according to actual evidence; deterministic intelligence must not be marketed as a successful live AI run.

## Golden cases and acceptance

These are synthetic arithmetic expectations. The independent stdlib oracle recorded in `artifacts/transformation-review/scientist-initial.md` checked the existing sample values and 108 small shared-contract boxes. It did not execute the new app, browser, container, or model.

| Case | Expected result |
|---|---|
| Existing 24-record sample | Billed 34353.00; positive variance 1480.00; 6 positive records |
| Existing record 3, contract 72 to 80 | Row 520.00 to 200.00; total 1160.00; delta -320.00; billed unchanged |
| Existing record 3, contract to 85 or 90 | Row 0.00; total 960.00; positive count 5 |
| Existing record 3, quantity 40 to 80 | Row 1040.00; total 2000.00; billed 37753.00 |
| Existing record 3, joint quantity 80 and contract 80 | Row 400.00; total 1360.00; variance delta -120.00; billed 37753.00 |
| Existing record 3 ranges q[20,60], p[80,90], c[70,90], others fixed | Row [0.00,1200.00]; total [960.00,2160.00] |
| Same range case, OAT spans at original values | quantity 520.00; billed-price 400.00; contract-price 600.00 |
| C1 shared by A(q40,p85) and B(q10,p82), c72 | Group 620.00 |
| C1 changes 72 to 80 | A 200.00, B 20.00; group 220.00; delta -400.00; both source links retained |
| C1 range [70,90], fixed quantities/billed prices | Group exact range [0.00,720.00] |
| C1 range [70,80] | Group exact range [220.00,720.00] |
| C1 zero-variance threshold | 85.00 |
| C1 cap 300.00 | First satisfying cent 78.40 gives 300.00; 78.39 gives 300.50 |
| Shared contract A(q10,p20), B(q10,p15), c[10,18] | Marginal intervals overlap; exact A-minus-B range [20.00,50.00], so A always ahead |
| One shared contract reused on multiple dates | All selected bindings change together; unselected overlapping contracts do not change |

Required acceptance goes beyond these examples:

- Every source record is matched or explicitly excluded; overlapping eligibility blocks until a valid choice, and inclusive boundary dates are checked.
- Contract target changes and ranges propagate to every bound invoice, including zero-variance rows that can become positive; unrelated rows remain identical.
- Tiny cent-grid exhaustive cases agree with the interval/pair formulas; large accepted amounts remain exact; constant ranges collapse to baseline; reversed/out-of-domain ranges fail.
- Batch outputs equal full joint recomputation and preserve the baseline. Duplicate targets, stale baseline hashes, hidden edits, and source/target ID confusion fail.
- Each certified ranking is checked against its declared set. Shared-source interval overlap is never described as a proven reversal. Ties have a declared display policy.
- Downloaded exports verify after server data are unavailable; rehashed semantic forgeries fail; foreign-session exports remain inaccessible.
- UI tests verify source links, exclusion scope, signed deltas, range labels, and accurate deterministic/model provenance. Those runs must be recorded separately from these mathematical checks.

## Model usefulness, priorities, and stopping rule

### Exact one-price priority boundary, implemented 8 November 2026

`prooflane/priority.py` fixes all fields at the original baseline and varies the unique leading invoice's contract-price target, including all invoices sharing that target. This is a separate question from robustness under the user's declared ranges. For price `c` in integer cents, each affected row has amount `q * max(p - c, 0)` in cents. Unaffected rows retain their original amounts. Only accepted whole-cent prices from 0 to 9,999,999,999 cents are searched.

For each challenger the set where the candidate is positive and strictly ahead is an interval: a fixed challenger gives a threshold; a shared challenger gives a difference of two hinge functions, whose positive region is an interval after splitting at their billed prices. Intersecting those intervals gives an interval containing the original price. Two binary searches find its inclusive endpoints, with integer arithmetic and no floating-point tolerance. Every boundary is recomputed against every included record; invoice IDs are not assumed unique.

The export records the last strict price, first changed price and one cent further. The first change can be a tie, a direct switch or elimination of all positive differences. Original ties, no positive differences and a single invoice are explained rather than assigned an invented unique priority. The offline verifier reconstructs the complete result from source bindings. The synthetic C1 example gives INV501 first at $82.59, INV501/INV503 tied at $82.60, and INV503 first at $82.61. `tests/test_priority.py` compares endpoints and witnesses with independent enumeration over 576 small cent-grid fixtures, including shared targets and duplicate IDs.

This is conditional arithmetic for the declared formula, not proof of a valid contract, a financial recommendation, a causal forecast or a claim of scientific novelty. Its effect on reviewer task completion has not been measured.

The original LLM writes code for a formula that a short fixed implementation already computes and verifies. That provides an isolated code-generation demonstration if the provider actually runs, but it does not establish superior analytical insight. More deterministic sensitivity features do not erase this limitation.

An honest future model role is to propose candidate source mappings, identify missing evidence, convert reviewer intent into a constrained scenario specification, or draft explanations tied to validated source IDs. Candidate mappings must remain suggestions; the deterministic matcher and an explicit eligible choice establish the calculation. New model usefulness should be measured on a held-out set with human-checked matches/claims, source-citation accuracy, abstention on ambiguity, schema rejection, latency/cost, and reviewer task completion. No such evaluation has occurred in this methods review. Keep the existing Vultr boundary and do not add a provider or costs to unblock a demo.

| Priority | Proposal | Expected effect and risks | Acceptance / experiment |
|---|---|---|---|
| Core | Evidence matching, exclusions, shared contract lineage | Correct source dependency; more input work is a usability risk | Boundary/ambiguity/propagation cases; reviewers can trace each result |
| Core | Joint scenarios, grouped OAT spans, exact total ranges | More useful conditional arithmetic; chosen ranges can dominate rankings | Golden arithmetic, tiny-grid checks, semantic-forgery rejection |
| Next | Shared-contract pairwise priority certificates | Explain stable priorities that marginal intervals miss | Counterexample above plus exhaustive pair cases; user can explain label |
| Optional | Guaranteed/possible interval narrowing per source | Help decide which fact to check; benefit is unvalidated and must not be sold as expected savings | Fixed baseline tasks comparing next-evidence selections with/without it |
| Later | Model-assisted proposals with validated citations | Reduce preparation work if actual measured quality warrants it | Genuine provider access and held-out evaluation; current gate NOT_RUN |

Do not add Monte Carlo, Sobol indices, confidence scores, causal attribution, Bayesian expected value, anomaly probabilities, or automated payment recommendations to this version. The data do not supply defensible distributions, causal identification, or action utilities. Do not add an optimizer merely to select the smallest hypothetical variance. A few exact, source-linked methods are sufficient for the present decision.

Research stops here: the implementation choice is supported, formulas have explicit assumptions and counterexamples, and remaining uncertainty concerns actual implementation behavior and user utility. Evidence that would change the recommendation includes tiered contracts/currency conversion, coupled quantities, frequent ambiguity the schema cannot resolve, or observed reviewers preferring another workflow. Those require a revised model or an experiment, not a stronger label on these results.

## Source record

All external sources accessed 2026-11-03. No external package was installed, and no external source implementation was copied. Equations specific to Prooflane and counterexamples above are independently derived from its declared formula; they are not attributed as scientific novelty.

| ID | Kind | Source and locator | Supported claim / limit |
|---|---|---|---|
| S1 | Verified primary documentation | [Python 3.13 Decimal](https://docs.python.org/3.13/library/decimal.html), introduction, context objects, floating-point notes; page identifies 3.13.18 | Exact decimal representation and configurable finite precision; not a blanket guarantee for arbitrary operations |
| S2 | Verified primary paper | [Saltelli and Annoni (2010)](https://www.andreasaltelli.eu/file/repository/PublishedPageNumbers.pdf), abstract and discussion of OAT; DOI 10.1016/j.envsoft.2010.04.012 | OAT's interaction/coverage limitation; does not prohibit explicitly scoped deterministic endpoint comparisons |
| S3 | Verified primary paper | [Bertsimas and Sim (2004)](https://www.mit.edu/~dbertsim/papers/melvyn/The-Price-Of-Robustness-OR52.pdf), pp.35–37; DOI 10.1287/opre.1030.0065 | Uncertainty sets involve robustness/conservatism choices; their additional probabilistic assumptions are not imported |
| S4 | Verified primary specification | [W3C PROV Primer](https://www.w3.org/TR/prov-primer/), W3C Working Group Note, 2013-04-30, sections 2–3 | Entities, activities, agents, and derivations provide provenance vocabulary; no claim that provenance proves truth |
| S5 | Verified primary specification | [RFC 8785](https://www.rfc-editor.org/rfc/rfc8785.html), June 2020, sections 1 and 3 | Canonical serialization supports repeatable hashing/signing; current project serializer is not asserted to implement JCS |
| L1 | Verified inspected local code | `prooflane/analysis.py`, `comparison.py`, `receipts.py`, `provider.py` | Fixed formula and existing scope described above; inspection is not execution |
| D1 | Derived mathematical result | Model, bounds, pairwise proof, and counterexamples in this document | Conditional guarantees on supplied values and the stated domain; no empirical or causal claim |
| H1 | Hypothesis | Evidence-first review queue and interval narrowing | Could help reviewers prioritize source checks; requires observed user validation |
| R1 | Recommendation | Core/next/optional ordering above | Prioritizes exact methods that fit the current evidence and zero-budget constraints |
