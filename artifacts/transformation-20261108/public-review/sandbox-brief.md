# Prooflane review brief

HTTP review acceptance synthetic

Case: 9cae5f8a-e8d4-440e-a07f-ca03780c2781 · revision 1
Baseline run: 29d82069-91fe-4edb-8f95-17139f680637 · mode sandbox

Positive price variance: USD 768.00
Included billed: USD 7110.00; excluded billed: USD 250.00; unresolved billed: USD 0.00.
A positive difference is a review signal, not proof of overbilling or recovered savings.

## Shared source groups

- C1 · Atlas: 3 rows, variance USD 620.00; invoice source rows 2, 3, 9.
- C2 · Nova: 1 rows, variance USD 96.00; invoice source rows 4.
- C2R · Nova: 1 rows, variance USD 32.00; invoice source rows 5.
- C3 · Meridian: 2 rows, variance USD 20.00; invoice source rows 6, 8.

## Source decisions

- Invoice source row 5 INV504: selected · C2R.
- Invoice source row 7 INV506: excluded · No active contract in this fictional fixture..

## Source-quality checks

No identical financial/date source-line groups detected by this limited check. This is not a fraud clearance.

## Declared uncertainty

No ranges declared. Inputs fixed at their original values.
Conditional total range: USD 768.00 to 768.00. These ranges are not probabilities.

## Executed alternatives

None executed.

## Price that changes original priority

One shared contract price varies in whole cents. All other inputs stay at the original baseline values.
- Last strict priority, USD 82.59: unique · INV501 (record 2).
- First changed state, USD 82.60: tie · INV501 (record 2), INV503 (record 4).
- One cent further, USD 82.61: unique · INV503 (record 4).

## Verification and limits

This brief is a readable handoff, not a signed or independently verified artifact. Download the corresponding JSON case packet and run:

python scripts/verify_receipt.py prooflane-case-9cae5f8a-e8d4-440e-a07f-ca03780c2781.json

The verifier reconstructs source links, arithmetic and declared assumptions. It does not authenticate an issuer, a supplied contract or a host runtime.
CSV and brief include source data. Share them only where those data may be shared.
