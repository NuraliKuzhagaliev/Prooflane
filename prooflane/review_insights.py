"""Deterministic review aids and human handoffs; never a payment decision."""
import csv
import io
from collections import defaultdict
from decimal import Decimal

from .analysis import parse_csv


def amount(value):
    return f"{value:.2f}"


def review_insights(source):
    records = source['records']
    billing = {key: Decimal(0) for key in ('total_billed', 'included_billed', 'excluded_billed', 'unresolved_billed')}
    duplicates, rivals = defaultdict(list), []
    for record in records:
        billed = Decimal(record['quantity']) * Decimal(record['unit_price'])
        billing['total_billed'] += billed
        state = record['status']
        key = 'excluded_billed' if state == 'excluded' else 'unresolved_billed' if state in {'unmatched', 'ambiguous'} else 'included_billed'
        billing[key] += billed
        signature = tuple(record.get(key, '') for key in ('invoice_id', 'vendor', 'item_id', 'invoice_date')) + (
            Decimal(record['quantity']), Decimal(record['unit_price']))
        duplicates[signature].append(record)
        if len(record.get('candidates', [])) > 1:
            rivals.append({'invoice_row': record['invoice_row'], 'invoice_id': record['invoice_id'], 'candidates': [
                {**{key: candidate[key] for key in ('contract_id', 'contract_row', 'contract_price')},
                 'invoice_variance': amount(Decimal(record['quantity']) * max(Decimal(record['unit_price']) - Decimal(candidate['contract_price']), 0))}
                for candidate in record['candidates']]})
    grouped = {}
    by_row = {binding['row']: binding for binding in source['bindings']}
    if source.get('canonical_csv'):
        for record in parse_csv(source['canonical_csv']):
            number = record['row']
            binding = by_row.get(number, {})
            key = (binding.get('contract_id'), binding.get('contract_row'), record['vendor']) if binding else ('embedded', number, record['vendor'])
            if key not in grouped:
                grouped[key] = {'contract_id': binding.get('contract_id'), 'contract_row': binding.get('contract_row'),
                                'vendor': record['vendor'], 'rows': [], 'invoice_rows': [], 'row_count': 0,
                                'total_billed': Decimal(0), 'total_variance': Decimal(0), 'flagged_count': 0}
            group = grouped[key]
            variance = Decimal(record['quantity']) * max(Decimal(record['unit_price']) - Decimal(record['contract_price']), 0)
            group['rows'].append(number)
            group['invoice_rows'].append(binding.get('invoice_row', number))
            group['row_count'] += 1
            group['total_billed'] += Decimal(record['quantity']) * Decimal(record['unit_price'])
            group['total_variance'] += variance
            group['flagged_count'] += int(variance > 0)
    groups = sorted(grouped.values(), key=lambda value: (-value['total_variance'], str(value['contract_id']), value['rows'][0]))
    return {'groups': [{**group, 'total_billed': amount(group['total_billed']), 'total_variance': amount(group['total_variance'])} for group in groups],
            'duplicate_groups': [{'invoice_rows': [record['invoice_row'] for record in group],
                                  'invoice_id': group[0]['invoice_id'], 'vendor': group[0]['vendor'],
                                  'reason': 'Same invoice ID, vendor, item, date, quantity and billed price. Could be legitimate repeated lines; confirm the source. Nothing was excluded automatically.'}
                                 for group in duplicates.values() if len(group) > 1],
            'coverage': {**{key: amount(value) for key, value in billing.items()}, 'currency': 'USD'},
            'rival_contracts': rivals,
            'scope': 'Source-quality signals and conditional invoice arithmetic. Billed amounts outside scope are not inferred variance, fraud or savings.'}


def spreadsheet_text(value):
    text = str(value if value is not None else '')
    if text.startswith(('\t', '\r', '\n')) or text.lstrip(' \t\r\n').startswith(('=', '+', '-', '@')):
        return "'" + text
    return text


def handoff_csv(source):
    """All source rows, including exclusions; textual cells neutralize formulas."""
    canonical = {row['row']: row for row in parse_csv(source['canonical_csv'])}
    bindings = {binding['invoice_row']: binding for binding in source['bindings']}
    stream = io.StringIO(newline='')
    writer = csv.writer(stream, lineterminator='\n')
    writer.writerow(['source_invoice_row', 'invoice_id', 'vendor', 'item_id', 'invoice_date', 'scope',
                     'contract_id', 'contract_source_row', 'quantity', 'billed_unit_price',
                     'contract_price', 'positive_variance_usd', 'exclusion_reason'])
    for record in source['records']:
        binding = bindings.get(record['invoice_row'], {})
        normalized = canonical.get(binding.get('row', record['invoice_row'])) if record['status'] != 'excluded' else None
        price = normalized['contract_price'] if normalized else ''
        variance = amount(Decimal(normalized['quantity']) * max(Decimal(normalized['unit_price']) - Decimal(price), 0)) if normalized else ''
        writer.writerow([record['invoice_row'], *[spreadsheet_text(record.get(key, '')) for key in ('invoice_id', 'vendor', 'item_id', 'invoice_date')],
                         record['status'], spreadsheet_text(binding.get('contract_id', '')), binding.get('contract_row', ''),
                         record['quantity'], record['unit_price'], price, variance, spreadsheet_text(record.get('reason', ''))])
    return '\ufeff' + stream.getvalue()


