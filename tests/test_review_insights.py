import csv
import io
from decimal import Decimal
from pathlib import Path

from prooflane.reconciliation import reconcile
from prooflane.review_insights import handoff_csv, review_insights, spreadsheet_text


def fixture():
    return reconcile(Path('examples/case-invoices.csv').read_text(encoding='utf-8'),
                     Path('examples/case-contracts.csv').read_text(encoding='utf-8'),
                     {'5': 'C2R'}, {'7': 'No active contract in synthetic fixture.'})


def test_contract_groups_and_excluded_exposure_are_distinct_from_variance():
    source = fixture()
    info = review_insights(source)
    assert info['coverage'] == {'total_billed': '7360.00', 'included_billed': '7110.00', 'excluded_billed': '250.00', 'unresolved_billed': '0.00', 'currency': 'USD'}
    c1 = info['groups'][0]
    assert c1['contract_id'] == 'C1' and c1['rows'] == [2, 3, 8] and c1['invoice_rows'] == [2, 3, 9]
    assert c1['total_variance'] == '620.00' and c1['flagged_count'] == 2
    assert [(c['contract_id'], c['invoice_variance']) for c in info['rival_contracts'][0]['candidates']] == [('C2', '40.00'), ('C2R', '32.00')]


def test_csv_includes_exclusion_and_neutralizes_untrusted_formula_cells():
    source = fixture()
    source['records'][0]['invoice_id'] = '=HYPERLINK("https://example.invalid")'
    source['records'][0]['vendor'] = ' +SUM(1,2)'
    text = handoff_csv(source)
    assert text.startswith('\ufeff')
    rows = list(csv.DictReader(io.StringIO(text.lstrip('\ufeff'))))
    assert len(rows) == 8
    assert rows[0]['invoice_id'].startswith("'=HYPERLINK")
    assert rows[0]['vendor'].startswith("' +SUM")
    assert rows[0]['positive_variance_usd'] == '520.00'
    assert rows[5]['scope'] == 'excluded' and rows[5]['positive_variance_usd'] == ''
    assert rows[5]['contract_price'] == '' and rows[5]['exclusion_reason']
    assert sum(Decimal(row['positive_variance_usd'] or 0) for row in rows) == Decimal('768.00')
    for text in ('=1', '+1', '-1', '@SUM(A1)', '\tformula', '  =1'):
        assert spreadsheet_text(text).startswith("'")


def test_duplicate_signal_preserves_lines_and_never_changes_scope():
    invoices = 'invoice_id,vendor,item_id,invoice_date,quantity,unit_price,notes\nA,V,I,2026-11-01,1,2,one\nA,V,I,2026-11-01,1,2.00,two\nA,V,I,2026-11-02,1,2,different date\n'
    contracts = 'contract_id,vendor,item_id,valid_from,valid_to,contract_price\nC,V,I,2026-01-01,2026-12-31,1\n'
    source = reconcile(invoices, contracts)
    before = source['canonical_csv']
    info = review_insights(source)
    assert [group['invoice_rows'] for group in info['duplicate_groups']] == [[2, 3]]
    assert source['canonical_csv'] == before and source['counts']['matched'] == 3
    assert info['groups'][0]['row_count'] == 3


def test_unresolved_coverage_does_not_infer_a_contract_price():
    invoices = Path('examples/case-invoices.csv').read_text(encoding='utf-8')
    contracts = Path('examples/case-contracts.csv').read_text(encoding='utf-8')
    info = review_insights(reconcile(invoices, contracts))
    assert info['groups'] == []
    assert info['coverage']['unresolved_billed'] == '722.00'
    assert info['coverage']['excluded_billed'] == '0.00'


def test_handoff_routes_are_owned_and_brief_distinguishes_baseline_and_alternative(tmp_path):
    from fastapi.testclient import TestClient
    from prooflane.app import create_app
    from test_cases import HEADERS, UnavailableSandbox, create_case, propose
    with TestClient(create_app(tmp_path, sandbox=UnavailableSandbox())) as client:
        case = create_case(client)
        path = '/api/cases/' + case['id']
        updated = client.post(path + '/variants', headers=HEADERS, json=propose(case)).json()['case']
        report = client.get(path + '/brief.md')
        assert report.status_code == 200 and 'attachment;' in report.headers['content-disposition']
        assert 'USD 768.00' in report.text and 'USD 368.00' in report.text and 'USD 250.00' in report.text
        assert 'not a signed or independently verified artifact' in report.text
        assert updated['baseline']['id'] in report.text
        handoff = client.get(path + '/handoff.csv')
        records = list(csv.DictReader(io.StringIO(handoff.text.lstrip('\ufeff'))))
        assert len(records) == 8 and records[0]['positive_variance_usd'] == '520.00'
        with TestClient(client.app) as stranger:
            for suffix in ('/handoff.csv', '/brief.md'):
                assert stranger.get(path + suffix).status_code == 404
