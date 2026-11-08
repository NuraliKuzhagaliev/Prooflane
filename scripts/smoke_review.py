"""Real HTTP acceptance for review handoffs, diagnostics and request recovery."""
import argparse
import csv
import io
import json
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from prooflane.case_evidence import check_case_packet


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base-url', default='http://127.0.0.1:8766')
    parser.add_argument('--mode', choices=('reference', 'sandbox'), default='reference')
    parser.add_argument('--output-dir', type=Path, default=ROOT / 'artifacts/transformation-20261108')
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    origin = args.base_url.rstrip('/')
    headers = {'X-Prooflane-Request': '1', 'Origin': origin}
    report = {'at': datetime.now(timezone.utc).isoformat(), 'base_url': origin, 'mode': args.mode,
              'scope': 'REAL_HTTP_NO_MODEL_CALLS', 'passed': False, 'checks': []}

    def check(name, passed):
        report['checks'].append({'name': name, 'passed': bool(passed)})
        if not passed:
            raise AssertionError(name)

    try:
        with httpx.Client(base_url=origin, timeout=60, trust_env=False) as client, httpx.Client(base_url=origin, timeout=60, trust_env=False) as stranger:
            sample = client.get('/api/cases/sample').json()
            sources = {key: sample[key] for key in ('invoices_csv', 'contracts_csv')}
            match = client.post('/api/cases/match', headers=headers, json=sources).json()
            rivals = match['review_insights']['rival_contracts'][0]['candidates']
            check('Eligible rival consequences before choice', [item['invoice_variance'] for item in rivals] == ['40.00', '32.00'])
            check('Unresolved billed exposure not inferred variance', match['review_insights']['coverage']['unresolved_billed'] == '722.00')
            check('No automatic rival selection', match['counts']['unresolved'] == 2)
            body = {'name': 'HTTP review acceptance synthetic', 'request_id': str(uuid.uuid4()), 'mode': args.mode, **sources,
                    'selections': {'5': 'C2R'}, 'exclusions': {'7': 'No active contract in this fictional fixture.'}}
            created = client.post('/api/cases', headers=headers, json=body)
            check('Case execution successful', created.status_code == 200)
            case = created.json()['case']
            check('Manual baseline', case['baseline']['summary']['total_variance'] == '768.00')
            path = '/api/cases/' + case['id']
            replay = client.post('/api/cases', headers=headers, json=body).json()
            check('Create replay returns same case and run', (replay['case']['id'], replay['case']['baseline']['id']) == (case['id'], case['baseline']['id']))
            status = client.get('/api/operations/' + body['request_id']).json()['operation']
            check('Completed operation is retrievable without another execution', status['status'] == 'completed' and status['case_id'] == case['id'])
            check('Operation session isolation', stranger.get('/api/operations/' + body['request_id']).status_code == 404)
            check('Request ID cannot change source meaning', client.post('/api/cases', headers=headers, json={**body, 'name': 'Different'}).status_code == 409)
            check('Contract groups include zero variance bound row', case['review_insights']['groups'][0]['rows'] == [2, 3, 8]
                  and case['review_insights']['groups'][0]['total_variance'] == '620.00')
            check('Excluded amount visible', case['review_insights']['coverage']['excluded_billed'] == '250.00')
            exported = client.get(path + '/handoff.csv')
            records = list(csv.DictReader(io.StringIO(exported.text.lstrip('\ufeff'))))
            check('Handoff has all source rows and excluded row has no invented variance', len(records) == 8 and records[5]['positive_variance_usd'] == '' and records[5]['scope'] == 'excluded')
            (args.output_dir / (args.mode + '-handoff.csv')).write_bytes(exported.content)
            brief = client.get(path + '/brief.md')
            check('Readable brief includes amounts and verification limits', all(text in brief.text for text in ('USD 768.00', 'USD 250.00', 'not a signed or independently verified artifact', 'Source-quality checks')))
            (args.output_dir / (args.mode + '-brief.md')).write_bytes(brief.content)
            for suffix in ('/handoff.csv', '/brief.md'):
                check('Handoff session isolation ' + suffix, stranger.get(path + suffix).status_code == 404)
            payload = {'request_id': str(uuid.uuid4()), 'revision': case['revision'], 'name': 'At priority boundary',
                       'changes': [{'target': 'contract:C1', 'value': '82.60'}]}
            result = client.post(path + '/variants', headers=headers, json=payload).json()['case']
            replay = client.post(path + '/variants', headers=headers, json=payload).json()['case']
            check('Variant replay does not execute a second alternative', len(replay['variants']) == 1 and replay['variants'][0]['id'] == result['variants'][0]['id'])
            check('Real variant and baseline remain distinct', result['variants'][0]['run']['summary']['total_variance'] == '244.00' and result['baseline']['summary']['total_variance'] == '768.00')
            packet = client.get(path + '/packet')
            check('Exported evidence reconstructs', check_case_packet(packet.json())['passed'])
            (args.output_dir / (args.mode + '-review-case.json')).write_bytes(packet.content)
            ambiguous = '{"case_sha256":"ambiguous",' + packet.text.lstrip()[1:]
            rejected = client.post('/api/verify-packet', headers={**headers, 'Content-Type': 'application/json'}, content=ambiguous)
            check('Raw duplicate-key JSON rejected', rejected.json()['passed'] is False)
            check('Non-JSON request content type rejected', client.post('/api/verify-packet', headers=headers, content=packet.content).status_code == 415)
            accepted = client.post('/api/verify-packet', headers={**headers, 'Content-Type': 'application/json'}, content=packet.content)
            check('Strict parser accepts normal case', accepted.json()['passed'])
            repeated = sources['invoices_csv'] + sources['invoices_csv'].splitlines()[1] + '\n'
            dup = client.post('/api/cases/match', headers=headers, json={**sources, 'invoices_csv': repeated}).json()
            check('Repeated financial line warned without implicit exclusion', dup['review_insights']['duplicate_groups'][0]['invoice_rows'] == [2, 10] and dup['counts']['excluded'] == 0 and dup['counts']['total'] == 9)
            check('No extra replay runs', len(client.get('/api/runs').json()['runs']) == 2)
            report['case_id'] = case['id']
            report['passed'] = True
    except Exception as exc:
        report['error'] = type(exc).__name__ + ': ' + str(exc)[:300]
    destination = args.output_dir / (args.mode + '-review-smoke.json')
    destination.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'passed': report['passed'], 'checks': len(report['checks']), 'error': report.get('error'), 'report': str(destination)}))
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
