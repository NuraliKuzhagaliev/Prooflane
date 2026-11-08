// Independent bounded source-function probes. This is not a browser/DOM test.
import fs from 'node:fs';
import vm from 'node:vm';
import crypto from 'node:crypto';
const source = fs.readFileSync(new URL('../../web/workbench.js', import.meta.url), 'utf8');
function fn(name) {
  const pattern = new RegExp(`(?:async )?function ${name}\\(`);
  const start = source.search(pattern);
  if (start < 0) throw Error(`Missing ${name}`);
  const rest = source.slice(start);
  const next = rest.slice(1).search(/\n(?:async )?function /);
  return next < 0 ? rest : rest.slice(0, next + 1);
}
const results = [];
function node(tag='div',css='',value) { return {tag,css,value,hidden:false,children:[],append(...children){this.children.push(...children);},replaceChildren(...children){this.children=children;},focus(){}}; }
for (const previous of [0, 1]) {
  const nodes = new Map();
  const baseline = { mode: 'sandbox' };
  const existing = { run: { status: 'verified', mode: 'sandbox' } };
  const state = { active: { id: 'case', revision: 1, baseline, variants: previous ? [existing] : [] }, busy: false, changes: [{target:'contract:C1', value:'80'}] };
  const notices = [], errors = [];
  const context = vm.createContext({state, $: id => { if (!nodes.has(id)) nodes.set(id, {...node(),value: id === 'wb-alternative-name' ? 'Failed proposal' : ''}); return nodes.get(id); },
    endpoint: suffix => '/api/cases/case'+suffix, post: async () => ({case:state.active, failed_run:{status:'failed',error:'Sandbox became unavailable',summary:null}}),
    acceptCase: async current => { state.active=current; }, refreshCases:async()=>{}, setBusy:value=>{state.busy=value;}, error:value=>{if(value)errors.push(value);}, notice:value=>{if(value)notices.push(value);},
    el:node,badge:(label,tone)=>node('span',tone,label),button:label=>node('button','',label),checksList:()=>node(),
    modeDescription:()=>'',completionLabel:()=> 'Independently verified', renderDraftChanges:()=>{},targetById:()=>null});
  vm.runInContext(fn('mutateCase')+'\n'+fn('runAlternative'), context);
  let exception=null;
  try { await vm.runInContext('runAlternative({preventDefault(){}})',context); } catch(error) {exception=String(error);}
  results.push({probe:'failed_alternative',previous_variants:previous,retained_draft:state.changes.length>0,errors,notices,exception});
}
{
  const state={active:{id:'old-case'},rows:[{row:2,invoice_id:'old-invoice'}]};
  const context=vm.createContext({state,idURL:encodeURIComponent,api:async()=>{throw Error('source fetch unavailable');}});
  vm.runInContext(fn('acceptCase'),context);
  let exception=null;try{await vm.runInContext("acceptCase({id:'new-case',baseline:{id:'new-run'}})",context);}catch(error){exception=String(error);}
  results.push({probe:'case_source_fetch_failure',active_case:state.active.id,visible_source:state.rows[0].invoice_id,exception});
}
{
  function el(tag,css,value){return {tag,css,value,children:[],append(...children){this.children.push(...children);}};}
  const context=vm.createContext({el});vm.runInContext(fn('checksList'),context);
  const tree=vm.runInContext("checksList(['Source reconciliation','All alternatives'], true)",context);
  results.push({probe:'case_string_checks',rows:tree.children.map(row=>({css:row.css,label:row.children[1].children[0].value}))});
}
{
  const original=fs.readFileSync(new URL('../transformation/reference-case.json',import.meta.url),'utf8');
  const state={busy:false,packetText:original,packetRequest:1};
  const nodes=new Map();const $=id=>{if(!nodes.has(id))nodes.set(id,node());return nodes.get(id);};
  let respond;const waiting=new Promise(resolve=>{respond=resolve;});
  const context=vm.createContext({state,$,bytes:s=>Buffer.byteLength(s),MAX_PACKET:8*1024*1024,
    error:()=>{},setBusy:value=>{state.busy=value;},post:()=>waiting,el:node,badge:(label,tone)=>node('span',tone,label),checksList:()=>node(),announce:()=>{}});
  vm.runInContext(fn('verifyPacket'),context);
  const running=vm.runInContext('verifyPacket({preventDefault(){}})',context);
  // These are the actual input handler's mutations; packet inputs are not disabled in syncActions.
  state.packetText='{"tampered":true}';state.packetRequest++;$('wb-verify-result').hidden=true;
  respond({passed:true,checks:[],scope:'Verified original supplied packet'});await running;
  results.push({probe:'packet_edit_during_verification',current_packet:state.packetText,result_visible:!$('wb-verify-result').hidden,result_badge:$('wb-verify-result').children[0]?.value,
    editor_disabled_while_busy:/\['[^\n]*'wb-packet-json'/.test(source.slice(source.indexOf('function syncActions'),source.indexOf('function selectView')))});
}
function sourceContext() {
  const nodes=new Map();const $=id=>{if(!nodes.has(id))nodes.set(id,{...node(),value:''});return nodes.get(id);};
  const state={busy:false,active:null,sourceRequests:{invoices:0,contracts:0},sourceLoading:{invoices:false,contracts:false}};
  const context=vm.createContext({state,$,MAX_CSV:128*1024,error:()=>{},notice:()=>{},text:(id,value)=>{$(id).value=value;},count:String,announce:()=>{},
    syncActions:()=>{},renderSources:()=>{},renderHeader:()=>{},renderEvidence:()=>{},selectView:()=>{},setBusy:value=>{state.busy=value;}});
  vm.runInContext(fn('invalidateSourceReads')+'\n'+fn('invalidateSources')+'\n'+fn('loadSource')+'\n'+fn('resetDraft'),context);
  return {state,$,context};
}
{
  const {state,$,context}=sourceContext();
  let firstDone,secondDone;
  const first=new Promise(resolve=>{firstDone=resolve;}),second=new Promise(resolve=>{secondDone=resolve;});
  context.first={name:'first.csv',size:100,text:()=>first};context.second={name:'second.csv',size:100,text:()=>second};
  const readingFirst=vm.runInContext("loadSource(first,'invoices')",context);
  const readingSecond=vm.runInContext("loadSource(second,'invoices')",context);
  secondDone('second selected source');await readingSecond;
  firstDone('first stale source');await readingFirst;
  results.push({probe:'invoice_file_read_order',selected_last:'second.csv',final_text:$('wb-invoices').value,final_label:$('wb-invoice-file-label').value});
}
{
  const {state,$,context}=sourceContext();
  let firstDone,secondDone;
  const first=new Promise(resolve=>{firstDone=resolve;}),second=new Promise(resolve=>{secondDone=resolve;});
  context.first={name:'first.csv',size:100,text:()=>first};context.second={name:'second.csv',size:100,text:()=>second};
  const a=vm.runInContext("loadSource(first,'invoices')",context);const b=vm.runInContext("loadSource(second,'invoices')",context);
  firstDone('stale');await a;const stillLoading=state.sourceLoading.invoices;
  secondDone('latest');await b;
  results.push({probe:'old_completion_keeps_new_read_busy',still_loading_after_old:stillLoading,loading_after_latest:state.sourceLoading.invoices,final_text:$('wb-invoices').value});
}
{
  const {state,$,context}=sourceContext();let invDone,conDone;
  const inv=new Promise(resolve=>{invDone=resolve;}),con=new Promise(resolve=>{conDone=resolve;});
  context.inv={name:'invoices.csv',size:100,text:()=>inv};context.con={name:'contracts.csv',size:100,text:()=>con};
  let calls=0;context.post=async()=>{calls++;throw Error('unexpected request while source read pending');};context.bytes=s=>Buffer.byteLength(s);context.modeDescription=()=>'';
  vm.runInContext(fn('matchSources')+'\n'+fn('createCase'),context);
  const a=vm.runInContext("loadSource(inv,'invoices')",context);const b=vm.runInContext("loadSource(con,'contracts')",context);
  invDone('invoice source');await a;state.match={ready:true};
  await vm.runInContext('matchSources()',context);await vm.runInContext('createCase()',context);
  const pendingContracts=state.sourceLoading.contracts;conDone('contract source');await b;
  results.push({probe:'cross_source_reads_and_execution_gate',pending_contracts_after_invoice:pendingContracts,requests_while_loading:calls,invoices:$('wb-invoices').value,contracts:$('wb-contracts').value,all_finished:Object.values(state.sourceLoading).every(v=>!v)});
}
for(const action of ['paste','reset','sample','openCase']){
  const {state,$,context}=sourceContext();let done;const reading=new Promise(resolve=>{done=resolve;});context.file={name:'old.csv',size:100,text:()=>reading};
  const pending=vm.runInContext("loadSource(file,'invoices')",context);
  if(action==='paste'){$('wb-invoices').value='pasted newer source';vm.runInContext("invalidateSourceReads('invoices'); invalidateSources();",context);}
  if(action==='reset')vm.runInContext('resetDraft()',context);
  if(action==='sample'){
    const begin=source.indexOf("$('wb-sample').addEventListener('click', async () => {");const end=source.indexOf("\nwindow.addEventListener('prooflane:health'",begin);
    const eventSource=source.slice(begin,end);const callback=eventSource.slice(eventSource.indexOf('async () =>'),eventSource.lastIndexOf(');'));
    context.api=async()=>({invoices_csv:'sample invoices',contracts_csv:'sample contracts',name:'Sample'});context.matchSources=async()=>{};
    await vm.runInContext('('+callback+')()',context);
  }
  if(action==='openCase'){
    context.idURL=encodeURIComponent;context.api=async()=>{throw Error('case unavailable');};vm.runInContext(fn('openCase'),context);await vm.runInContext("openCase('new-case')",context);
  }
  done('old delayed source');await pending;
  results.push({probe:'pending_source_then_'+action,final_text:$('wb-invoices').value,loading:state.sourceLoading.invoices,late_source_ignored:$('wb-invoices').value!=='old delayed source'});
}
for (const result of results) {
  if (result.probe==='failed_alternative') result.passed=result.retained_draft && result.errors.length===1 && result.notices.length===0 && result.exception===null;
  else if (result.probe==='case_source_fetch_failure') result.passed=result.active_case==='old-case' && result.visible_source==='old-invoice';
  else if (result.probe==='case_string_checks') result.passed=result.rows.every(row=>row.css==='' && row.label.endsWith(' · passed'));
  else if (result.probe==='packet_edit_during_verification') result.passed=!result.result_visible && result.editor_disabled_while_busy;
  else if (result.probe==='invoice_file_read_order') result.passed=result.final_text==='second selected source' && result.final_label.startsWith('second.csv');
  else if (result.probe==='old_completion_keeps_new_read_busy') result.passed=result.still_loading_after_old && !result.loading_after_latest && result.final_text==='latest';
  else if (result.probe==='cross_source_reads_and_execution_gate') result.passed=result.pending_contracts_after_invoice && result.requests_while_loading===0 && result.invoices==='invoice source' && result.contracts==='contract source' && result.all_finished;
  else if (result.probe.startsWith('pending_source_then_')) result.passed=result.late_source_ignored && !result.loading;
}
const passed=results.every(result=>result.passed===true);
console.log(JSON.stringify({scope:'Actual source functions executed in Node VM; fetch/DOM rendering boundaries stubbed; no browser or provider call',source_sha256:crypto.createHash('sha256').update(source).digest('hex'),passed,results},null,2));
if(!passed)process.exitCode=1;
