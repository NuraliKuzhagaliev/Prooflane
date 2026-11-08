import { money, signedMoney } from './format.js';
import { fieldLabel, modeLabel, valueLabel, completed, completionLabel, decisionLabel, unresolved, chosenContract, validateChange, validateRange, filterMatches, sourceFocus } from './workbench-model.js';
import { LOCATION_KEY, OPERATION_KEY, navigationState, operationState, readSession, writeSession } from './review-session.js';

const $ = id => document.getElementById(id);
const state = { health: null, active: null, view: 'sources', rows: [], busy: false, cases: [], match: null, matchRow: null, selectedRow: null, excludedSourceRow: null, selectedTarget: null, dependency: 'invoice', changes: [], packetText: '', packetRequest: 0, explorePane: 'ranges', sourceRequests: { invoices: 0, contracts: 0 }, sourceLoading: { invoices: false, contracts: false }, synthetic: false, selections: {}, exclusions: {} };
const MAX_CSV = 128 * 1024;
const MAX_PACKET = 8 * 1024 * 1024;
const session = () => { try { return window.sessionStorage; } catch { return null; } };
// Hydrate before handlers or network awaits: a slow history request must never
// enable a second execution that replaces an outcome-unknown request identity.
let pendingOperation = readSession(session(), OPERATION_KEY, operationState);
let busyClock = null;
function rememberLocation() { if (state.active) writeSession(session(), LOCATION_KEY, { id: state.active.id, view: state.view, pane: state.explorePane }, navigationState); }
function renderRecovery() {
  $('wb-operation-recovery').hidden = !pendingOperation;
  if (pendingOperation) text('wb-operation-label', `A ${pendingOperation.kind} request may already have reached the server. Check its status before running it again.`);
}
function beginOperation(kind) {
  if (pendingOperation) throw new Error('Check pending result before starting another run.');
  pendingOperation = { id: crypto.randomUUID(), kind };
  writeSession(session(), OPERATION_KEY, pendingOperation, operationState);
  renderRecovery();
  return pendingOperation.id;
}
function finishOperation() { pendingOperation = null; writeSession(session(), OPERATION_KEY, null, operationState); renderRecovery(); }
async function recoverOperation() {
  if (state.busy || !pendingOperation) return;
  const pending = pendingOperation;
  setBusy(true, 'Checking the saved request status. No calculation or model is started…'); error();
  let completedCase = null;
  try {
    const { operation } = await api(`/api/operations/${idURL(pending.id)}`);
    if (operation.status === 'completed' && operation.case_id) completedCase = operation.case_id;
    else if (operation.status === 'pending') notice('The original request is still running. Check again shortly; no duplicate run was started.');
    else { finishOperation(); error(operation.error || 'This request did not complete. The original baseline remains unchanged. Review the inputs before starting a new request.'); }
  } catch (failure) {
    if (failure.status === 404) finishOperation();
    error(failure.status === 404 ? 'The request status is unavailable in this session or has expired. Check Archive before starting another run.' : failure.message);
  } finally { setBusy(false); }
  if (completedCase && await openCase(completedCase)) { finishOperation(); syncActions(); notice('Recovered the completed result without another calculation or model request.'); }
}
const count = value => value == null ? '—' : new Intl.NumberFormat('en-US').format(value);
const bytes = text => new TextEncoder().encode(text).byteLength;
const idURL = id => encodeURIComponent(String(id));
const endpoint = suffix => `/api/cases/${idURL(state.active.id)}${suffix || ''}`;
const dateLabel = value => { const date = new Date(value); return Number.isNaN(date.getTime()) ? '' : date.toLocaleString('en-US', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' }); };

function el(tag, className = '', value) { const node = document.createElement(tag); if (className) node.className = className; if (value != null) node.textContent = String(value); return node; }
function text(id, value) { $(id).textContent = String(value ?? ''); }
function button(label, handler, className = 'wb-text-button') { const node = el('button', className, label); node.type = 'button'; node.addEventListener('click', handler); return node; }
function link(label, href, className = 'wb-text-button', download = false) { const node = el('a', className, label); node.href = href; if (download) node.download = ''; return node; }
function badge(label, tone = '') { return el('span', `wb-badge ${tone ? `wb-${tone}` : ''}`, label); }
function statusBadge(status) { return badge(decisionLabel(status), ['unmatched', 'ambiguous'].includes(status) ? 'warn' : ['matched', 'selected'].includes(status) ? 'blue' : ''); }
function facts(pairs) { const node = el('dl', 'wb-facts'); for (const [name, value] of pairs) node.append(el('dt', '', name), el('dd', '', value ?? '—')); return node; }
function error(message = '') {
  text('wb-error', message);
  $('wb-error').hidden = !message;
  text('folio-alert', $('folio-archive').open ? '' : message);
  for (const [pane, id] of [['ranges', 'folio-range-error'], ['alternatives', 'folio-alternative-error']]) {
    const localMessage = state.view === 'explore' && state.explorePane === pane ? message : '';
    text(id, localMessage);
    $(id).hidden = !localMessage;
  }
}
function notice(message = '') {
  text('wb-notice', message);
  $('wb-notice').hidden = !message;
  if (message) announce(message);
}
function announce(message) { text('announcement', message); }
function focusPoint(node) {
  if (!node) return;
  if (node.tabIndex < 0) node.tabIndex = -1;
  node.focus({ preventScroll: true });
  node.scrollIntoView({ behavior: 'instant', block: 'nearest', inline: 'nearest' });
}
function setBusy(busy, description = '') {
  if (busyClock) { clearInterval(busyClock); busyClock = null; }
  state.busy = busy;
  $('case-workbench').classList.toggle('is-busy', busy);
  $('wb-main').setAttribute('aria-busy', String(busy));
  $('wb-progress').hidden = !busy;
  text('wb-progress-text', description);
  text('wb-progress-time', '');
  if (busy) {
    const started = Date.now();
    busyClock = setInterval(() => text('wb-progress-time', `${Math.floor((Date.now() - started) / 1000)}s elapsed · waiting for the server's result`), 1000);
  }
  if (busy && !$('folio-archive').open) announce(description);
  document.querySelectorAll('#case-workbench button[data-mutating]').forEach(node => { node.disabled = busy; });
  syncActions();
}
async function api(path, options = {}) {
  const execution = options.method === 'POST' && (path === '/api/cases' || /\/variants$/.test(path));
  const controller = new AbortController();
  const deadline = setTimeout(() => controller.abort(), execution ? 240000 : path === '/api/verify-packet' ? 60000 : 20000);
  try {
    const response = await fetch(path, { credentials: 'same-origin', ...options, signal: controller.signal, headers: { Accept: 'application/json', ...(options.body ? { 'Content-Type': 'application/json', 'X-Prooflane-Request': '1' } : {}), ...options.headers } });
    let data; try { data = await response.json(); } catch { throw new Error('The server returned an unreadable response. Retry when the service is available.'); }
    if (!response.ok) { const failure = new Error(typeof data.detail === 'string' ? data.detail : typeof data.error === 'string' ? data.error : 'The request could not be completed. Check the inputs and try again.'); failure.status = response.status; failure.data = data; throw failure; }
    return data;
  } catch (failure) {
    if (controller.signal.aborted) throw new Error(execution ? 'The response timed out. The server may still be processing this run. Check pending result before starting another run.' : 'The response timed out. Your source text and original baseline are preserved; try this action again when the service is available.');
    throw failure;
  } finally { clearTimeout(deadline); }
}
function post(path, payload) { return api(path, { method: 'POST', body: JSON.stringify(payload) }); }
function canMode(mode) { return mode === 'reference' || !!state.health?.docker?.available && (mode !== 'vultr' || !!(state.health?.inference?.configured && state.health?.inference?.enabled)); }
function modeDescription(mode) { return mode === 'reference' ? 'Trusted fixed rules. No model or sandbox.' : mode === 'sandbox' ? 'Fixed Python in Docker; output checked independently.' : 'Vultr generates Python; Docker executes; output checked independently.'; }
function currentMatch() { return state.active?.source || state.match; }
function targetById(id) { return state.active?.targets?.find(target => target.id === id); }
function rowById(n) { return state.rows.find(row => String(row.row) === String(n)); }
function rowAnalysis(n) { return state.active?.intelligence?.rows?.find(row => row.row === n); }
function bindingFor(n) { return state.active?.source?.bindings?.find(item => item.row === n); }
function sourceFor(n) { const binding = bindingFor(n); return state.active?.source?.records?.find(item => item.invoice_row === (binding?.invoice_row ?? n)); }
function rowVariance(n) { return rowAnalysis(n)?.baseline ?? state.active?.baseline?.summary?.findings?.find(item => item.row === n)?.variance ?? null; }

function syncActions() {
  $('wb-match').disabled = state.busy || Object.values(state.sourceLoading).some(Boolean) || !$('wb-invoices').value.trim() || !$('wb-contracts').value.trim();
  $('wb-sample').disabled = state.busy;
  $('wb-reviewed-demo').disabled = state.busy || !!pendingOperation;
  $('wb-check-operation').disabled = state.busy;
  $('wb-new').disabled = state.busy;
  $('wb-rail-toggle').disabled = state.busy;
  document.querySelectorAll('[data-explore-pane]').forEach(node => { node.disabled = state.busy; });
  $('wb-create').disabled = state.busy || !!pendingOperation || Object.values(state.sourceLoading).some(Boolean) || !state.match?.ready || !canMode($('wb-execution-mode').value);
  $('wb-save-bound').disabled = state.busy || !state.active;
  $('wb-reset-bounds').disabled = state.busy || !state.active?.bounds?.length;
  $('wb-remove-bound').disabled = state.busy;
  $('wb-add-change').disabled = state.busy || state.changes.length >= (state.active?.limits?.max_changes || 12);
  $('wb-run-alternative').disabled = state.busy || !!pendingOperation || !state.active || !state.changes.length || (state.active.variants?.length || 0) >= (state.active.limits?.max_variants || 4) || !canMode(state.active.baseline.mode);
  $('wb-verify').disabled = state.busy || !state.packetText.trim();
  for (const name of ['wb-invoices', 'wb-contracts', 'wb-invoice-file', 'wb-contract-file', 'wb-name', 'wb-execution-mode', 'wb-bound-low', 'wb-bound-high', 'wb-range-target', 'wb-change-target', 'wb-change-value', 'wb-alternative-name', 'wb-packet-file', 'wb-packet-json']) $(name).disabled = state.busy;
  document.querySelectorAll('[data-wb-view]').forEach(node => { const view = node.dataset.wbView; node.disabled = state.busy || (!state.active && ['overview', 'explore'].includes(view)); });
}

function selectView(view, focus = false) {
  if (state.busy || !state.active && ['overview', 'explore'].includes(view)) return;
  state.view = view;
  for (const name of ['sources', 'overview', 'explore', 'evidence']) $(`wb-view-${name}`).hidden = name !== view;
  document.querySelectorAll('.folio-chapters [data-wb-view]').forEach(node => {
    if (node.dataset.wbView === view) node.setAttribute('aria-current', 'page');
    else node.removeAttribute('aria-current');
  });
  if (view === 'sources' && state.active) renderSources();
  if (view === 'overview' && state.active) { state.excludedSourceRow = null; if (!rowById(state.selectedRow)) state.selectedRow = state.rows[0]?.row; renderRows(); renderRowInspector(); }
  if (view === 'evidence' && state.active) { $('wb-evidence-row').value = state.excludedSourceRow ? `excluded:${state.excludedSourceRow}` : String(state.selectedRow); renderDependency(); }
  if (focus) focusPoint($(`wb-${view}-heading`));
  rememberLocation();
}

async function refreshCases() {
  $('wb-refresh').disabled = true;
  try { const result = await api('/api/cases'); state.cases = result.cases || []; renderCases(); $('wb-history-error').hidden = true; }
  catch (failure) { text('wb-history-error', 'Case history could not be loaded.'); $('wb-history-error').hidden = false; }
  finally { $('wb-refresh').disabled = false; }
}
function renderCases() {
  $('wb-case-list').replaceChildren(); $('wb-cases-empty').hidden = !!state.cases.length;
  for (const item of state.cases.slice(0, 12)) {
    const li = el('li');
    const node = button('', async () => {
      if (await openCase(item.id)) closeArchive($('wb-overview-heading'));
    }, item.id === state.active?.id ? 'selected' : '');
    node.append(el('strong', '', item.name), el('small', '', `${dateLabel(item.created_at)} · ${item.variant_count || 0} ${(item.variant_count || 0) === 1 ? 'alternative' : 'alternatives'}`));
    li.append(node);
    $('wb-case-list').append(li);
  }
}
function renderHeader() {
  const current = state.active;
  text('wb-title', current?.name || 'Start an invoice review');
  text('wb-subtitle', current ? `${count(current.baseline.summary?.row_count)} included invoice rows · ${count(current.source.counts?.excluded || 0)} excluded · ${modeLabel[current.baseline.mode]}` : 'Compare billed prices with contract terms and resolve any uncertain matches.');
  text('wb-mode', current ? completionLabel(current.baseline) : 'New review'); $('wb-mode').className = `wb-badge${current ? current.baseline.mode === 'reference' ? ' wb-blue' : ' wb-good' : ''}`;
  $('wb-packet').hidden = !current; $('wb-identity').hidden = !current;
  if (current) {
    $('wb-packet').href = endpoint('/packet'); $('wb-packet').download = `prooflane-case-${current.id}.json`;
    $('wb-identity').replaceChildren(el('span', '', `Baseline ${dateLabel(current.baseline.created_at || current.created_at)}`), el('span', '', '·'), el('code', '', `RUN ${current.baseline.id.slice(0, 12)}`), button('Copy ID', () => copy(current.baseline.id, 'Baseline run ID copied.'), 'wb-copy'), el('span', '', `Revision ${current.revision}`));
  }
  const n = currentMatch()?.counts?.unresolved || 0;
  text('wb-source-count', n || ''); text('wb-tab-source-count', n || '');
  text('wb-alt-count', current?.variants?.length || ''); text('wb-tab-alt-count', current?.variants?.length || '');
  renderCases();
}
async function copy(value, success) { try { await navigator.clipboard.writeText(value); notice(success); } catch { notice('Copy is unavailable in this browser. Select the full value in Proof.'); } }

function invalidateSourceReads(kind) {
  for (const key of kind ? [kind] : ['invoices', 'contracts']) { state.sourceRequests[key]++; state.sourceLoading[key] = false; }
}
function resetDraft() {
  invalidateSourceReads();
  state.active = null; state.rows = []; state.match = null; state.matchRow = null; state.selectedRow = null; state.excludedSourceRow = null; state.selectedTarget = null; state.selections = {}; state.exclusions = {}; state.changes = []; state.synthetic = false;
  $('wb-name').value = 'Supplier review'; $('wb-invoices').value = ''; $('wb-contracts').value = ''; $('wb-invoice-file').value = ''; $('wb-contract-file').value = ''; $('wb-operator-token').value = ''; $('wb-alternative-token').value = ''; $('wb-alternative-name').value = ''; $('wb-match-search').value = ''; $('wb-match-filter').value = 'all';
  text('wb-invoice-file-label', 'UTF-8 CSV · up to 128 KiB · 500 rows'); text('wb-contract-file-label', 'USD prices · inclusive effective dates'); text('wb-draft-label', 'Exact vendor + item + invoice date. No fuzzy matching.');
  notice(); error(); renderHeader(); renderSources(); renderEvidence(); selectView('sources'); syncActions(); focusPoint($('wb-title'));
  writeSession(session(), LOCATION_KEY, null, navigationState);
}
function invalidateSources() {
  if (state.busy) return;
  state.match = null; state.matchRow = null; state.selections = {}; state.exclusions = {}; state.synthetic = false;
  text('wb-draft-label', 'Source draft changed. Match the current files before creating a baseline.'); renderSources(); renderHeader(); syncActions(); error();
  $('wb-source-repair').hidden = true;
}
async function loadSource(file, kind) {
  if (!file || state.busy) return;
  invalidateSourceReads(kind);
  const request = state.sourceRequests[kind];
  const label = kind === 'invoices' ? 'wb-invoice-file-label' : 'wb-contract-file-label';
  state.sourceLoading[kind] = true; $(`wb-${kind}`).value = ''; invalidateSources(); text(label, `Reading ${file.name}…`);
  try {
    if (file.size > MAX_CSV) throw new Error('Each CSV must be at most 128 KiB.');
    if (!/\.csv$/i.test(file.name)) throw new Error('Choose a .csv file.');
    const csv = await file.text();
    if (request !== state.sourceRequests[kind] || state.busy || state.active) return;
    if (!csv.trim()) throw new Error('The selected CSV is empty.');
    $(`wb-${kind}`).value = csv; invalidateSources(); text(label, `${file.name} · ${count(file.size)} bytes`); announce(`${file.name} loaded.`);
  } catch (failure) { if (request === state.sourceRequests[kind]) { text(label, 'Source not loaded'); sourceError(failure.message); } }
  finally { if (request === state.sourceRequests[kind]) { state.sourceLoading[kind] = false; syncActions(); } }
}
async function matchSources({ chooseFirst = false } = {}) {
  if (state.busy || Object.values(state.sourceLoading).some(Boolean)) return;
  error(); notice(); setBusy(true, 'Matching exact vendor, item and invoice date against the supplied contracts…');
  state.match = null;
  try {
    const invoices = $('wb-invoices').value; const contracts = $('wb-contracts').value;
    if (bytes(invoices) > MAX_CSV || bytes(contracts) > MAX_CSV) throw new Error('Each CSV must be at most 128 KiB.');
    state.match = await post('/api/cases/match', { invoices_csv: invoices, contracts_csv: contracts, selections: state.selections, exclusions: state.exclusions });
    if (chooseFirst || state.matchRow == null) { state.matchRow = (state.match.records.find(unresolved) || state.match.records[0])?.invoice_row; $('wb-match-filter').value = state.match.counts.unresolved ? 'unresolved' : 'all'; }
    if (!state.match.counts.unresolved && $('wb-match-filter').value === 'unresolved') $('wb-match-filter').value = 'all';
    $('wb-source-repair').hidden = true;
    announce(`${state.match.counts.total} invoice rows. ${state.match.counts.unresolved} unresolved, ${state.match.counts.excluded} excluded.`);
  } catch (failure) { sourceError(failure.message); }
  finally {
    renderSources(); renderHeader(); setBusy(false);
    if (state.match) focusPoint(chooseFirst ? $('wb-source-decisions') : $('wb-match-inspector').querySelector('h3'));
    else focusPoint($('wb-source-repair').querySelector('h3'));
  }
}

function sourceError(message) {
  error(message);
  $('wb-import').open = true;
  text('wb-source-repair-message', message);
  $('wb-source-repair').hidden = false;
}
function editSource(kind) {
  if (state.busy || state.active) return;
  $('wb-import').open = true;
  const input = $(`wb-${kind}`);
  input.closest('details').open = true;
  focusPoint(input);
}
function downloadStarter(kind) {
  const sample = kind === 'invoices'
    ? 'invoice_id,vendor,item_id,invoice_date,quantity,unit_price,notes\nEXAMPLE-001,Example supplier,ITEM-001,2026-11-01,10,12.50,Fictional starter row\n'
    : 'contract_id,vendor,item_id,valid_from,valid_to,contract_price\nEXAMPLE-C1,Example supplier,ITEM-001,2026-11-01,2026-11-30,10.00\n';
  const url = URL.createObjectURL(new Blob([sample], { type: 'text/csv;charset=utf-8' }));
  const a = link('', url, '', true); a.download = `prooflane-${kind}-starter.csv`; document.body.append(a); a.click(); a.remove();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
  announce('Starter CSV downloaded. Replace the fictional row with your source data.');
}
function inspectSourceRow(invoiceRow) {
  state.matchRow = invoiceRow;
  $('wb-match-search').value = ''; $('wb-match-filter').value = 'all';
  selectSourceRecord(invoiceRow); renderMatchTable(); renderMatchInspector();
  focusPoint($('wb-match-inspector').querySelector('h3'));
}
function renderDecisionQueue(report) {
  const c = report.counts;
  const pending = report.records.filter(unresolved);
  const node = $('wb-decision-queue'); node.replaceChildren();
  const summary = el('div'); const heading = el('h3', '', pending.length ? 'Resolve the source decisions' : 'Every source row is accounted for'); heading.id = 'wb-decision-queue-heading';
  summary.append(el('p', 'wb-kicker', state.active ? 'FROZEN SOURCE RECORD' : 'BEFORE THE BASELINE'), heading,
    el('p', '', `${c.total - c.unresolved} of ${c.total} rows accounted for · ${c.excluded || 0} explicitly excluded`));
  const progress = el('progress'); progress.max = c.total; progress.value = c.total - c.unresolved; progress.setAttribute('aria-label', 'Source rows accounted for'); summary.append(progress);
  node.append(summary);
  const queue = el('div', 'wb-queue-items');
  if (pending.length) {
    for (const record of pending.slice(0, 5)) {
      const item = button('', () => inspectSourceRow(record.invoice_row), 'wb-queue-item');
      item.append(el('span', '', record.status === 'ambiguous' ? 'CHOOSE A CONTRACT' : 'CHECK THE SOURCE'), el('strong', '', record.invoice_id), el('small', '', `Source row ${record.invoice_row} · ${record.status === 'ambiguous' ? `${record.candidates.length} eligible contracts` : 'No eligible contract'}`)); queue.append(item);
    }
    if (pending.length > 5) queue.append(button(`View all ${pending.length} unresolved rows`, () => { $('wb-match-filter').value = 'unresolved'; renderMatchTable(); focusPoint($('wb-match-search')); }, 'wb-text-button'));
  } else queue.append(el('p', '', state.active ? 'These decisions are preserved with the baseline. Select a row below to trace its evidence.' : report.ready ? 'Next: choose an execution mode and create the baseline below.' : 'All rows were excluded. Include at least one invoice to create a baseline.'));
  node.append(queue);
}
function renderSourceInsights(report) {
  const analysis = state.active?.review_insights || report.review_insights;
  const node = $('wb-source-insights'); node.replaceChildren(); node.hidden = !analysis;
  if (!analysis) return;
  const coverage = analysis.coverage;
  if (coverage) {
    const amounts = el('div', 'wb-coverage-money');
    for (const [label, value] of [['Included billed amount', coverage.included_billed], ['Excluded billed amount', coverage.excluded_billed], ['Unresolved billed amount', coverage.unresolved_billed]]) { const item = el('div'); item.append(el('small', '', label), el('strong', '', money(value))); amounts.append(item); }
    node.append(amounts, el('p', 'wb-help', 'Billed amounts describe coverage. Excluded or unresolved amounts are not estimated price variances or recoverable savings.'));
  }
  for (const group of analysis.duplicate_groups || []) {
    const warning = el('div', 'wb-duplicate-warning');
    warning.append(el('strong', '', `Possible duplicate source rows · ${group.invoice_id}`), el('p', '', group.reason || 'These invoice fields match. Check the source before treating them as separate invoices.'));
    for (const row of group.invoice_rows) warning.append(button(`Inspect source row ${row}`, () => inspectSourceRow(row), 'wb-text-button'));
    warning.append(el('small', '', 'No rows were automatically excluded. Matching fields alone do not establish a duplicate payment.')); node.append(warning);
  }
}

function renderSources() {
  const report = currentMatch();
  $('wb-import').open = !report || !$('wb-source-repair').hidden;
  $('wb-import').hidden = !!state.active; $('wb-sample').hidden = !!state.active; $('wb-saved-sources').hidden = !state.active; $('wb-match-workspace').hidden = !report; $('wb-source-empty').hidden = !!report; $('wb-create-footer').hidden = !!state.active;
  $('wb-first-use').hidden = !!report;
  if (!report) return;
  renderDecisionQueue(report); renderSourceInsights(report);
  const c = report.counts; $('wb-coverage').replaceChildren();
  for (const [label, amount, css] of [['source rows', c.total, ''], ['exact matches', c.matched, ''], ['selected', c.selected, ''], ...(c.embedded ? [['embedded prices', c.embedded, '']] : []), ['unresolved', c.unresolved, c.unresolved ? 'wb-unresolved' : ''], ['excluded', c.excluded, '']]) { const node = el('span', css); node.append(el('strong', '', count(amount || 0)), document.createTextNode(label)); $('wb-coverage').append(node); }
  if (!state.matchRow || !report.records.some(row => row.invoice_row === state.matchRow)) state.matchRow = (report.records.find(unresolved) || report.records[0])?.invoice_row;
  renderMatchTable(); renderMatchInspector();
  text('wb-create', report.ready || state.active ? `Create baseline · ${count(c.matched + c.selected + (c.embedded || 0))} rows` : c.unresolved ? `Resolve ${count(c.unresolved)} source ${c.unresolved === 1 ? 'match' : 'matches'}` : 'Include at least one row');
}
function renderMatchTable() {
  const records = filterMatches(currentMatch()?.records || [], $('wb-match-filter').value, $('wb-match-search').value);
  $('wb-matches-body').replaceChildren(); $('wb-matches-empty').hidden = !!records.length;
  for (const record of records) {
    const selected = record.invoice_row === state.matchRow;
    const tr = el('tr', selected ? 'selected' : '');
    const invoice = el('th');
    invoice.scope = 'row';
    const inspect = button(record.invoice_id, () => {
      selectSourceRecord(record.invoice_row);
      renderMatchTable();
      renderMatchInspector(true);
      focusPoint($('wb-match-inspector').querySelector('h3'));
    }, 'wb-row-link');
    inspect.id = `wb-match-row-${record.invoice_row}`;
    inspect.setAttribute('aria-controls', 'wb-match-inspector');
    if (selected) inspect.setAttribute('aria-current', 'true');
    invoice.append(inspect, el('small', '', `${record.vendor} · ${record.item_id || 'embedded'} · row ${record.invoice_row}`));
    const contract = el('td', 'wb-source-ref', record.chosen_contract_id || (record.status === 'ambiguous' ? `${record.candidates.length} candidates` : record.status === 'embedded' ? 'Embedded' : '—')); const status = el('td'); status.append(statusBadge(record.status));
    tr.append(invoice, el('td', '', record.invoice_date || '—'), contract, status); $('wb-matches-body').append(tr);
  }
}
function renderMatchInspector(animate = false) {
  const node = $('wb-match-inspector'); node.replaceChildren(); const record = currentMatch()?.records?.find(row => row.invoice_row === state.matchRow);
  if (!record) { node.append(el('p', 'wb-empty-small', 'Choose an invoice to inspect its source match.')); return; }
  node.append(el('p', 'wb-kicker', `INVOICE SOURCE ROW ${record.invoice_row}`), el('h3', '', record.invoice_id), el('p', 'wb-inspector-sub', record.vendor), statusBadge(record.status), facts([['Item key', record.item_id || 'Not in embedded CSV'], ['Invoice date', record.invoice_date || 'Not in embedded CSV'], ['Quantity', record.quantity], ['Billed unit price', money(record.unit_price)]]));
  addInspectorNavigation(node, 'wb-match-row', record.invoice_row, record.invoice_id, 'wb-match-search', animate);
  if (record.status === 'embedded') node.append(el('p', 'wb-help', `Embedded contract price ${money(record.contract_price)}. No separate contract source was checked.`));
  for (const candidate of record.candidates || []) {
    const item = el('div', `wb-candidate${candidate.contract_id === record.chosen_contract_id ? ' selected' : ''}`); const head = el('div'); head.append(el('strong', '', candidate.contract_id), el('strong', '', money(candidate.contract_price))); item.append(head, el('p', '', `Contract row ${candidate.contract_row} · ${candidate.valid_from} → ${candidate.valid_to}`));
    if (candidate.contract_id === record.chosen_contract_id) item.append(badge(record.status === 'selected' ? 'Explicitly selected' : 'Exact dated match', 'blue'));
    else if (!state.active) { const choose = button(`Use ${candidate.contract_id}`, async () => { state.selections[String(record.invoice_row)] = candidate.contract_id; delete state.exclusions[String(record.invoice_row)]; await matchSources(); }, 'wb-button'); choose.dataset.mutating = 'true'; choose.disabled = state.busy; item.append(choose); }
    const conditional = (state.active?.review_insights || currentMatch()?.review_insights)?.rival_contracts?.find(rival => rival.invoice_row === record.invoice_row)?.candidates?.find(rival => rival.contract_id === candidate.contract_id);
    if (conditional) item.append(el('p', 'wb-candidate-effect', `This invoice's positive variance would be ${money(conditional.invoice_variance)} with this eligible price. Other rows and contract validity are not assessed by this comparison.`));
    node.append(item);
  }
  if (record.status === 'unmatched') node.append(el('p', 'wb-help', 'No eligible contract for this exact vendor, item and invoice date. Correct the source or record an explicit exclusion below.'));
  if (record.status === 'ambiguous') node.append(el('p', 'wb-help', 'Overlapping supplied contracts. Choose the applicable row explicitly; the selection is recorded with the case.'));
  if (record.reason) node.append(facts([['Exclusion reason', record.reason]]));
  if (!state.active) {
    if (record.status === 'excluded' || record.status === 'selected') { const reset = button('Remove this decision', async () => { delete state.selections[String(record.invoice_row)]; delete state.exclusions[String(record.invoice_row)]; await matchSources(); }); reset.dataset.mutating = 'true'; node.append(reset); }
    if (record.status !== 'excluded') {
      const details = el('details', 'wb-exclusion'); details.open = record.status === 'unmatched'; details.append(el('summary', '', 'Exclude this invoice with a reason'));
      const label = el('label', '', 'Reason for exclusion'); label.htmlFor = 'wb-exclusion-reason'; const reason = el('textarea'); reason.id = 'wb-exclusion-reason'; reason.maxLength = 200; reason.rows = 2; reason.placeholder = 'Explain why this row is outside this review.';
      const exclude = button('Record exclusion', async () => { if (reason.value.trim().length < 3) { error('An exclusion needs a reason of 3 to 200 characters.'); reason.focus(); return; } state.exclusions[String(record.invoice_row)] = reason.value.trim(); delete state.selections[String(record.invoice_row)]; await matchSources(); }, 'wb-button'); exclude.dataset.mutating = 'true'; details.append(label, reason, exclude); node.append(details);
    }
  }
  node.append(el('p', 'wb-help', 'Matching a supplied price is not authentication of the contract or its applicability.'));
  if (state.active) node.append(button(record.status === 'excluded' ? 'Follow this exclusion in Proof →' : 'Follow this source in Proof →', () => { selectSourceRecord(record.invoice_row); renderEvidence(); selectView('evidence', true); }));
}

function selectSourceRecord(invoiceRow) {
  state.matchRow = invoiceRow;
  if (!state.active) return;
  const focus = sourceFocus(state.active.source, invoiceRow);
  state.selectedRow = focus?.row ?? null;
  state.excludedSourceRow = focus?.excludedSourceRow ?? null;
  state.dependency = 'invoice';
  renderEvidence();
}

async function acceptCase(current, { reset = false } = {}) {
  // Source endpoint contains every normalized record, including zero-variance rows.
  // Commit identities and their source records together, after the dependent fetch.
  const result = await api(`/api/runs/${idURL(current.baseline.id)}/source`);
  invalidateSourceReads();
  state.active = current; state.rows = result.rows;
  if (reset) { state.changes = []; state.groupRows = null; state.groupLabel = ''; $('wb-alternative-name').value = ''; $('wb-change-value').value = ''; state.selectedTarget = null; state.selectedRow = null; state.excludedSourceRow = null; state.matchRow = null; $('wb-row-search').value = ''; $('wb-row-filter').value = 'positive'; }
  state.selectedRow = state.rows.some(row => row.row === state.selectedRow) ? state.selectedRow : current.baseline.summary.findings[0]?.row || state.rows[0]?.row;
  state.selectedTarget = targetById(state.selectedTarget) ? state.selectedTarget : current.targets[0]?.id;
  renderHeader(); renderSources(); renderOverview(); renderExplore(); renderEvidence(); syncActions();
  rememberLocation();
}
async function openCase(id) {
  if (state.busy) return false;
  invalidateSourceReads(); error(); notice(); setBusy(true, 'Opening the saved case and its source records…');
  try {
    const result = await api(`/api/cases/${idURL(id)}`);
    await acceptCase(result.case, { reset: true });
  } catch (failure) {
    error(failure.message);
    if ($('folio-archive').open) {
      const message = $('folio-archive-error');
      message.textContent = failure.message;
      message.hidden = false;
      focusPoint(message);
    }
    return false;
  } finally {
    setBusy(false);
  }
  selectView('overview');
  return true;
}
async function createCase() {
  if (state.busy || pendingOperation || Object.values(state.sourceLoading).some(Boolean) || !state.match?.ready) return; error(); notice(); const mode = $('wb-execution-mode').value;
  const payload = { name: $('wb-name').value.trim() || 'Supplier review', mode, invoices_csv: $('wb-invoices').value, contracts_csv: $('wb-contracts').value, selections: state.selections, exclusions: state.exclusions, request_id: beginOperation('baseline') };
  if (mode === 'vultr') payload.operator_token = $('wb-operator-token').value;
  setBusy(true, `Creating the frozen baseline. ${modeDescription(mode)}`);
  try {
    const result = await post('/api/cases', payload);
    if (!result.case) { notice('This request is already running. Use Check pending result to retrieve it without starting another run.'); return; }
    await acceptCase(result.case, { reset: true }); finishOperation(); await refreshCases(); announce(`Case created. ${completionLabel(result.case.baseline)}.`);
  }
  catch (failure) {
    if (failure.status && failure.status !== 409) finishOperation();
    const runError = failure.data?.failed_run?.error;
    const detail = typeof runError === 'string' && runError !== failure.message ? ` ${runError.slice(0, 600)}` : '';
    error(`${failure.message}${detail}${pendingOperation ? ' Check the pending result before starting another run.' : ''}`);
  }
  finally { $('wb-operator-token').value = ''; setBusy(false); if (state.active) selectView('overview', true); else focusPoint($('wb-create')); }
}

function renderOverview() {
  if (!state.active) return; const { baseline, source } = state.active; const summary = baseline.summary, coverage = source.counts;
  const result = el('div', 'folio-result'); result.append(el('span', '', 'POSITIVE PRICE VARIANCE IN USD'), el('strong', '', money(summary.total_variance)), el('small', '', 'Above the supplied prices · original calculation'));
  const scope = el('div', 'folio-scope-note'); scope.append(el('strong', '', `${summary.row_count} of ${coverage.total} invoices in scope.`), el('p', '', `${coverage.excluded || 0} explicitly excluded. Every exclusion stays in the source record.`), button('Read the source decisions →', () => selectView('sources', true), 'wb-text-button'));
  const conclusion = el('div', 'folio-conclusion'); conclusion.append(result, scope);
  const bookkeeping = el('div', 'folio-bookkeeping'); for (const [label, value] of [['Total billed', money(summary.total_billed)], ['Flagged for review', `${summary.flagged_count} of ${summary.row_count}`], ['Original mode', modeLabel[baseline.mode]]]) { const item = el('span', '', label); item.append(el('strong', '', value)); bookkeeping.append(item); }
  $('wb-metrics').replaceChildren(conclusion, bookkeeping);
  const sources = source.kind === 'embedded' ? 'Embedded prices · no separate contract source' : `${coverage.selected} explicit contract ${coverage.selected === 1 ? 'selection' : 'selections'}`;
  $('wb-overview-signals').replaceChildren(button(sources, () => selectView('sources', true), 'wb-signal'), button(`${state.active.bounds.length} declared ranges →`, () => { setExplorePane('ranges'); selectView('explore', true); }, 'wb-signal'), button(`${state.active.variants.length} executed alternatives →`, () => { setExplorePane('alternatives'); selectView('explore', true); }, 'wb-signal'));
  text('wb-row-count', `${summary.flagged_count} flagged`); renderContractGroups(); renderRows(); renderRowInspector();
}
function renderContractGroups() {
  const node = $('wb-contract-groups'); const groups = state.active.review_insights?.groups || []; node.hidden = !groups.length; node.replaceChildren();
  if (!groups.length) return;
  const heading = el('h3', '', 'Review by shared contract'); heading.id = 'wb-contract-groups-heading';
  node.append(heading, el('p', 'wb-help', 'One contract price can affect several invoices. These totals use the supplied original values.'));
  const list = el('ul', 'wb-contract-group-list');
  for (const group of groups) {
    const item = el('li'); const action = button('', () => { state.groupRows = group.rows; state.groupLabel = group.contract_id || 'Embedded contract price'; $('wb-row-search').value = ''; $('wb-row-filter').value = 'all'; selectRow(group.rows[0]); }, 'wb-contract-group');
    const title = el('span'); title.append(el('strong', '', group.contract_id || 'Embedded contract price'), el('small', '', `${group.vendor} · ${group.row_count} invoice ${group.row_count === 1 ? 'row' : 'rows'} · ${group.flagged_count} flagged`));
    const amount = el('span'); amount.append(el('strong', '', money(group.total_variance)), el('small', '', `${money(group.total_billed)} billed`)); action.append(title, amount); item.append(action); list.append(item);
  }
  node.append(list);
}
function renderRows() {
  if (!state.active) return; const needle = $('wb-row-search').value.trim().toLowerCase(); const rows = state.rows.filter(row => (!state.groupRows || state.groupRows.includes(row.row)) && ($('wb-row-filter').value === 'all' || rowAnalysis(row.row)?.possible_positive && rowVariance(row.row) !== '0.00' || state.active.baseline.summary.findings.some(f => f.row === row.row)) && `${row.invoice_id} ${row.vendor}`.toLowerCase().includes(needle));
  const groupFilter = $('wb-group-filter'); groupFilter.replaceChildren(); groupFilter.hidden = !state.groupRows;
  if (state.groupRows) groupFilter.append(el('span', '', `Showing ${state.groupLabel}: ${state.groupRows.length} bound invoice rows`), button('Show every contract', () => { state.groupRows = null; state.groupLabel = ''; renderRows(); focusPoint($('wb-row-search')); }, 'wb-text-button'));
  const visibleFlagged = rows.filter(row => rowVariance(row.row) != null && rowVariance(row.row) !== '0.00').length;
  text('wb-row-count', `${visibleFlagged} flagged · ${rows.length} shown`);
  $('wb-rows-body').replaceChildren(); $('wb-rows-empty').hidden = !!rows.length;
  for (const row of rows) {
    const selected = row.row === state.selectedRow;
    const tr = el('tr', selected ? 'selected' : '');
    const first = el('th');
    first.scope = 'row';
    const binding = bindingFor(row.row);
    const inspect = button(row.invoice_id, () => selectRow(row.row), 'wb-row-link');
    inspect.id = `wb-ledger-row-${row.row}`;
    inspect.setAttribute('aria-label', `Inspect ${row.invoice_id}, invoice source row ${binding?.invoice_row ?? row.row}, normalized row ${row.row}`);
    inspect.setAttribute('aria-controls', 'wb-row-inspector');
    if (selected) inspect.setAttribute('aria-current', 'true');
    first.append(inspect, el('small', '', row.vendor));
    const source = el('td');
    source.append(el('span', 'wb-source-ref', binding ? `Invoice ${binding.invoice_row} → contract ${binding.contract_row}` : `CSV row ${row.row}`), el('small', '', binding?.contract_id || 'Embedded contract price'));
    const amount = el('td', 'wb-num');
    amount.append(el('strong', '', money(rowVariance(row.row))));
    tr.append(first, source, amount);
    $('wb-rows-body').append(tr);
  }
}
function selectRow(n) {
  state.selectedRow = n;
  state.excludedSourceRow = null;
  state.matchRow = bindingFor(n)?.invoice_row ?? n;
  renderRows();
  renderRowInspector(true);
  focusPoint($('wb-row-inspector').querySelector('h3'));
}
function addInspectorNavigation(node, rowIdPrefix, row, invoice, searchId, animate) {
  if (animate) {
    const rule = el('span', 'folio-note-rule');
    rule.setAttribute('aria-hidden', 'true');
    node.prepend(rule);
  }
  const back = button('Back to table ↑', () => focusPoint($(`${rowIdPrefix}-${row}`) || $(searchId)), 'wb-text-button wb-back-to-row');
  back.setAttribute('aria-label', `Back to table, ${invoice}`);
  node.querySelector('h3').after(back);
}
function renderRowInspector(animate = false) {
  const node = $('wb-row-inspector'); node.replaceChildren(); const row = rowById(state.selectedRow); if (!row) { node.append(el('p', 'wb-empty-small', 'Select an included row to inspect the supporting evidence.')); return; }
  const source = sourceFor(row.row); const binding = bindingFor(row.row);
  node.append(el('p', 'wb-kicker', 'SELECTED SOURCE RECORD'), el('h3', '', row.invoice_id), el('p', 'wb-inspector-sub', row.vendor));
  addInspectorNavigation(node, 'wb-ledger-row', row.row, row.invoice_id, 'wb-row-search', animate);
  if (source) node.append(statusBadge(source.status));
  const chain = el('div', 'wb-link-chain'); for (const [label, value] of [['Invoice source', `row ${binding?.invoice_row ?? row.row}`], ['Contract source', binding ? `${binding.contract_id} · row ${binding.contract_row}` : 'Embedded price'], ['Normalized record', `row ${row.row}`]]) { const item = el('span'); item.append(document.createTextNode(label), el('strong', '', value)); chain.append(item); } node.append(chain);
  node.append(facts([['Quantity', row.quantity], ['Billed unit price', money(row.unit_price)], ['Contract price', money(row.contract_price)], ...(source?.item_id ? [['Item key', source.item_id], ['Invoice date', source.invoice_date]] : [])]));
  const formula = el('div', 'wb-formula'); formula.append(el('small', '', 'Positive price variance'), el('p', '', `max(${money(row.unit_price)} − ${money(row.contract_price)}, $0) × ${row.quantity}`), el('strong', '', money(rowVariance(row.row)))); node.append(formula);
  node.append(button('Explore assumptions on this row →', () => { const target = state.active.targets.find(item => item.rows.includes(row.row) && item.field === 'contract_price'); chooseTarget(target?.id); setExplorePane('ranges'); selectView('explore', true); }, 'wb-button'), button('Follow the evidence path ↗', () => { $('wb-evidence-row').value = String(row.row); state.dependency = 'invoice'; renderDependency(); selectView('evidence', true); }));
  if (source?.notes) node.append(el('p', 'wb-help', source.notes));
}

function populateTargets(id, selected) {
  const select = $(id); select.replaceChildren();
  for (const target of state.active.targets) { const option = el('option', '', `${target.label} · ${target.rows.length} ${target.rows.length === 1 ? 'row' : 'rows'}`); option.value = target.id; select.append(option); }
  if (targetById(selected)) select.value = selected;
}
function chooseTarget(id) {
  if (!targetById(id)) return;
  error();
  state.selectedTarget = id;
  $('wb-range-target').value = id;
  renderTargetEditor();
  renderTornado();
}
function editTarget(id) {
  chooseTarget(id);
  focusPoint($('wb-range-target'));
}
function renderTargetEditor() {
  const target = targetById(state.selectedTarget); if (!target) return;
  const bound = state.active.bounds.find(item => item.target === target.id);
  $('wb-bound-low').value = bound?.low ?? target.before; $('wb-bound-high').value = bound?.high ?? target.before;
  for (const id of ['wb-bound-low', 'wb-bound-high']) {
    const input = $(id);
    input.inputMode = target.field === 'quantity' ? 'numeric' : 'decimal';
    input.setAttribute('aria-label', `${id === 'wb-bound-low' ? 'Low value' : 'High value'} for ${fieldLabel[target.field]}`);
    input.removeAttribute('aria-invalid');
  }
  const context = $('wb-target-context'); context.replaceChildren(el('strong', '', `Original ${valueLabel(target.field, target.before)}`), el('p', '', `${fieldLabel[target.field]} · ${target.contract_id ? 'shared contract' : 'one source record'}`), el('p', '', `Applies to ${target.rows.map(n => rowById(n)?.invoice_id || `row ${n}`).join(', ')}`));
  $('wb-remove-bound').hidden = !bound; text('wb-save-bound', bound ? 'Update range' : 'Apply range');
}
function renderExplore() {
  if (!state.active) return;
  const analysis = state.active.intelligence;
  text('folio-original-amount', money(state.active.baseline.summary.total_variance)); text('folio-original-scope', `${state.active.baseline.summary.row_count} included invoices · ${completionLabel(state.active.baseline)}`); setExplorePane(state.explorePane || 'ranges');
  const range = el('div'); range.append(el('strong', '', `${money(analysis.low)} — ${money(analysis.high)}`), el('small', '', 'Exact bounds under the declared assumptions · calculated range'));
  const scope = el('div'); scope.append(el('strong', '', `${count(analysis.range_count)} declared ${analysis.range_count === 1 ? 'range' : 'ranges'}`), el('small', '', `Width ${money(analysis.width)} · original ${money(analysis.baseline_variance)}`));
  $('wb-range-summary').replaceChildren(range, scope);
  const oldChange = $('wb-change-target').value;
  populateTargets('wb-range-target', state.selectedTarget); populateTargets('wb-change-target', oldChange || state.selectedTarget); renderTargetEditor(); renderChangeOriginal(); renderTornado(); renderNextFacts(); renderPrioritySwitch(); renderAlternatives();
}
function renderPrioritySwitch() {
  const analysis = state.active.priority_switch;
  $('wb-priority-switch').hidden = !analysis;
  if (!analysis) return;
  const node = $('wb-priority-switch-content');
  node.replaceChildren();
  const unavailable = {
    no_positive: 'The original has no positive price differences to rank.',
    baseline_tie: 'The original already has a tie for first place. Inspect the tied invoices before choosing a priority.',
    single_invoice: 'Only one invoice is included. There is no other invoice to compare for first place.',
  };
  if (analysis.status !== 'available') {
    node.append(el('p', 'wb-help', unavailable[analysis.status] || 'No priority boundary is available.'));
    return;
  }
  const candidate = rowById(analysis.candidate_row);
  const name = candidate?.invoice_id || `Record ${analysis.candidate_row}`;
  node.append(el('p', 'wb-help', `${name} is first at the original ${analysis.label} price of ${money(analysis.original_price)}. ${analysis.scope}`));
  for (const transition of analysis.transitions) {
    const section = el('section', 'wb-priority-transition');
    const direction = transition.direction === 'increase' ? 'increases' : 'decreases';
    section.append(el('h4', '', `When ${analysis.label} ${direction}`));
    const grid = el('div', 'wb-priority-witnesses');
    for (const [label, witness] of [['Last strict priority', transition.last_strict], ['First change', transition.at], ['One cent further', transition.beyond]]) {
      if (!witness) continue;
      const item = el('div');
      const leaders = witness.leaders.map(row => `${row.invoice_id} (record ${row.row})`).join(', ');
      const description = witness.status === 'no_positive' ? 'No positive variance remains.' : witness.status === 'tie' ? `Tied first · ${leaders}` : `First · ${leaders}`;
      item.append(el('small', '', label), el('strong', '', money(witness.price)), el('p', '', description));
      if (witness.leaders.length) item.append(el('small', '', `Leading variance ${money(witness.leaders[0].variance)}`));
      grid.append(item);
    }
    section.append(grid, button(`Try ${money(transition.at.price)} in an alternative`, () => {
      if (state.busy) return;
      $('wb-change-target').value = analysis.target;
      renderChangeOriginal();
      $('wb-change-value').value = transition.at.price;
      setExplorePane('alternatives');
      focusPoint($('wb-change-value'));
      announce('Boundary price prepared. Add it to your draft to execute an alternative.');
    }, 'wb-button'));
    node.append(section);
  }
  const interval = analysis.strict_price_interval;
  node.append(el('p', 'wb-help', `${name} remains uniquely first from ${money(interval.low)} through ${money(interval.high)}, inclusive on the cent grid. The packet verifier reconstructs these boundaries and the displayed results.`));
}
function renderTornado() {
  if (!state.active) return; const analysis = state.active.intelligence; const points = analysis.sensitivity || []; const container = $('wb-tornado'); container.replaceChildren(); $('wb-sensitivity-body').replaceChildren();
  if (!points.length) { const empty = el('div', 'wb-plot-empty'); empty.append(el('strong', '', 'Start with an assumption you can check.'), el('p', '', 'Select an invoice or shared contract, then declare a low and high value. The server calculates its effect on the whole case.')); container.append(empty); return; }
  const totals = [analysis.baseline_variance, ...points.flatMap(point => [point.at_low, point.at_high])].map(Number);
  const minimum = Math.min(...totals);
  const span = Math.max(...totals) - minimum || 1;
  const position = value => 5 + (Number(value) - minimum) / span * 90;
  const plot = el('div', 'wb-mobile-sensitivity');
  plot.setAttribute('role', 'group');
  plot.setAttribute('aria-label', 'Sensitivity by assumption');
  for (const point of points) {
    const target = targetById(point.target);
    const loX = position(point.at_low);
    const hiX = position(point.at_high);
    const select = () => editTarget(point.target);
    const control = button('', select, 'wb-mobile-target');
    control.setAttribute('aria-pressed', String(point.target === state.selectedTarget));
    control.setAttribute('aria-controls', 'wb-range-target');
    const track = el('span', 'wb-mobile-track'); const bar = el('span', 'wb-mobile-bar');
    if (loX > hiX) bar.classList.add('low-at-right');
    bar.style.left = `${Math.min(loX, hiX)}%`;
    bar.style.width = `max(2px, ${Math.abs(hiX - loX)}%)`;
    const original = el('span', 'wb-mobile-original'); original.style.left = `${position(analysis.baseline_variance)}%`;
    track.append(bar, original); track.setAttribute('aria-hidden', 'true');
    const values = el('span', 'wb-mobile-values'); values.append(el('span', '', `Low input → ${money(point.at_low)}`), el('span', '', `High input → ${money(point.at_high)}`));
    control.append(el('strong', '', point.label), track, values, el('small', '', `${point.rows.length} ${point.rows.length === 1 ? 'row' : 'rows'} · span ${money(point.outcome_span)}`));
    plot.append(control);
    const tr = el('tr');
    const name = el('th');
    name.scope = 'row';
    name.append(button(point.label, select, 'wb-row-link'));
    tr.append(name, el('td', '', `${valueLabel(target.field, point.low_value)} → ${money(point.at_low)}`), el('td', '', `${valueLabel(target.field, point.high_value)} → ${money(point.at_high)}`), el('td', 'wb-num', money(point.outcome_span)));
    $('wb-sensitivity-body').append(tr);
  }
  container.append(plot, el('p', 'wb-help', `● Low input  ○ High input  ··· Original case: ${money(analysis.baseline_variance)}`));
}
function renderNextFacts() {
  const analysis = state.active.intelligence; $('wb-next-facts').replaceChildren();
  for (const item of analysis.review_queue || []) { const li = el('li'); const detail = el('div'); detail.append(button(item.label, () => editTarget(item.target)), el('p', '', `Guaranteed width reduction ${money(item.guaranteed_width_reduction)} · up to ${money(item.possible_width_reduction)} · ${item.rows.length} rows`)); li.append(detail); $('wb-next-facts').append(li); }
  if (!analysis.review_queue?.length) $('wb-next-facts').append(el('p', 'wb-empty-small', 'Declare ranges to rank which input would remove the most uncertainty. No expected financial benefit is inferred.'));
  const leader = analysis.leader; const row = rowById(leader.candidate_row); const node = $('wb-leader'); node.replaceChildren(badge(leader.certified ? 'Strict leader throughout ranges' : 'Strict leader not certified', leader.certified ? 'blue' : ''), el('h3', '', row?.invoice_id || leader.invoice_id || `Row ${leader.candidate_row}`), el('p', '', leader.reason));
  if (leader.minimum_margin != null) node.append(el('p', 'wb-help', `Minimum pairwise margin ${signedMoney(leader.minimum_margin)}. Closest challenger: ${rowById(leader.challenger_row)?.invoice_id || `row ${leader.challenger_row}`}.`));
  $('wb-break-even').replaceChildren();
  for (const item of analysis.break_even) { const row = el('div', 'wb-break-even-row'); const detail = el('div'); detail.append(el('strong', '', money(item.zero_variance_price)), el('span', '', ` · ${item.rows.length} rows`)); row.append(button(item.label, () => chooseTarget(item.target)), detail); $('wb-break-even').append(row); }
  $('wb-break-even').append(el('p', 'wb-help', 'Supplied contract price that removes positive variance on every bound row, with all other inputs fixed. This is a threshold, not a proposed contract correction.'));
}
async function mutateCase(path, payload, description) {
  error(); notice(); setBusy(true, description);
  const draftRange = { target: state.selectedTarget, low: $('wb-bound-low').value, high: $('wb-bound-high').value };
  try {
    const result = await post(endpoint(path), { revision: state.active.revision, ...payload });
    if (!result.case && result.operation?.status === 'pending') { notice('The original alternative is still running. Check the pending result before starting another run.'); return false; }
    if (result.failed_run) {
      if (path === '/variants') finishOperation();
      const failed = result.failed_run; error(failed.error || 'The alternative did not complete. The baseline and your draft are preserved.');
      const inspector = $('wb-alternative-inspector'); inspector.hidden = false; inspector.replaceChildren(badge('Alternative failed · no comparison', 'failed'), el('h3', '', 'The proposed run was not accepted.'), el('p', 'wb-help', `Run ${failed.id}. The original case is unchanged; your draft is retained.`));
      for (const event of failed.events || []) { const item = el('div', 'wb-event'); item.append(el('strong', '', `${event.stage} · ${event.status}`), el('span', '', event.detail)); inspector.append(item); }
      if (failed.verification?.checks) inspector.append(checksList(failed.verification.checks));
      inspector.append(button('Inspect failed run in Single CSV review', () => { showLegacy(); window.dispatchEvent(new CustomEvent('prooflane:open-run', { detail: { id: failed.id } })); }));
      await refreshCases(); return false;
    }
    await acceptCase(result.case); if (path === '/variants') finishOperation(); await refreshCases(); return true;
  }
  catch (failure) {
    if (path === '/variants' && failure.status && failure.status !== 409) finishOperation();
    if (failure.status === 409) {
      try { const current = await api(endpoint()); await acceptCase(current.case); if (targetById(draftRange.target)) { chooseTarget(draftRange.target); $('wb-bound-low').value = draftRange.low; $('wb-bound-high').value = draftRange.high; } notice('This case changed in another request. The latest saved revision is loaded; your draft is retained. Review it before submitting again.'); }
      catch (refreshFailure) { error(`The case changed and could not be refreshed: ${refreshFailure.message}`); }
    } else error(`${failure.message}${path === '/variants' && pendingOperation ? ' Check the pending result before starting another run.' : ''}`);
    return false;
  } finally { setBusy(false); }
}
async function saveBound() {
  if (state.busy || !state.active) return; const target = targetById(state.selectedTarget); const low = $('wb-bound-low').value.trim(), high = $('wb-bound-high').value.trim(); const invalid = validateRange(target, low, high);
  for (const id of ['wb-bound-low', 'wb-bound-high']) $(id).setAttribute('aria-invalid', String(!!invalid));
  if (invalid) { error(invalid); focusPoint($('wb-bound-low')); return; }
  const others = state.active.bounds.filter(bound => bound.target !== target.id);
  if (others.length >= state.active.limits.max_bounds) { error(`This case supports at most ${state.active.limits.max_bounds} declared ranges. Remove a range first.`); return; }
  if (await mutateCase('/bounds', { bounds: [...others, { target: target.id, low, high }] }, 'Calculating exact joint bounds and one-at-a-time sensitivity using trusted rules…')) {
    const { low: resultLow, high: resultHigh } = state.active.intelligence;
    notice(`Range saved. The case spans ${money(resultLow)} to ${money(resultHigh)}.`);
  }
  focusPoint($('wb-save-bound'));
}
function renderChangeOriginal() {
  const target = targetById($('wb-change-target').value); text('wb-change-original', target ? `Original ${fieldLabel[target.field].toLowerCase()}: ${valueLabel(target.field, target.before)} · affects ${target.rows.map(n => rowById(n)?.invoice_id || `row ${n}`).join(', ')}` : '');
  $('wb-change-value').inputMode = target?.field === 'quantity' ? 'numeric' : 'decimal';
}
function renderDraftChanges() {
  $('wb-draft-changes').replaceChildren(); text('wb-change-capacity', `${state.changes.length} of ${state.active?.limits?.max_changes || 12} changes`);
  for (const change of state.changes) {
    const target = targetById(change.target);
    if (!target) continue;
    const node = el('div', 'wb-draft-change');
    const detail = el('div', '', target.label);
    detail.append(el('small', '', `${target.rows.length} affected ${target.rows.length === 1 ? 'row' : 'rows'} · original ${valueLabel(target.field, target.before)}`));
    const remove = button('×', () => {
      if (state.busy) return;
      state.changes = state.changes.filter(item => item.target !== change.target);
      renderDraftChanges();
      focusPoint($('wb-change-target'));
      announce(`Removed ${target.label} from the draft.`);
    }, '');
    remove.setAttribute('aria-label', `Remove ${target.label} from draft`);
    node.append(detail, el('strong', '', `→ ${valueLabel(target.field, change.value)}`), remove);
    $('wb-draft-changes').append(node);
  }
  syncActions();
}
function addChange() {
  if (state.busy) return; const target = targetById($('wb-change-target').value); const value = $('wb-change-value').value.trim(); const invalid = validateChange(target, value, state.changes, state.active?.limits?.max_changes || 12);
  if (invalid) { error(invalid); return; } error(); state.changes.push({ target: target.id, value }); $('wb-change-value').value = ''; renderDraftChanges(); announce(`Added ${target.label}. ${target.rows.length} affected rows.`);
}
function renderAlternatives() {
  const current = state.active; const max = current.limits.max_variants; const full = current.variants.length >= max;
  text('wb-alternative-capacity', `${current.variants.length} of ${max} alternatives`); $('wb-alternative-form').hidden = full; $('wb-alternatives-full').hidden = !full;
  $('wb-alternative-token-wrap').hidden = current.baseline.mode !== 'vultr';
  text('wb-alternative-mode', `Same original mode: ${modeLabel[current.baseline.mode]}. ${modeDescription(current.baseline.mode)}${canMode(current.baseline.mode) ? '' : ' This mode is currently unavailable; no fallback.'}`);
  $('wb-alternatives-body').replaceChildren(); $('wb-alternatives-mobile').replaceChildren(); $('wb-alternative-inspector').hidden = true;
  const append = (run, name, changes, delta, variant) => {
    if (!completed(run)) return;
    const tr = el('tr'); const label = el('td'); label.append(el('strong', '', name), el('small', '', changes.length ? changes.map(change => { const target = targetById(change.target); return `${target.label} → ${valueLabel(target.field, change.value)}`; }).join(' · ') : 'Frozen source inputs · original baseline'));
    const status = el('td'); status.append(badge(completionLabel(run), run.mode === 'reference' ? 'blue' : 'good'));
    const action = el('td');
    const inspect = button('Inspect', () => inspectAlternative(variant, inspect), 'wb-row-link');
    inspect.setAttribute('aria-label', `Inspect ${name}`);
    inspect.setAttribute('aria-controls', 'wb-alternative-inspector');
    action.append(inspect);
    tr.append(label, el('td', 'wb-num', money(run.summary.total_variance)), el('td', 'wb-num', variant ? signedMoney(delta.total_variance) : '—'), el('td', 'wb-num', count(run.summary.flagged_count)), status, action); $('wb-alternatives-body').append(tr);
    const compact = el('li', 'wb-alternative-summary');
    compact.append(el('h4', '', name), el('p', 'wb-help', changes.length ? changes.map(change => `${targetById(change.target).label} → ${valueLabel(targetById(change.target).field, change.value)}`).join(' · ') : 'Original baseline · frozen source inputs'), facts([['Positive variance', money(run.summary.total_variance)], ['Change from original', variant ? signedMoney(delta.total_variance) : 'Original'], ['Flagged invoices', count(run.summary.flagged_count)], ['Execution', completionLabel(run)]]));
    const inspectCompact = button(`Inspect ${name}`, () => inspectAlternative(variant, inspectCompact), 'wb-button'); compact.append(inspectCompact); $('wb-alternatives-mobile').append(compact);
  };
  append(current.baseline, 'Supplied baseline', [], null, null); for (const variant of current.variants) append(variant.run, variant.name, variant.changes, variant.delta, variant);
  renderDraftChanges();
}
function inspectAlternative(variant, opener) {
  const node = $('wb-alternative-inspector'); const run = variant?.run || state.active.baseline; node.hidden = false; node.replaceChildren(el('h3', '', variant?.name || 'Supplied baseline'), el('p', 'wb-help', `${completionLabel(run)} · ${modeDescription(run.mode)} · RUN ${run.id}`));
  if (variant) {
    const list = el('ul'); for (const change of variant.changes) { const target = targetById(change.target); list.append(el('li', '', `${target.label}: ${valueLabel(target.field, target.before)} → ${valueLabel(target.field, change.value)}; normalized rows ${target.rows.join(', ')}`)); } node.append(list, el('p', '', `${variant.changed_rows.length} distinct changed rows. Total billed ${money(run.summary.total_billed)} (${signedMoney(variant.delta.total_billed)}). All changes were recalculated together.`));
  }
  const actions = el('div', 'wb-button-row');
  actions.append(link('Download this receipt ↓', `/api/runs/${idURL(run.id)}/receipt`, 'wb-text-button', true), button('Close details', () => {
    node.hidden = true;
    focusPoint(opener);
  }));
  if (variant && state.active.variants.length < state.active.limits.max_variants) actions.append(button('Duplicate as draft', () => { if (state.busy) return; state.changes = variant.changes.map(item => ({ ...item })); $('wb-alternative-name').value = `${variant.name} copy`.slice(0, 80); renderDraftChanges(); $('wb-alternative-name').focus(); notice('Copied assumptions into an unexecuted draft. Change its name or values before running.'); })); node.append(actions);
  focusPoint(node.querySelector('h3'));
}
async function runAlternative(event) {
  event.preventDefault(); if (state.busy || pendingOperation || !state.changes.length) return; const name = $('wb-alternative-name').value.trim(); if (!name) { error('Give the alternative a name.'); $('wb-alternative-name').focus(); return; }
  const payload = { name, changes: state.changes.map(item => ({ ...item })), request_id: beginOperation('alternative') }; if (state.active.baseline.mode === 'vultr') payload.operator_token = $('wb-alternative-token').value;
  const ok = await mutateCase('/variants', payload, `Running “${name}” from the original baseline. ${modeDescription(state.active.baseline.mode)}`); $('wb-alternative-token').value = '';
  if (ok) { state.changes = []; $('wb-alternative-name').value = ''; renderDraftChanges(); notice(`“${name}” saved. ${completionLabel(state.active.variants.at(-1).run)}; the original baseline is unchanged.`); }
}

function renderEvidence() {
  $('wb-evidence-case').hidden = !state.active;
  if (!state.active) return;
  const old = $('wb-evidence-row').value; $('wb-evidence-row').replaceChildren();
  for (const row of state.rows) { const option = el('option', '', `${row.invoice_id} · ${row.vendor} · normalized row ${row.row}`); option.value = row.row; $('wb-evidence-row').append(option); }
  for (const record of state.active.source.records.filter(item => item.status === 'excluded')) { const option = el('option', '', `${record.invoice_id} · excluded · source row ${record.invoice_row}`); option.value = `excluded:${record.invoice_row}`; $('wb-evidence-row').append(option); }
  if (state.excludedSourceRow) $('wb-evidence-row').value = `excluded:${state.excludedSourceRow}`;
  else if (rowById(state.selectedRow || old)) $('wb-evidence-row').value = String(state.selectedRow || old);
  const c = state.active.source.counts; text('wb-packet-contents', `Baseline + ${state.active.variants.length} completed alternatives · ${state.active.source.kind === 'contracts' ? '2 source files' : 'embedded source CSV'} · ${state.active.baseline.summary.row_count} included rows · ${c.excluded || 0} explicit exclusions · ${state.active.bounds.length} declared ranges.`);
  $('wb-packet-secondary').href = endpoint('/packet'); $('wb-packet-secondary').download = `prooflane-case-${state.active.id}.json`;
  $('wb-handoff').href = endpoint('/handoff.csv'); $('wb-handoff').download = `prooflane-review-${state.active.id}.csv`;
  $('wb-review-brief').href = endpoint('/brief.md'); $('wb-review-brief').download = `prooflane-brief-${state.active.id}.md`;
  renderDependency(); renderExecution();
}
function renderDependency() {
  if (!state.active) return;
  const selected = $('wb-evidence-row').value;
  if (selected.startsWith('excluded:')) {
    const record = state.active.source.records.find(item => item.status === 'excluded' && item.invoice_row === Number(selected.slice(9)));
    if (!record) return;
    state.excludedSourceRow = record.invoice_row; state.selectedRow = null; state.matchRow = record.invoice_row;
    $('wb-dependency-path').replaceChildren(el('p', 'folio-exclusion-trace', `${record.invoice_id}, source row ${record.invoice_row} → explicit exclusion → no baseline calculation`));
    $('wb-evidence-inspector').replaceChildren(el('p', 'wb-kicker', 'EXCLUSION RECORD'), el('h3', '', `${record.invoice_id} is outside the calculated scope`), el('p', '', 'This source is retained in the case packet. It contributes no amount to the baseline or alternatives.'), facts([['Original source row', record.invoice_row], ['Vendor', record.vendor], ['Exclusion reason', record.reason], ['Contract decision', 'No contract price applied'], ['Calculated amount', 'Not calculated; excluded']]));
    return;
  }
  const row = rowById(selected); if (!row) return; state.excludedSourceRow = null; state.selectedRow = row.row; const binding = bindingFor(row.row); state.matchRow = binding?.invoice_row ?? row.row;
  const nodes = [['invoice', '01. Invoice', row.invoice_id, `Invoice row ${binding?.invoice_row ?? row.row}`], ['contract', '02. Contract price', binding?.contract_id || 'Embedded price', binding ? `Contract row ${binding.contract_row}` : 'No separate source'], ['input', '03. Calculation input', `Input record ${row.row}`, `${row.quantity} × supplied prices`], ['calculation', '04. Baseline', money(rowVariance(row.row)), completionLabel(state.active.baseline)], ['alternatives', '05. Alternatives', `${state.active.variants.length} alternatives`, 'Each from this baseline'], ['packet', '06. Receipt', 'Receipt → packet', 'Hash-linked evidence']];
  const path = $('wb-dependency-path');
  path.replaceChildren();
  const stages = [['Supplied sources', nodes.slice(0, 2)], ['Reproducible calculation', nodes.slice(2, 4)], ['Portable evidence', nodes.slice(4)]];
  for (const [stageName, stageNodes] of stages) {
    const stage = el('section', 'wb-proof-stage'); stage.append(el('h3', '', stageName));
    const controls = el('div', 'wb-proof-stage-controls');
    for (const [id, kicker, title, detail] of stageNodes) {
    const node = button('', () => {
      state.dependency = id;
      for (const control of path.querySelectorAll('button')) control.setAttribute('aria-pressed', String(control === node));
      renderDependencyInspector(row, binding);
      focusPoint($('wb-evidence-inspector').querySelector('h3'));
    }, 'wb-dependency-node');
    node.setAttribute('aria-pressed', String(state.dependency === id));
    node.setAttribute('aria-controls', 'wb-evidence-inspector');
    node.append(el('small', '', kicker), el('strong', '', title), el('span', '', detail));
    controls.append(node);
    }
    stage.append(controls); path.append(stage);
  }
  renderDependencyInspector(row, binding);
}
function renderDependencyInspector(row, binding) {
  const node = $('wb-evidence-inspector'); const source = sourceFor(row.row); const run = state.active.baseline; const selected = state.dependency; node.replaceChildren(el('p', 'wb-kicker', 'DEPENDENCY INSPECTOR'));
  if (selected === 'invoice') {
    node.append(el('h3', '', `Original invoice ${row.invoice_id}`), el('p', '', 'The supplied source row, before assumptions or exclusions are applied.'), facts([['Invoice source row', binding?.invoice_row ?? row.row], ['Vendor', row.vendor], ['Item key', source?.item_id || 'Not supplied'], ['Invoice date', source?.invoice_date || 'Not supplied'], ['Quantity', source?.quantity || row.quantity], ['Billed unit price', money(source?.unit_price || row.unit_price)], ['Notes', source?.notes || 'None supplied']]));
  } else if (selected === 'contract') {
    const contract = chosenContract(source);
    node.append(el('h3', '', binding?.contract_id || 'Price embedded in invoice CSV'), el('p', '', binding ? 'Exact vendor/item/date matching links this supplied contract record to the invoice. A manual choice is preserved as a decision.' : 'No separate contract source was checked for this case. The price is supplied in the original invoice CSV.'), facts([['Decision', decisionLabel(source?.status || 'embedded')], ['Contract source row', binding?.contract_row || 'Not applicable'], ['Original price', money(row.contract_price)], ...(contract ? [['Effective from', contract.valid_from], ['Effective to', contract.valid_to], ['Eligible candidates', source.candidates.map(c => c.contract_id).join(', ')]] : []), ['Invoices sharing price', state.active.targets.find(t => t.field === 'contract_price' && t.rows.includes(row.row))?.rows.map(n => rowById(n)?.invoice_id).join(', ')]]));
  } else if (selected === 'input') {
    node.append(el('h3', '', `Normalized input record ${row.row}`), el('p', '', 'The reconciled six-column record is the input bound to the baseline receipt. Only explicitly included rows enter its calculation.'), facts([['Invoice source row', binding?.invoice_row ?? row.row], ['Normalized row', row.row], ['Quantity', row.quantity], ['Billed unit price', money(row.unit_price)], ['Contract price', money(row.contract_price)], ['Invoice ID', row.invoice_id], ['Vendor', row.vendor]]));
  } else if (selected === 'calculation') {
    node.append(el('h3', '', `${completionLabel(run)} for ${row.invoice_id}`), el('p', '', modeDescription(run.mode)), facts([['Rule', 'max(billed unit price − contract price, 0) × quantity'], ['This row', money(rowVariance(row.row))], ['Whole included case', money(run.summary.total_variance)], ['Baseline mode', modeLabel[run.mode]], ['Run ID', run.id]]), link('Download baseline receipt ↓', `/api/runs/${idURL(run.id)}/receipt`, 'wb-text-button', true));
  } else if (selected === 'alternatives') {
    node.append(el('h3', '', 'Explicit changes from one original'), el('p', '', 'Each alternative uses this baseline and its execution mode. The proposed values are assumptions; source evidence stays unchanged.'));
    if (!state.active.variants.length) node.append(el('p', 'wb-help', 'No completed alternatives yet.'));
    for (const variant of state.active.variants) { const details = el('details'); details.append(el('summary', '', `${variant.name} · ${money(variant.run.summary.total_variance)} (${signedMoney(variant.delta.total_variance)})`)); const list = el('ul'); for (const change of variant.changes) { const target = targetById(change.target); list.append(el('li', '', `${target.label}: ${valueLabel(target.field, target.before)} → ${valueLabel(target.field, change.value)} · rows ${target.rows.join(', ')}`)); } details.append(list, link('Alternative receipt ↓', `/api/runs/${idURL(variant.run.id)}/receipt`, 'wb-text-button', true)); node.append(details); }
  } else {
    node.append(el('h3', '', 'Baseline receipt integrity'), el('p', '', 'The receipt links input, code, output and provenance fields. The case packet also carries source decisions, alternative receipts, declared ranges and reconstructed results.'), el('code', 'wb-full-hash', run.receipt_hash), button('Copy full baseline receipt hash', () => copy(run.receipt_hash, 'Baseline receipt hash copied.')), el('p', 'wb-help', 'The packet verifier reconstructs every layer. Hashes are integrity evidence, not a signature, runtime attestation, or proof of source truth.'), link('Download baseline receipt ↓', `/api/runs/${idURL(run.id)}/receipt`, 'wb-text-button', true));
  }
}
function checksList(checks, stringChecksPassed = false) {
  const list = el('ul', 'wb-checks');
  for (const entry of checks || []) { const item = typeof entry === 'string' ? { name: entry, passed: stringChecksPassed } : entry; const li = el('li', item.passed === true ? '' : 'failed'); const detail = el('div'); detail.append(el('strong', '', `${item.name || item.check || 'Check'} · ${item.passed === true ? 'passed' : 'not passed'}`)); if (item.detail) detail.append(el('small', '', item.detail)); li.append(el('span', 'wb-check-symbol', item.passed === true ? '✓' : '!'), detail); list.append(li); }
  return list;
}
function renderExecution() {
  const run = state.active.baseline; const node = $('wb-execution-record'); node.replaceChildren(el('p', 'wb-help', `${completionLabel(run)}. ${modeDescription(run.mode)}`));
  if (run.mode === 'vultr') {
    node.append(facts([['Requested model', run.requested_model], ['Returned model', run.model]]));
    for (const attempt of run.attempts || []) {
      node.append(facts([['Attempt', attempt.index], ['Vultr request ID', attempt.request_id], ['Tokens reported', attempt.usage?.total_tokens]]));
    }
    if (run.explanation_trace) {
      const trace = run.explanation_trace;
      const guided = trace.status === 'checked';
      node.append(el('h3', '', guided ? 'Review guidance selected by Vultr' : 'Checked application summary'), el('p', 'wb-help', run.explanation));
      if (guided) node.append(facts([['Explanation model', trace.model], ['Vultr request ID', trace.request_id], ['Tokens reported', trace.usage?.total_tokens]]));
    }
  }
  for (const event of run.events || []) { const row = el('div', 'wb-event'); row.append(el('strong', '', `${event.stage} · ${event.status}`), el('span', '', event.detail)); node.append(row); }
  const exec = run.execution || {}; const pairs = [['Runtime', exec.runtime || 'Not reported'], ['Elapsed', exec.elapsed_ms == null ? 'Not reported' : `${exec.elapsed_ms} ms`], ['Container removed', exec.cleanup == null ? 'Not reported' : String(exec.cleanup)], ['Container', exec.container_id || 'Not reported']];
  if (exec.limits) pairs.push(['Container limits', JSON.stringify(exec.limits)]); node.append(facts(pairs));
  const checks = el('details'); checks.append(el('summary', '', run.mode === 'reference' ? 'Reference calculation checks' : 'Independent output verification'), checksList(run.verification?.checks)); node.append(checks);
  const code = el('details'); code.append(el('summary', '', run.mode === 'reference' ? 'Trusted reference calculation source' : 'Executed Python source')); const pre = el('pre'); pre.append(el('code', '', run.code || 'No code returned.')); code.append(pre); node.append(code);
  const hash = el('details'); hash.append(el('summary', '', 'Full receipt identity'), el('code', 'wb-full-hash', run.receipt_hash), button('Copy full hash', () => copy(run.receipt_hash, 'Baseline receipt hash copied.')), link('Download baseline receipt ↓', `/api/runs/${idURL(run.id)}/receipt`, 'wb-text-button', true)); node.append(hash);
}
async function runContainment() {
  const control = $('wb-containment-run');
  if (control.getAttribute('aria-disabled') === 'true') return;
  const result = $('wb-containment-result');
  control.setAttribute('aria-disabled', 'true');
  result.replaceChildren(el('p', 'wb-help', 'Running checks in a new container…'));
  announce('Running sandbox containment checks.');
  try {
    const probe = await post('/api/containment', {});
    const passed = probe.passed === true;
    const title = passed ? 'Containment checks passed' : 'Containment checks failed';
    result.replaceChildren(badge(title, passed ? 'good' : 'failed'), checksList(probe.checks));
    announce(title);
  } catch (failure) {
    result.replaceChildren(el('p', 'wb-help', failure.message));
    announce(`Containment check could not complete. ${failure.message}`);
  } finally {
    control.removeAttribute('aria-disabled');
  }
}
async function verifyPacket(event) {
  event.preventDefault(); if (state.busy || !state.packetText.trim()) return;
  const packetRequest = state.packetRequest;
  error(); $('wb-verify-result').hidden = true;
  try { if (bytes(state.packetText) > MAX_PACKET) throw new Error('A case packet must be at most 8 MiB.'); JSON.parse(state.packetText); } catch (failure) { error(failure instanceof SyntaxError ? 'This file is not valid JSON. Choose an unmodified case packet.' : failure.message); return; }
  setBusy(true, 'Verifying the packet by reconstructing source joins, receipts, changes and range results. No code is executed…');
  try {
    // Preserve the exact uploaded text: parsing and reserializing here would hide
    // duplicate JSON keys from the server's strict evidence parser.
    const result = await api('/api/verify-packet', { method: 'POST', body: state.packetText });
    if (packetRequest !== state.packetRequest) return;
    const node = $('wb-verify-result'); node.replaceChildren(badge(result.passed ? 'Packet checks passed' : 'Packet rejected', result.passed ? 'good' : 'failed'), el('h3', '', result.passed ? 'Arithmetic and content integrity checked.' : 'This packet did not pass verification.'));
    if (result.error) node.append(el('p', '', result.error));
    if (result.scope) node.append(el('p', '', typeof result.scope === 'string' ? result.scope : JSON.stringify(result.scope)));
    if (Array.isArray(result.checks)) node.append(checksList(result.checks, result.passed === true));
    else if (result.checks) { const details = el('pre'); details.textContent = JSON.stringify(result.checks, null, 2); node.append(details); }
    node.hidden = false; announce(result.passed ? 'Packet verification passed. See the verification scope.' : 'Packet rejected. See the failed check.');
  } catch (failure) { error(failure.message); }
  finally { setBusy(false); }
}

function renderHealth(health) {
  state.health = health; text('wb-runtime', health ? health.docker?.available ? 'Docker execution available' : 'Reference mode available' : 'Service readiness unknown');
  $('wb-containment-run').disabled = !health?.docker?.available;
  $('wb-containment-unavailable').hidden = !!health?.docker?.available;
  for (const mode of ['reference', 'sandbox', 'vultr']) { const option = $('wb-execution-mode').querySelector(`option[value="${mode}"]`); option.disabled = !canMode(mode); option.textContent = `${modeLabel[mode]}${canMode(mode) ? '' : ' · unavailable'}`; }
  updateMode(); syncActions();
}
function updateMode() { const mode = $('wb-execution-mode').value; text('wb-mode-help', modeDescription(mode)); $('wb-token-wrap').hidden = mode !== 'vultr'; if (mode !== 'vultr') $('wb-operator-token').value = ''; syncActions(); }
function showLegacy(environment = false) {
  if (state.busy) return;
  $('case-workbench').hidden = true;
  $('legacy-workspace').hidden = false;
  document.querySelector('.skip-link').href = '#workspace';
  focusPoint(environment ? $('trust-boundary') : $('wb-return'));
}
function returnWorkbench() {
  $('legacy-workspace').hidden = true;
  $('case-workbench').hidden = false;
  document.querySelector('.skip-link').href = '#wb-main';
  focusPoint($(`wb-${state.view}-heading`));
}

let archiveOpener = null;
let archiveDestination = null;
function openArchive() {
  if (state.busy) return;
  archiveOpener = document.activeElement; $('folio-archive-error').hidden = true;
  $('folio-archive').showModal(); $('wb-rail-toggle').setAttribute('aria-expanded', 'true'); $('folio-close-archive').focus();
}
function closeArchive(destination = null) {
  if (!$('folio-archive').open) return;
  archiveDestination = destination;
  $('folio-archive').close();
}
function setExplorePane(pane, focus = false) {
  if (!['ranges', 'alternatives'].includes(pane)) return;
  state.explorePane = pane;
  $('folio-range-pane').hidden = pane !== 'ranges'; $('folio-alternative-pane').hidden = pane !== 'alternatives';
  document.querySelectorAll('[data-explore-pane]').forEach(node => { const active = node.dataset.explorePane === pane; node.setAttribute('aria-selected', String(active)); node.tabIndex = active ? 0 : -1; if (active && focus) node.focus(); });
  rememberLocation();
}
for (const node of document.querySelectorAll('[data-explore-pane]')) {
  node.addEventListener('click', () => { if (!state.busy) setExplorePane(node.dataset.explorePane); });
  node.addEventListener('keydown', event => { if (state.busy || !['ArrowLeft', 'ArrowRight', 'Home', 'End'].includes(event.key)) return; event.preventDefault(); const next = event.key === 'Home' ? 'ranges' : event.key === 'End' ? 'alternatives' : state.explorePane === 'ranges' ? 'alternatives' : 'ranges'; setExplorePane(next, true); });
}

document.querySelectorAll('[data-wb-view]').forEach(node => node.addEventListener('click', () => selectView(node.dataset.wbView, true)));
$('wb-new').addEventListener('click', () => { closeArchive(); resetDraft(); });
$('wb-home').addEventListener('click', event => { event.preventDefault(); if (!state.busy) selectView(state.active ? 'overview' : 'sources', true); });
$('wb-refresh').addEventListener('click', refreshCases);
$('wb-rail-toggle').addEventListener('click', openArchive);
$('folio-close-archive').addEventListener('click', () => closeArchive());
$('folio-archive').addEventListener('close', () => {
  $('wb-rail-toggle').setAttribute('aria-expanded', 'false');
  if (!$('case-workbench').hidden) focusPoint(archiveDestination || archiveOpener);
  if (archiveDestination && state.active) {
    const baseline = state.active.baseline;
    announce(`Saved case opened. ${baseline.summary.row_count} included invoices. ${completionLabel(baseline)}.`);
  }
  archiveDestination = null;
});
$('wb-legacy').addEventListener('click', () => { closeArchive(); showLegacy(); }); $('wb-environment').addEventListener('click', () => showLegacy(true)); $('wb-return').addEventListener('click', returnWorkbench);
$('wb-containment-run').addEventListener('click', runContainment);
$('wb-invoice-file').addEventListener('change', event => loadSource(event.target.files[0], 'invoices'));
$('wb-contract-file').addEventListener('change', event => loadSource(event.target.files[0], 'contracts'));
$('wb-invoices').addEventListener('input', () => { invalidateSourceReads('invoices'); invalidateSources(); }); $('wb-contracts').addEventListener('input', () => { invalidateSourceReads('contracts'); invalidateSources(); });
$('wb-match').addEventListener('click', () => matchSources({ chooseFirst: true })); $('wb-create').addEventListener('click', createCase);
$('wb-match-search').addEventListener('input', renderMatchTable); $('wb-match-filter').addEventListener('change', renderMatchTable);
$('wb-execution-mode').addEventListener('change', updateMode); $('wb-row-search').addEventListener('input', renderRows); $('wb-row-filter').addEventListener('change', renderRows);
$('wb-range-target').addEventListener('change', () => chooseTarget($('wb-range-target').value)); $('wb-save-bound').addEventListener('click', saveBound);
$('wb-remove-bound').addEventListener('click', () => { if (!state.busy) mutateCase('/bounds', { bounds: state.active.bounds.filter(bound => bound.target !== state.selectedTarget) }, 'Removing this declared range and recalculating exact results…'); });
$('wb-reset-bounds').addEventListener('click', () => { if (!state.busy) mutateCase('/bounds', { bounds: [] }, 'Restoring all fixed inputs and recalculating exact results…'); });
$('wb-change-target').addEventListener('change', () => { $('wb-change-value').value = ''; renderChangeOriginal(); }); $('wb-add-change').addEventListener('click', addChange); $('wb-alternative-form').addEventListener('submit', runAlternative);
$('wb-evidence-row').addEventListener('change', renderDependency); $('wb-verify-form').addEventListener('submit', verifyPacket);
$('wb-packet-json').addEventListener('input', () => { state.packetText = $('wb-packet-json').value; state.packetRequest++; $('wb-verify-result').hidden = true; text('wb-packet-file-label', 'Pasted packet · not verified'); syncActions(); });
$('wb-packet-file').addEventListener('change', async event => { const file = event.target.files[0]; if (!file) return; const request = ++state.packetRequest; state.packetText = ''; $('wb-packet-json').value = ''; $('wb-verify-result').hidden = true; text('wb-packet-file-label', `Reading ${file.name}…`); syncActions(); error(); try { if (file.size > MAX_PACKET) throw new Error('A case packet must be at most 8 MiB.'); const content = await file.text(); if (request !== state.packetRequest) return; state.packetText = content; $('wb-packet-json').value = content; text('wb-packet-file-label', `${file.name} · ${count(file.size)} bytes`); syncActions(); } catch (failure) { text('wb-packet-file-label', 'No packet loaded'); error(failure.message); } });
async function loadExample(reviewed = false) {
  if (state.busy) return; invalidateSourceReads(); error(); notice(); setBusy(true, 'Loading the fictional source files…');
  try { const sample = await api('/api/cases/sample'); $('wb-invoices').value = sample.invoices_csv; $('wb-contracts').value = sample.contracts_csv; $('wb-name').value = sample.name; state.match = null; state.matchRow = null; state.selections = {}; state.exclusions = {}; state.synthetic = true; $('wb-invoice-file').value = ''; $('wb-contract-file').value = ''; text('wb-invoice-file-label', 'Fictional sample invoices · source CSV'); text('wb-contract-file-label', 'Fictional sample contracts · source CSV'); text('wb-draft-label', 'Fictional sample · includes overlapping contracts and an unmatched invoice.'); }
  catch (failure) { error(failure.message); }
  finally { setBusy(false); }
  if (state.synthetic) {
    if (reviewed) {
      state.selections = { '5': 'C2R' };
      state.exclusions = { '7': 'No active contract in the fictional fixture.' };
    }
    await matchSources({ chooseFirst: true });
    if (reviewed && state.match?.ready) {
      $('wb-execution-mode').value = 'reference'; updateMode();
      await createCase();
      if (state.active) notice('Reviewed fictional example. C2R was explicitly selected for INV504; INV506 was excluded because no active contract was supplied. Inspect these source decisions. This is a fixed reference calculation, with no AI call.');
    }
  }
}
$('wb-sample').addEventListener('click', () => loadExample());
$('wb-reviewed-demo').addEventListener('click', () => { if (!pendingOperation) loadExample(true); });
$('wb-check-operation').addEventListener('click', recoverOperation);
$('wb-invoice-template').addEventListener('click', () => downloadStarter('invoices'));
$('wb-contract-template').addEventListener('click', () => downloadStarter('contracts'));
$('wb-fix-invoices').addEventListener('click', () => editSource('invoices'));
$('wb-fix-contracts').addEventListener('click', () => editSource('contracts'));
window.addEventListener('prooflane:health', event => renderHealth(event.detail));
window.addEventListener('prooflane:promote-run', async event => {
  if (state.busy) return; invalidateSourceReads(); returnWorkbench(); setBusy(true, 'Creating a case from the original single CSV review…'); error();
  try { const result = await post('/api/cases', { name: (event.detail.name || 'Embedded-price review').slice(0, 80), baseline_run_id: event.detail.id }); await acceptCase(result.case, { reset: true }); await refreshCases(); }
  catch (failure) { error(failure.message); }
  finally { setBusy(false); if (state.active) selectView('overview', true); }
});

selectView('sources'); renderSources(); renderEvidence(); renderRecovery(); syncActions();
setExplorePane('ranges');
// The older view establishes the same-origin cookie first, avoiding two initial sessions.
await (window.prooflaneSessionReady || new Promise(resolve => window.addEventListener('prooflane:session-ready', resolve, { once: true })));
renderHealth(window.prooflaneHealth || null); await refreshCases();
const previousLocation = readSession(session(), LOCATION_KEY, navigationState);
if (previousLocation) {
  if (await openCase(previousLocation.id)) {
    setExplorePane(previousLocation.pane); selectView(previousLocation.view);
    notice('Reopened your saved review. Only its ID and chapter were kept in this tab; source files and credentials were not stored in browser storage.');
  } else writeSession(session(), LOCATION_KEY, null, navigationState);
}