def markdown_text(value):
    text = str(value if value is not None else '').replace('\r', ' ').replace('\n', ' ')
    for char in ('\\', '`', '*', '_', '[', ']', '#', '<', '>', '|'):
        text = text.replace(char, '\\' + char)
    return text


def review_brief(case):
    info = case['review_insights']
    coverage = info['coverage']
    baseline = case['baseline']
    lines = ['# Prooflane review brief', '', markdown_text(case['name']), '',
             f"Case: {case['id']} · revision {case['revision']}",
             f"Baseline run: {baseline['id']} · mode {baseline['mode']}", '',
             f"Positive price variance: USD {baseline['summary']['total_variance']}",
             f"Included billed: USD {coverage['included_billed']}; excluded billed: USD {coverage['excluded_billed']}; unresolved billed: USD {coverage['unresolved_billed']}.",
             'A positive difference is a review signal, not proof of overbilling or recovered savings.', '', '## Shared source groups', '']
    for group in info['groups']:
        lines.append(f"- {markdown_text(group['contract_id'] or 'Embedded price')} · {markdown_text(group['vendor'])}: {group['row_count']} rows, variance USD {group['total_variance']}; invoice source rows {', '.join(map(str, group['invoice_rows']))}.")
    lines += ['', '## Source decisions', '']
    for record in case['source']['records']:
        if record['status'] in {'selected', 'excluded'}:
            detail = record.get('reason') if record['status'] == 'excluded' else record.get('chosen_contract_id')
            lines.append(f"- Invoice source row {record['invoice_row']} {markdown_text(record['invoice_id'])}: {record['status']} · {markdown_text(detail)}.")
    lines += ['', '## Source-quality checks', '']
    if not info['duplicate_groups']:
        lines.append('No identical financial/date source-line groups detected by this limited check. This is not a fraud clearance.')
    for group in info['duplicate_groups']:
        lines.append(f"- Confirm repeated lines for {markdown_text(group['invoice_id'])}, invoice source rows {', '.join(map(str, group['invoice_rows']))}: {group['reason']}")
    lines += ['', '## Declared uncertainty', '']
    targets = {item['id']: item for item in case['targets']}
    if not case['bounds']:
        lines.append('No ranges declared. Inputs fixed at their original values.')
    for bound in case['bounds']:
        lines.append(f"- {markdown_text(targets[bound['target']]['label'])}: {bound['low']} to {bound['high']}.")
    intelligence = case['intelligence']
    lines.append(f"Conditional total range: USD {intelligence['low']} to {intelligence['high']}. These ranges are not probabilities.")
    lines += ['', '## Executed alternatives', '']
    if not case['variants']:
        lines.append('None executed.')
    for variant in case['variants']:
        lines.append(f"- {markdown_text(variant['name'])}: USD {variant['run']['summary']['total_variance']}; delta USD {variant['delta']['total_variance']}; run {variant['id']}.")
        for change in variant['changes']:
            lines.append(f"  - {markdown_text(targets[change['target']]['label'])} → {change['value']}.")
    switch = case.get('priority_switch', {})
    if switch.get('status') == 'available':
        lines += ['', '## Price that changes original priority', '', switch['scope']]
        for transition in switch['transitions']:
            for label, key in (('Last strict priority', 'last_strict'), ('First changed state', 'at'), ('One cent further', 'beyond')):
                value = transition[key]
                if value:
                    leaders = ', '.join(f"{markdown_text(row['invoice_id'])} (record {row['row']})" for row in value['leaders']) or 'No positive variance'
                    lines.append(f"- {label}, USD {value['price']}: {value['status']} · {leaders}.")
    lines += ['', '## Verification and limits', '',
              'This brief is a readable handoff, not a signed or independently verified artifact. Download the corresponding JSON case packet and run:', '',
              f"python scripts/verify_receipt.py prooflane-case-{case['id']}.json", '',
              'The verifier reconstructs source links, arithmetic and declared assumptions. It does not authenticate an issuer, a supplied contract or a host runtime.',
              'CSV and brief include source data. Share them only where those data may be shared.', '']
    return '\n'.join(lines)
