# Prooflane review brief

November supplier review · synthetic

Case: a4f0f88d-df7c-40d0-a745-a5cb6becff8a · revision 2
Baseline run: 49098066-79a7-4cb3-8fc9-dd7f2c8d5aaf · mode sandbox

Positive price variance: USD 768.00
Included billed: USD 7110.00; excluded billed: USD 3650.00; unresolved billed: USD 0.00.
A positive difference is a review signal, not proof of overbilling or recovered savings.

## Shared source groups

- C1 · Atlas: 3 rows, variance USD 620.00; invoice source rows 2, 3, 9.
- C2 · Nova: 1 rows, variance USD 96.00; invoice source rows 4.
- C2R · Nova: 1 rows, variance USD 32.00; invoice source rows 5.
- C3 · Meridian: 2 rows, variance USD 20.00; invoice source rows 6, 8.

## Source decisions

- Invoice source row 5 INV504: selected · C2R.
- Invoice source row 7 INV506: excluded · No active contract in this fictional review..
- Invoice source row 10 INV501: excluded · Intentional synthetic repeat of source row 2; manually excluded after source review..

## Source-quality checks

- Confirm repeated lines for INV501, invoice source rows 2, 10: Same invoice ID, vendor, item, date, quantity and billed price. Could be legitimate repeated lines; confirm the source. Nothing was excluded automatically.

## Declared uncertainty

No ranges declared. Inputs fixed at their original values.
Conditional total range: USD 768.00 to 768.00. These ranges are not probabilities.

## Executed alternatives

- Confirmed shared price 80: USD 368.00; delta USD -400.00; run f7e283e2-7e44-48ba-ac67-fec5c7af9c19.
  - Contract C1 → 80.00.

## Price that changes original priority

One shared contract price varies in whole cents. All other inputs stay at the original baseline values.
- Last strict priority, USD 82.59: unique · INV501 (record 2).
- First changed state, USD 82.60: tie · INV501 (record 2), INV503 (record 4).
- One cent further, USD 82.61: unique · INV503 (record 4).

## Verification and limits

This brief is a readable handoff, not a signed or independently verified artifact. Download the corresponding JSON case packet and run:

python scripts/verify_receipt.py prooflane-case-a4f0f88d-df7c-40d0-a745-a5cb6becff8a.json

The verifier reconstructs source links, arithmetic and declared assumptions. It does not authenticate an issuer, a supplied contract or a host runtime.
CSV and brief include source data. Share them only where those data may be shared.
