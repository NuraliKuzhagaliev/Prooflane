"""Independent bounded review probes; provider/runtime are explicit doubles, never live."""
import copy
import csv
import gc
import io
import json
import os
import sqlite3
import sys
import tempfile
import time
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from prooflane.analysis import canonical, contract_output, digest, parse_csv, summarize
from prooflane.case_evidence import check_case_packet

results = []
def check(name, condition):
    results.append({"name": name, "passed": bool(condition)})
    if not condition:
        raise AssertionError(name)

def rehash(packet):
    packet['case_sha256'] = digest(canonical({k:v for k,v in packet.items() if k != 'case_sha256'}))

for mode in ('reference', 'sandbox'):
    packet = json.loads((ROOT/'artifacts/transformation'/f'{mode}-case.json').read_text(encoding='utf-8'))
    check(mode+': actual saved packet independently verified', check_case_packet(packet)['passed'])
    check(mode+': manual source coverage', packet['source']['counts']=={'total':8,'matched':6,'selected':1,'unresolved':0,'excluded':1})
    check(mode+': manual arithmetic and joint variant', packet['baseline']['summary']['total_variance']=='768.00' and [v['receipt']['summary']['total_variance'] for v in packet['alternatives']]==['368.00','568.00'])
    receipts = [packet['baseline'], *[v['receipt'] for v in packet['alternatives']]]
    check(mode+': recorded runtime scope', all(r['provenance']['model_calls']==0 and r['execution']['runtime']==('docker' if mode=='sandbox' else 'trusted-reference') for r in receipts))
    if mode=='sandbox':
        check('sandbox: recorded cleanup on all three receipts', all(r['execution']['cleanup'] is True for r in receipts))
    for field in ('source', 'intelligence', 'baseline_context'):
        altered=copy.deepcopy(packet)
        if field=='source': altered['sources']['contracts_csv']=altered['sources']['contracts_csv'].replace('72.00','71.00')
        elif field=='intelligence': altered['intelligence']['high']='0.00'
        else:
            altered['baseline']['case_context']['case_id']='other-case'
            altered['baseline']['receipt_sha256']=digest(canonical({k:v for k,v in altered['baseline'].items() if k!='receipt_sha256'}))
        rehash(altered)
        rejected=False
        try:check_case_packet(altered)
        except (ValueError,KeyError,TypeError):rejected=True
        check(mode+': rehashed '+field+' inconsistency rejected',rejected)

class RuntimeDouble:
    calls=0
    def available(self):return {'available':True,'detail':'Independent review double; not Docker'}
    def run(self, code, csv):
        self.calls+=1
        return {'stdout':canonical(contract_output(summarize(parse_csv(csv)))),'stderr':'','exit_code':0,'cleanup':True,'elapsed_ms':1}
class ProviderDouble:
    calls=0
    model='review-double'
    def configured(self):return True
    def generate(self,*args,**kwargs):
        self.calls+=1
        return {'code':'# Never executed: review runtime double','plan':['Review double'],'model':self.model,'requested_model':self.model,'usage':{}}

