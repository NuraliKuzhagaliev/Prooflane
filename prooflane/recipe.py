"""Reviewed fixed recipe, distinct from model-generated code and host verifier."""
RECIPE = '''import csv, json
from decimal import Decimal
with open('/tmp/input.csv', encoding='utf-8-sig', newline='') as source:
    rows = list(csv.DictReader(source))
billed_cents = 0
variance_cents = 0
findings = []
for record, row in enumerate(rows, 2):
    units = int(row['quantity'])
    price = int(Decimal(row['unit_price'].strip()) * 100)
    agreed = int(Decimal(row['contract_price'].strip()) * 100)
    billed_cents += units * price
    excess = units * max(0, price - agreed)
    if excess:
        variance_cents += excess
        findings.append({'row': record, 'variance': f'{excess // 100}.{excess % 100:02d}'})
def usd(cents):
    return f'{cents // 100}.{cents % 100:02d}'
print(json.dumps({'row_count': len(rows), 'total_billed': usd(billed_cents),
    'total_variance': usd(variance_cents), 'findings': findings}))
'''
