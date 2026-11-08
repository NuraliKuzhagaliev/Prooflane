import {test} from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import vm from 'node:vm';
import { OPERATION_KEY, operationState, readSession } from '../web/review-session.js';
const source=readFileSync(new URL('../web/workbench.js',import.meta.url),'utf8');
function fn(name){const start=source.indexOf(`function ${name}(`);assert.ok(start>=0);const next=source.slice(start+1).search(/\n(?:async )?function |\nfor \(const node of document.querySelectorAll/);return source.slice(start,next<0?source.length:start+1+next);}
function element(){return{hidden:false,attrs:{},tabIndex:0,focused:0,open:false,setAttribute(k,v){this.attrs[k]=v;},focus(){this.focused++;},showModal(){this.open=true;},close(){this.open=false;}};}
test('assumption tool switch exposes one panel and one keyboard tab without changing saved analysis',()=>{
 const nodes=new Map(); const $=id=>{if(!nodes.has(id))nodes.set(id,element());return nodes.get(id);};
 const tabs=['ranges','alternatives'].map(pane=>Object.assign(element(),{dataset:{explorePane:pane}}));
 const state={explorePane:'ranges',active:{bounds:[{target:'contract:C1',low:'65',high:'85'}],variants:[{name:'Executed original-mode variant'}]},changes:[{target:'contract:C1',value:'80'}]};
 const original=JSON.stringify({active:state.active,changes:state.changes});
 const context=vm.createContext({state,$,rememberLocation(){},document:{querySelectorAll:()=>tabs}}); vm.runInContext(fn('setExplorePane'),context);
 vm.runInContext("setExplorePane('alternatives', true)",context);
 assert.equal($('folio-range-pane').hidden,true);assert.equal($('folio-alternative-pane').hidden,false);
 assert.equal(tabs[0].attrs['aria-selected'],'false');assert.equal(tabs[0].tabIndex,-1);assert.equal(tabs[1].tabIndex,0);assert.equal(tabs[1].focused,1);
 assert.equal(JSON.stringify({active:state.active,changes:state.changes}),original);
 vm.runInContext("setExplorePane('ranges')",context);assert.equal($('folio-range-pane').hidden,false);assert.equal($('folio-alternative-pane').hidden,true);
 vm.runInContext("setExplorePane('unsupported')",context);assert.equal(state.explorePane,'ranges');
});
test('archive cannot interrupt a pending request and captures the opener before native modal focus',()=>{
 const nodes=new Map();const $=id=>{if(!nodes.has(id))nodes.set(id,element());return nodes.get(id);};const opener=element();
 const state={busy:true};const context=vm.createContext({state,$,document:{activeElement:opener},archiveOpener:null});
 vm.runInContext(fn('openArchive')+'\n'+fn('closeArchive'),context);
 vm.runInContext('openArchive()',context);assert.equal($('folio-archive').open,false);assert.equal(context.archiveOpener,null);
 state.busy=false;vm.runInContext('openArchive()',context);assert.equal($('folio-archive').open,true);assert.equal(context.archiveOpener,opener);assert.equal($('wb-rail-toggle').attrs['aria-expanded'],'true');assert.equal($('folio-close-archive').focused,1);
 vm.runInContext('closeArchive()',context);assert.equal($('folio-archive').open,false);
});

test('choosing a source row moves focus to the new inspector and returns to the replacement row', () => {
  let active;
  const makeNode = () => ({
    children: [],
    tabIndex: -1,
    setAttribute() {},
    append(...children) { this.children.push(...children); },
    prepend(child) { this.children.unshift(child); },
    replaceChildren() { this.children = []; },
    focus() { active = this; },
    scrollIntoView(options) { this.scrollBehavior = options.behavior; },
  });
  const table = makeNode();
  const inspector = makeNode();
  const search = makeNode();
  const empty = makeNode();
  const state = { matchRow: 5 };
  const records = [{ invoice_id: 'INV506', invoice_row: 7, status: 'unmatched' }];
  const rowButton = () => table.children[0]?.children[0].children[0];
  const nodes = {
    'wb-matches-body': table,
    'wb-matches-empty': empty,
    'wb-match-filter': { value: 'all' },
    'wb-match-search': search,
    'wb-match-inspector': inspector,
  };
  const context = vm.createContext({
    state,
    $: id => id === 'wb-match-row-7' ? rowButton() : nodes[id],
    currentMatch: () => ({ records }),
    filterMatches: () => records,
    el: makeNode,
    button: (_label, activate) => Object.assign(makeNode(), { activate, tabIndex: 0 }),
    statusBadge: makeNode,
    selectSourceRecord: row => { state.matchRow = row; },
    renderMatchInspector() {
      const heading = Object.assign(makeNode(), { after(control) { inspector.back = control; } });
      inspector.querySelector = () => heading;
      vm.runInContext("addInspectorNavigation($('wb-match-inspector'), 'wb-match-row', 7, 'INV506', 'wb-match-search', true)", context);
    },
  });
  vm.runInContext(['focusPoint', 'renderMatchTable', 'addInspectorNavigation'].map(fn).join('\n'), context);
  vm.runInContext('renderMatchTable()', context);
  const original = rowButton();
  original.focus();
  original.activate();
  assert.equal(state.matchRow, 7);
  assert.equal(active, inspector.querySelector('h3'));
  assert.equal(active.scrollBehavior, 'instant');
  assert.notEqual(rowButton(), original);
  inspector.back.activate();
  assert.equal(active, rowButton());
  table.replaceChildren();
  inspector.back.activate();
  assert.equal(active, search);
});

test('packet submission preserves duplicate JSON keys for strict server rejection', async () => {
  const original = '{"schema":"prooflane.case.v1","case_id":"first","case_id":"second"}';
  let sent;
  const resultNode = { hidden: true, replaceChildren() {}, append() {} };
  const node = () => ({ append() {} });
  const context = vm.createContext({
    state: { busy: false, packetText: original, packetRequest: 1 },
    $: () => resultNode, MAX_PACKET: 8 * 1024 * 1024,
    bytes: value => Buffer.byteLength(value), error() {}, setBusy() {}, announce() {},
    badge: node, el: node,
    api: async (path, options) => { sent = { path, ...options }; return { passed: false, error: 'Duplicate JSON keys rejected.' }; },
  });
  vm.runInContext('async ' + fn('verifyPacket'), context);
  await vm.runInContext('verifyPacket({preventDefault(){}})', context);
  assert.equal(sent.path, '/api/verify-packet');
  assert.equal(sent.method, 'POST');
  assert.equal(sent.body, original);
  assert.equal(resultNode.hidden, false);
});

test('a stalled execution response has a deadline and never retries its POST', async () => {
  const timers = [];
  const cleared = [];
  let requests = 0;
  const context = vm.createContext({
    AbortController,
    setTimeout: (callback, delay) => { timers.push({ callback, delay }); return 7; },
    clearTimeout: timer => cleared.push(timer),
    fetch: (_path, options) => {
      requests++;
      return new Promise((_resolve, reject) => options.signal.addEventListener('abort', () => reject(new Error('aborted')), { once: true }));
    },
  });
  vm.runInContext('async ' + fn('api'), context);
  const request = vm.runInContext("api('/api/cases', {method:'POST',body:'{}'})", context);
  assert.equal(timers[0].delay, 240000);
  timers[0].callback();
  await assert.rejects(request, /Check pending result/);
  assert.equal(requests, 1);
  assert.deepEqual(cleared, [7]);
});

test('failed live baseline exposes its safe diagnostic and clears the credential', async () => {
  const nodes = new Map();
  const $ = id => { if (!nodes.has(id)) nodes.set(id, {value: '', focus() {}}); return nodes.get(id); };
  $('wb-execution-mode').value = 'vultr'; $('wb-name').value = 'Synthetic'; $('wb-operator-token').value = 'test-only-operator';
  let message = '', finished = 0;
  const failure = Object.assign(new Error('Baseline execution failed; no case was created.'), {
    status: 422, data: {failed_run: {error: 'Vultr model output was incomplete (finish_reason=length).'}}
  });
  const context = vm.createContext({
    state: {busy:false,sourceLoading:{},match:{ready:true},selections:{},exclusions:{},active:null}, pendingOperation:null, $,
    error(value='') {message=value;}, notice(){}, beginOperation(){return 'test-id';}, setBusy(){},modeDescription(){return 'Live Vultr';},
    finishOperation(){finished++;},focusPoint(){},post:async()=>{throw failure;}
  });
  vm.runInContext('async ' + fn('createCase'), context);
  await vm.runInContext('createCase()', context);
  assert.match(message, /finish_reason=length/);
  assert.equal($('wb-operator-token').value, '');
  assert.equal(finished, 1);
});

test('completed API reads clear their shorter deadline and preserve server errors', async () => {
  const delays = [], cleared = [];
  const context = vm.createContext({ AbortController,
    setTimeout: (_callback, delay) => { delays.push(delay); return 3; }, clearTimeout: timer => cleared.push(timer),
    fetch: async () => ({ok:false,status:404,json:async()=>({detail:'Case expired.'})}),
  });
  vm.runInContext('async ' + fn('api'), context);
  await assert.rejects(vm.runInContext("api('/api/cases/missing')", context), error => error.status === 404 && error.message === 'Case expired.');
  assert.deepEqual(delays, [20000]);
  assert.deepEqual(cleared, [3]);
});

test('pending request identity blocks execution before history or session-readiness promises settle', async () => {
  const saved = { id: 'a38c3e0e-1727-4912-af5f-64896e64da2c', kind: 'baseline' };
  const prefix = source.slice(source.indexOf('const $ ='), source.indexOf('function rememberLocation'));
  const controls = new Map();
  const context = vm.createContext({ OPERATION_KEY, operationState, readSession,
    window: { sessionStorage: { getItem: key => key === OPERATION_KEY ? JSON.stringify(saved) : null }, prooflaneSessionReady: new Promise(() => {}) },
    document: { getElementById(id) { if (!controls.has(id)) controls.set(id, {value:'reference'}); return controls.get(id); }, querySelectorAll: () => [] },
    canMode: () => true,
  });
  // Only synchronous startup runs; neither history nor readiness has resolved.
  vm.runInContext(prefix + '\n' + fn('syncActions') + '\n' + fn('beginOperation') + '\nasync ' + fn('createCase'), context);
  vm.runInContext('state.match={ready:true}; syncActions()', context);
  assert.equal(controls.get('wb-create').disabled, true);
  assert.equal(controls.get('wb-reviewed-demo').disabled, true);
  await vm.runInContext('createCase()', context);
  assert.equal(vm.runInContext('pendingOperation.id', context), saved.id);
  assert.throws(() => vm.runInContext("beginOperation('baseline')", context), /Check pending result/);
  assert.equal(vm.runInContext('pendingOperation.id', context), saved.id);
});