with tempfile.TemporaryDirectory(prefix='principal-probe-',dir=Path(__file__).parent) as directory:
    with patch.dict(os.environ,{'PROOFLANE_DATA_DIR':directory,'PROOFLANE_LIVE_ENABLED':'true','PROOFLANE_OPERATOR_TOKEN':'local-review-token'},clear=False):
        from fastapi.testclient import TestClient
        from prooflane.app import create_app
        runtime, provider=RuntimeDouble(),ProviderDouble()
        app=create_app(directory,sandbox=runtime,provider=provider)
        headers={'X-Prooflane-Request':'1'}
        payload={'name':'Independent review','mode':'vultr','operator_token':'local-review-token',
                 'invoices_csv':(ROOT/'examples/case-invoices.csv').read_text(encoding='utf-8'),
                 'contracts_csv':(ROOT/'examples/case-contracts.csv').read_text(encoding='utf-8'),
                 'selections':{'5':'C2R'},'exclusions':{'7':'No valid supplied contract'}}
        with TestClient(app) as owner,TestClient(app) as foreign:
            response=owner.post('/api/cases',json=payload,headers=headers)
            check('Double live baseline accepted through existing gate',response.status_code==200)
            case=response.json()['case'];base='/api/cases/'+case['id']
            changes={'revision':case['revision'],'name':'Proposal','changes':[{'target':'contract:C1','value':'80'}],'operator_token':'local-review-token'}
            for suffix in ('','/packet'):
                check('Foreign case read denied '+suffix,foreign.get(base+suffix).status_code==404)
            check('Foreign case mutation denied',foreign.post(base+'/variants',json=changes,headers=headers).status_code==404)
            check('Foreign source read denied',foreign.get('/api/runs/'+case['baseline']['id']+'/source').status_code==404)
            before=(runtime.calls,provider.calls)
            check('Wrong live operator token rejected',owner.post(base+'/variants',json={**changes,'operator_token':'wrong'},headers=headers).status_code==403)
            os.environ['PROOFLANE_LIVE_ENABLED']='false'
            check('Live gate rechecked at alternative',owner.post(base+'/variants',json=changes,headers=headers).status_code==503)
            check('No execution or model call on denied variants',before==(runtime.calls,provider.calls))
            check('Denied variants preserve complete original case',owner.get(base).json()['case']==case)
            check('Mode switch injection forbidden',owner.post(base+'/variants',json={**changes,'mode':'reference'},headers=headers).status_code==422)
            check('Escaped invalid Unicode redacted',owner.post('/api/cases',content=json.dumps({**payload,'name':'secret-\ud800'}),headers={**headers,'Content-Type':'application/json'}).status_code==422)
            invalid=owner.post('/api/verify-packet',content=b'\xff',headers={**headers,'Content-Type':'application/json'})
            check('Malformed UTF8 packet cleanly rejected',invalid.status_code==200 and invalid.json()['passed'] is False)
            with sqlite3.connect(Path(directory)/'prooflane.sqlite3') as db:
                db.execute('UPDATE runs SET created=? WHERE id=?',(time.time()-86401,case['baseline']['id']))
            db.close()
            check('Expired baseline makes case unavailable',owner.get(base).status_code==404)
            check('Expired baseline removes case from list',owner.get('/api/cases').json()=={'cases':[]})
    gc.collect()

# Cycle 2: genuinely new boundaries using small manual source oracles.
def csv_text(fields, rows):
    stream=io.StringIO(newline='');writer=csv.writer(stream,lineterminator='\r\n');writer.writerow(fields);writer.writerows(rows);return '\ufeff'+stream.getvalue()
contract_id='Cα / <script> &\nsource'
vendor='Vendor "quoted"'
sources={
    'invoices_csv':csv_text(['invoice_id','vendor','item_id','invoice_date','quantity','unit_price','notes'],[
        ['A\nquoted', ' '+vendor+' ', 'X', '2026-11-01','2','10','Supplied text: <script>alert(1)</script>'],
        ['B😀',vendor,'X','2026-11-30','3','7','second line\nwithin quoted cell']]),
    'contracts_csv':csv_text(['contract_id','vendor','item_id','valid_from','valid_to','contract_price'],[
        [' '+contract_id+' ',vendor,'X','2026-11-01','2026-11-30','8']])}
with tempfile.TemporaryDirectory(prefix='principal-probe-',dir=Path(__file__).parent) as directory:
    with patch.dict(os.environ,{'PROOFLANE_DATA_DIR':directory,'PROOFLANE_LIVE_ENABLED':'false'},clear=False):
        app=create_app(directory,sandbox=RuntimeDouble(),provider=ProviderDouble())
        with TestClient(app) as owner:
            response=owner.post('/api/cases',json={'name':'Review\r\nX-Foo: untrusted label','mode':'reference',**sources},headers=headers)
            check('Cycle2: BOM CRLF quoted multiline UTF8 sources accepted',response.status_code==200)
            case=response.json()['case'];base='/api/cases/'+case['id'];baseline_id=case['baseline']['id']
            check('Cycle2: inclusive endpoint dates and logical record numbers',case['source']['bindings']==[
                {'row':2,'invoice_row':2,'contract_id':contract_id,'contract_row':2},
                {'row':3,'invoice_row':3,'contract_id':contract_id,'contract_row':2}])
            check('Cycle2: trimmed keys preserve manual baseline4',case['baseline']['summary']['total_variance']=='4.00' and case['baseline']['summary']['total_billed']=='41.00')
            target='contract:'+contract_id
            response=owner.post(base+'/bounds',json={'revision':1,'bounds':[{'target':target,'low':'0','high':'12'}]},headers=headers)
            check('Cycle2: target IDs are data not URL paths',response.status_code==200)
            updated=response.json()['case']
            check('Cycle2: joint range manual0to41',updated['intelligence']['low']=='0.00' and updated['intelligence']['high']=='41.00')
            check('Cycle2: response identity preserved and revision incremented',updated['id']==case['id'] and updated['baseline']['id']==baseline_id and updated['revision']==2)
            proposal={'revision':1,'name':'stale proposal','changes':[{'target':target,'value':'9.00'}]}
            check('Cycle2: stale write409 before creating run',owner.post(base+'/variants',json=proposal,headers=headers).status_code==409 and len(owner.get('/api/runs').json()['runs'])==1)
            check('Cycle2: bool revision is rejected',owner.post(base+'/bounds',json={'revision':True,'bounds':[]},headers=headers).status_code==422)
            for value in ('\ud800','\x00','1e3'):
                invalid=owner.post(base+'/bounds',content=json.dumps({'revision':2,'bounds':[{'target':target,'low':value,'high':'12'}]}),headers={**headers,'Content-Type':'application/json'})
                check('Cycle2: malformed range '+repr(value)+' rejected without500',invalid.status_code==422)
            response=owner.post(base+'/variants',json={**proposal,'revision':2,'name':'new proposal'},headers=headers)
            check('Cycle2: valid retry creates one alternative',response.status_code==200 and response.json()['case']['revision']==3)
            saved=response.json()['case']
            check('Cycle2: quoted shared ID propagates to both rows',saved['variants'][0]['changed_rows']==[2,3] and saved['variants'][0]['run']['summary']['total_variance']=='2.00')
            packet_response=owner.get(base+'/packet');packet=packet_response.json()
            check('Cycle2: filename uses case UUID not untrusted label','X-Foo' not in packet_response.headers['content-disposition'] and packet_response.headers['content-disposition'].endswith(case['id']+'.json"'))
            check('Cycle2: normalized unusual source packet independently verifies',check_case_packet(packet)['passed'])
            check('Cycle2: original source bytes retained exactly',all(packet['sources'][k]==v for k,v in sources.items()))
    gc.collect()

with tempfile.TemporaryDirectory(prefix='principal-probe-',dir=Path(__file__).parent) as directory:
    with patch.dict(os.environ,{'PROOFLANE_DATA_DIR':directory,'PROOFLANE_LIVE_ENABLED':'false'},clear=False):
        app=create_app(directory,sandbox=RuntimeDouble(),provider=ProviderDouble())
        with TestClient(app) as owner,TestClient(app) as other:
            response=owner.post('/api/cases',json={'name':'Quota review','mode':'reference',**sources},headers=headers)
            case=response.json()['case'];base='/api/cases/'+case['id']
            reads=[owner.get(base+('/packet' if i%2 else '')).status_code for i in range(119)]
            check('Cycle2: shared read quota accepts first120 operations',reads==[200]*119)
            check('Cycle2: case read121 is429',owner.get(base).status_code==429)
            check('Cycle2: packet read shares exhausted quota',owner.get(base+'/packet').status_code==429)
            check('Cycle2: mutations share exhausted quota',owner.post(base+'/bounds',json={'revision':1,'bounds':[]},headers=headers).status_code==429)
            other_response=other.post('/api/cases',json={'name':'Other session','mode':'reference',**sources},headers=headers)
            check('Cycle2: independent session belowIPquota still works',other_response.status_code==200)
    gc.collect()
print(json.dumps({'scope':'Saved actual HTTP packets plus independent TestClient with provider/runtime doubles; no live external service','checks':len(results),'passed':all(c['passed'] for c in results),'results':results},indent=2))
