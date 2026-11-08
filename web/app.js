'use strict';
import { money } from './format.js';
import { createScenarioWorkspace } from './scenario.js';

(() => {
  const $ = (id) => document.getElementById(id);
  const MAX_CSV_BYTES = 128 * 1024;
  const numberFormat = new Intl.NumberFormat('en-US');
  const DEFAULT_CONTEXT = 'Find invoice lines billed above their contract price. Show the variance and the source rows that support it.';
  const state = { health: null, csv: '', filename: 'pasted-invoices.csv', synthetic: false, busy: false, currentRun: null, loadingTimer: null, binding: null, stale: false, restoring: false };
  const modeCopy = {
    reference: {
      title: 'Reference calculation · trusted fixed rules',
      detail: 'Runs trusted arithmetic in the application. No model was called and no sandbox was used for this review.',
      note: 'A reproducible baseline. Runs trusted arithmetic in the application; does not call a model or demonstrate isolation.'
    },
    sandbox: {
      title: 'Sandbox recipe · fixed code',
      detail: 'This mode executes a fixed Python recipe in Docker. It is not AI-generated code. Inspect the execution and verification records below.',
      note: 'A fixed Python recipe runs in a disposable Docker container. No model calls. Docker must be available.'
    },
    vultr: {
      title: 'Vultr agent · model-generated code',
      detail: 'This mode uses Vultr Serverless Inference to write code for Docker execution. Check the actual events and independent verification below.',
      note: 'Vultr writes the Python; Docker executes it. An independent verifier checks the result. Requires enabled inference and an operator token.'
    }
  };

  function text(node, value) { node.textContent = value == null ? '' : String(value); }
  function element(tag, className, value) {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (value != null) text(node, value);
    return node;
  }
  function count(value) { return value != null && value !== '' && Number.isFinite(Number(value)) ? numberFormat.format(Number(value)) : '—'; }
  function mode() { return document.querySelector('input[name="mode"]:checked').value; }
  function announce(message) { text($('announcement'), message); }
  function setError(id, message) { text($(id), message || ''); $(id).hidden = !message; }
  function statusPill(node, label, type = 'neutral') {
    node.className = `status-pill ${type === 'success' ? '' : `${type}-pill`}`.trim();
    text(node, label);
  }
  function readable(value) { return String(value || '').replaceAll('_', ' ').replaceAll('-', ' '); }
  function safeRunId(id) { return encodeURIComponent(String(id)); }
  function scrollTo(node) { node.scrollIntoView({ behavior: window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth', block: 'start' }); }
  function modeAvailable(value) {
    return value === 'reference' || !!state.health?.docker?.available && (value !== 'vultr' || !!(state.health.inference?.configured && state.health.inference?.enabled));
  }
  function captureBinding() { state.binding = { csv: state.csv, question: $('question').value, mode: mode() }; }
  function updateDraftBinding() {
    if (state.restoring) return;
    text($('question-count'), `${$('question').value.length} of 600`);
    state.stale = !!state.currentRun && (!state.binding || state.binding.csv !== state.csv || state.binding.question !== $('question').value || state.binding.mode !== mode());
    $('stale-result').hidden = !state.stale;
    $('summary-binding-note').hidden = !state.stale;
    $('run-result').classList.toggle('previous-result', state.stale);
    $('wb-promote-run').disabled = state.busy || state.stale;
    text($('download-receipt'), state.stale ? 'Download previous receipt' : 'Download receipt');
    if (state.currentRun && !state.busy) {
      const verified = state.currentRun.status === 'verified' && state.currentRun.verification?.passed === true;
      statusPill($('run-status'), state.stale ? 'Previous result · inputs changed' : verified ? state.currentRun.mode === 'reference' ? 'Reference complete' : 'Result verified' : 'Run failed', state.stale ? 'warning' : verified ? 'success' : 'error');
    }
    scenario.syncAvailability();
  }

  async function restoreInputs(run) {
    const receipt = run.receipt_hash ? await api(`/api/runs/${safeRunId(run.id)}/receipt`) : null;
    state.restoring = true;
    try {
      if (receipt) setCsv(receipt.input_csv, run.filename, /synthetic/i.test(run.filename || ''));
      if (receipt && run.lineage) text($('dataset-label'), 'Hypothetical scenario · one changed assumption from the original review');
      $('question').value = run.question || '';
      const input = document.querySelector(`input[name="mode"][value="${['reference', 'sandbox', 'vultr'].includes(run.mode) ? run.mode : 'reference'}"]`);
      input.checked = true;
      $('csv-file').value = '';
      captureBinding();
      updateMode();
    } finally { state.restoring = false; }
  }

  const scenario = createScenarioWorkspace({ api, openRun, announce, scrollTo,
    canStart: () => !state.busy && !state.stale && state.currentRun?.status === 'verified' && state.currentRun?.verification?.passed === true && state.currentRun?.case_context?.kind !== 'alternative',
    execute: async (id, payload) => {
      setBusy(true, 'Executing a separate scenario in the original mode, then independently checking both results.');
      try {
        const run = await api(`/api/runs/${safeRunId(id)}/scenario`, { method: 'POST', body: JSON.stringify(payload) });
        await restoreInputs(run);
        renderRun(run);
        await refreshHistory();
        scrollTo($('scenario-workspace'));
      } catch (error) { $('run-result').hidden = !state.currentRun; throw error; }
      finally { setBusy(false); }
    }
  });

  async function api(path, options = {}) {
    const response = await fetch(path, {
      credentials: 'same-origin',
      ...options,
      headers: { 'Accept': 'application/json', ...(options.body ? { 'Content-Type': 'application/json', 'X-Prooflane-Request': '1' } : {}), ...options.headers }
    });
    let body;
    try { body = await response.json(); } catch { throw new Error('The server returned an unreadable response. Check the service and try again.'); }
    if (!response.ok) {
      const detail = typeof body.detail === 'string' ? body.detail : 'The request could not be completed.';
      throw new Error(detail);
    }
    return body;
  }

  function updateRunButton() {
    $('run-button').disabled = state.busy || !state.csv.trim() || !modeAvailable(mode());
    text($('run-button-label'), state.busy ? 'Review in progress…' : 'Run invoice review');
  }

  function updateMode() {
    const selected = mode();
    $('token-field').hidden = selected !== 'vultr';
    if (selected !== 'vultr') $('operator-token').value = '';
    let note = modeCopy[selected].note;
    let unavailable = false;
    if (selected !== 'reference' && state.health && !state.health.docker?.available) {
      note += ' Docker is currently unavailable; this mode cannot execute.';
      unavailable = true;
    }
    if (selected === 'vultr' && state.health && (!state.health.inference?.configured || !state.health.inference?.enabled)) {
      note += ' Inference is not currently enabled and configured on this server.';
      unavailable = true;
    }
    text($('mode-note'), note);
    $('mode-note').classList.toggle('unavailable', unavailable);
    for (const input of document.querySelectorAll('input[name="mode"]')) {
      input.disabled = state.busy || !modeAvailable(input.value);
      input.closest('.mode-option').classList.toggle('mode-unavailable', !modeAvailable(input.value));
    }
    text($('sandbox-availability'), state.health?.docker?.available ? 'Fixed Python · real Docker execution' : state.health ? 'Unavailable · Docker is not ready' : 'Unavailable · service readiness not confirmed');
    text($('vultr-availability'), modeAvailable('vultr') ? 'Model writes code · Docker executes it' : !state.health ? 'Unavailable · service readiness not confirmed' : !state.health.inference?.configured ? 'Unavailable · inference is not configured' : !state.health.inference?.enabled ? 'Unavailable · inference is disabled' : 'Unavailable · Docker is not ready');
    updateRunButton();
    updateDraftBinding();
  }

  async function refreshHealth() {
    try {
      const health = await api('/api/health');
      state.health = health;
      window.prooflaneHealth = health;
      window.dispatchEvent(new CustomEvent('prooflane:health', { detail: health }));
      const dockerReady = !!health.docker?.available;
      const inferenceReady = !!(health.inference?.configured && health.inference?.enabled);
      const dot = element('span', `status-dot ${dockerReady ? '' : 'warning'}`);
      dot.setAttribute('aria-hidden', 'true');
      $('connection-summary').replaceChildren(dot, element('span', '', dockerReady ? 'Sandbox available' : 'Reference mode available'));
      text($('docker-health'), dockerReady ? 'Available' : 'Unavailable');
      $('docker-health').title = health.docker?.detail || '';
      text($('inference-health'), inferenceReady ? `Enabled · ${health.inference.model || 'model configured'}` : health.inference?.configured ? 'Configured · disabled' : 'Not configured');
      if (health.version) text($('app-version'), `Prooflane ${health.version} · Vultr Agent Rush 2026`);
      updateMode();
    } catch (error) {
      const dot = element('span', 'status-dot warning');
      dot.setAttribute('aria-hidden', 'true');
      $('connection-summary').replaceChildren(dot, element('span', '', 'Service check failed'));
      text($('docker-health'), 'Unknown · service unreachable');
      text($('inference-health'), 'Unknown');
      updateMode();
    }
  }

  function setCsv(csv, filename, synthetic = false) {
    if (new TextEncoder().encode(csv).byteLength > MAX_CSV_BYTES) throw new Error('This CSV is larger than 128 KiB. Please use a smaller file.');
    state.csv = csv;
    state.filename = filename || 'pasted-invoices.csv';
    state.synthetic = synthetic;
    $('csv-content').value = csv;
    text($('upload-title'), csv.trim() ? state.filename : 'Choose an invoice CSV');
    text($('upload-subtitle'), csv.trim() ? `${count(new TextEncoder().encode(csv).byteLength)} bytes · ready for review` : 'or drop a file here · up to 128 KiB');
    text($('dataset-label'), synthetic ? 'Synthetic sample · fictional invoices and vendors' : 'Your supplied data · review before sending');
    $('dataset-label').hidden = !csv.trim();
    updateRunButton();
    updateDraftBinding();
  }

  async function loadFile(file) {
    if (!file || state.busy) return;
    setError('form-error', '');
    try {
      if (file.size > MAX_CSV_BYTES) throw new Error('This file is larger than 128 KiB. Please use a smaller CSV.');
      if (!file.name.toLowerCase().endsWith('.csv')) throw new Error('Please select a .csv file.');
      const csv = await file.text();
      if (!csv.trim()) throw new Error('This file is empty. Choose a CSV with invoice rows.');
      setCsv(csv, file.name);
      announce(`${file.name} loaded. Ready to review.`);
    } catch (error) { setError('form-error', error.message); }
  }

  function dateLabel(value) {
    const date = new Date(value);
    return Number.isNaN(date.getTime()) ? '' : date.toLocaleString('en-US', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });
  }

  async function refreshHistory() {
    $('refresh-history').disabled = true;
    try {
      const result = await api('/api/runs');
      $('history-list').replaceChildren();
      const runs = Array.isArray(result.runs) ? result.runs : [];
      $('history-empty').hidden = runs.length > 0;
      setError('history-error', '');
      for (const run of runs.slice(0, 12)) {
        const li = element('li');
        const button = element('button', `history-button${state.currentRun?.id === run.id ? ' selected' : ''}`);
        button.type = 'button';
        button.dataset.runId = String(run.id);
        button.append(element('strong', '', run.filename || 'Invoice review'));
        const label = `${dateLabel(run.created_at)} · ${readable(run.mode)} · ${run.status === 'verified' ? money(run.total_variance) : readable(run.status)}`;
        button.append(element('span', '', label));
        button.addEventListener('click', () => openRun(run.id));
        li.append(button);
        $('history-list').append(li);
      }
    } catch (error) { setError('history-error', 'Recent runs could not be loaded.'); }
    finally { $('refresh-history').disabled = false; }
  }

  function setBusy(busy, description = 'Waiting for the server to complete the review.') {
    state.busy = busy;
    $('review-form').setAttribute('aria-busy', String(busy));
    $('results-title').parentElement.parentElement.setAttribute('aria-busy', String(busy));
    $('load-sample').disabled = busy;
    $('csv-file').disabled = busy;
    $('csv-content').disabled = busy;
    $('question').disabled = busy;
    $('operator-token').disabled = busy;
    updateMode();
    if (state.loadingTimer) { window.clearInterval(state.loadingTimer); state.loadingTimer = null; }
    $('loading-state').hidden = !busy;
    if (busy) {
      $('empty-state').hidden = true;
      $('run-result').hidden = true;
      statusPill($('run-status'), 'Running', 'neutral');
      text($('loading-description'), description);
      const started = performance.now();
      text($('loading-time'), '0 seconds elapsed');
      state.loadingTimer = window.setInterval(() => text($('loading-time'), `${Math.floor((performance.now() - started) / 1000)} seconds elapsed`), 1000);
    }
    $('restore-result').disabled = busy;
  }

  function renderChecks(container, checks) {
    container.replaceChildren();
    for (const check of checks || []) {
      const passed = check.passed === true;
      const li = element('li', passed ? 'passed' : 'failed');
      const symbol = element('span', 'check-symbol', passed ? '✓' : '!');
      symbol.setAttribute('aria-hidden', 'true');
      const copy = element('div');
      copy.append(element('strong', '', `${readable(check.name)} · ${passed ? 'passed' : 'not passed'}`), element('small', '', check.detail));
      li.append(symbol, copy);
      container.append(li);
    }
    if (!(checks || []).length) container.append(element('li', '', 'No verification checks were returned.'));
  }

  function renderVendors(vendors) {
    $('vendor-chart').replaceChildren();
    const sorted = (Array.isArray(vendors) ? vendors : []).filter(vendor => Number.isFinite(Number(vendor.variance)) && Number(vendor.variance) > 0).sort((a, b) => Number(b.variance) - Number(a.variance));
    const max = sorted.length ? Math.max(...sorted.map(vendor => Number(vendor.variance))) : 0;
    for (const vendor of sorted) {
      const row = element('div', 'vendor-row');
      const name = element('span', 'vendor-name', vendor.vendor);
      name.title = String(vendor.vendor || '');
      const track = element('div', 'bar-track');
      track.setAttribute('aria-hidden', 'true');
      const fill = element('div', 'bar-fill');
      fill.style.width = `${Math.max(0, Math.min(100, Number(vendor.variance) / max * 100))}%`;
      track.append(fill);
      row.append(name, track, element('span', 'vendor-value', money(vendor.variance)));
      $('vendor-chart').append(row);
    }
    if (!sorted.length) $('vendor-chart').append(element('p', 'field-help', 'No positive vendor variances to display.'));
  }

  function showFinding(finding) {
    text($('finding-dialog-title'), finding.invoice_id || 'Invoice finding');
    text($('finding-subtitle'), `${finding.vendor || 'Vendor not supplied'} · source row ${finding.row ?? 'unknown'} · ${state.currentRun?.filename || 'CSV'}`);
    const fields = [
      ['CSV row', finding.row], ['Vendor', finding.vendor], ['Quantity', finding.quantity],
      ['Unit price', money(finding.unit_price)], ['Contract price', money(finding.contract_price)], ['Notes', finding.notes || 'No note supplied.']
    ];
    $('finding-details').replaceChildren();
    for (const [label, value] of fields) $('finding-details').append(element('dt', '', label), element('dd', '', value));
    text($('finding-formula'), `(${money(finding.unit_price)} − ${money(finding.contract_price)}) × ${count(finding.quantity)}`);
    text($('finding-value'), money(finding.variance));
    scenario.finding(finding.row);
    $('finding-dialog').showModal();
  }

  function renderFindings(findings) {
    const rows = Array.isArray(findings) ? findings : [];
    text($('findings-count'), count(rows.length));
    $('findings-body').replaceChildren();
    $('no-findings').hidden = rows.length > 0;
    for (const finding of rows) {
      const tr = element('tr');
      const invoice = element('td');
      const link = element('button', 'invoice-link', finding.invoice_id || 'Inspect invoice');
      link.type = 'button';
      link.setAttribute('aria-label', `Inspect invoice ${finding.invoice_id || ''}, source row ${finding.row ?? 'unknown'}`);
      link.addEventListener('click', () => showFinding(finding));
      invoice.append(link, element('span', 'table-vendor', finding.vendor));
      const source = element('td');
      source.append(element('span', 'row-label', `row ${finding.row ?? '?'}`));
      const variance = element('td', 'number-column');
      variance.append(element('span', 'variance-value', money(finding.variance)));
      const arrow = element('td', 'row-arrow', '↗');
      arrow.setAttribute('aria-hidden', 'true');
      tr.append(invoice, source, variance, arrow);
      $('findings-body').append(tr);
    }
  }

  function renderEvents(events) {
    $('event-list').replaceChildren();
    for (const event of events || []) {
      const status = String(event.status || '').toLowerCase();
      const failed = ['failed', 'fail', 'error', 'blocked'].includes(status);
      const passed = ['pass', 'passed', 'success', 'completed', 'verified', 'ok'].includes(status);
      const icon = element('span', `event-icon${failed ? ' event-failed' : passed ? '' : ' event-neutral'}`, failed ? '!' : passed ? '✓' : '·');
      icon.setAttribute('aria-hidden', 'true');
      const copy = element('div');
      copy.append(element('div', 'event-title', `${readable(event.stage)}${status ? ` · ${readable(status)}` : ''}`), element('p', 'event-description', event.detail));
      const li = element('li');
      li.append(icon, copy);
      $('event-list').append(li);
    }
    if (!(events || []).length) $('event-list').append(element('li', 'field-help', 'No execution events were returned.'));
  }

  function renderRun(run) {
    state.currentRun = run;
    $('empty-state').hidden = true;
    $('loading-state').hidden = true;
    $('run-result').hidden = false;
    const verified = run.status === 'verified' && run.verification?.passed === true;
    statusPill($('run-status'), verified ? run.mode === 'reference' ? 'Reference complete' : 'Result verified' : run.status === 'failed' ? 'Run failed' : 'Not verified', verified ? 'success' : 'error');
    const provenance = modeCopy[run.mode] || { title: 'Execution mode not identified', detail: 'Inspect the execution record before relying on this result.' };
    text($('provenance-title'), provenance.title);
    text($('provenance-detail'), run.status === 'failed' ? 'This run did not finish successfully. The events below show what was attempted; no successful execution is implied.' : provenance.detail);
    $('provenance-banner').classList.toggle('reference', run.mode === 'reference');
    text($('result-filename'), `${run.filename || 'Invoice CSV'}${run.created_at ? ` · ${dateLabel(run.created_at)}` : ''}`);
    text($('result-run-id'), `RUN ${run.id}`);
    setError('run-error', run.error || (verified ? '' : 'This result did not pass verification. Inspect the checks and execution events.'));
    $('summary-content').hidden = !verified || !run.summary;
    if (run.summary && verified) {
      text($('stat-variance'), money(run.summary.total_variance));
      text($('stat-flagged'), count(run.summary.flagged_count));
      text($('stat-rows'), `of ${count(run.summary.row_count)} rows reviewed`);
      text($('stat-billed'), money(run.summary.total_billed));
      renderVendors(run.summary.vendors);
      renderFindings(run.summary.findings);
      $('explanation-panel').hidden = !run.explanation;
      text($('explanation-text'), run.explanation || '');
      text($('explanation-label'), 'REVIEW NOTE · FROM VERIFIED FIGURES');
    }
    renderEvents(run.events);
    const execution = run.execution || {};
    $('execution-meta').replaceChildren();
    const pairs = [ ['Runtime', execution.runtime], ['Elapsed', Number.isFinite(Number(execution.elapsed_ms)) && execution.elapsed_ms != null ? `${count(execution.elapsed_ms)} ms` : null], ['Container removed', execution.cleanup == null ? null : execution.cleanup ? 'confirmed' : 'unconfirmed'], ['Container', execution.container_id?.slice(0,12)] ];
    for (const [label, value] of pairs) if (value != null) $('execution-meta').append(element('span', '', `${label}: ${value}`));
    if (execution.limits) {
      const limits = execution.limits;
      $('execution-meta').append(element('span', '', `Network: ${limits.network} · Memory: ${limits.memory_mb} MiB · CPU: ${limits.cpu} · Time limit: ${limits.timeout_seconds}s`));
    }
    text($('verification-label'), run.mode === 'reference' ? 'Reference calculation checks' : 'Independent verification');
    text($('code-label'), run.mode === 'reference' ? 'Reference calculation source' : 'Executed code');
    renderChecks($('verification-list'), run.verification?.checks);
    const checks = run.verification?.checks || [];
    text($('verification-count'), `${checks.filter(check => check.passed === true).length}/${checks.length} passed`);
    text($('executed-code'), run.code || 'No code was returned for this run.');
    text($('receipt-hash'), run.receipt_hash || 'No receipt hash was returned.');
    $('download-receipt').href = `/api/runs/${safeRunId(run.id)}/receipt`;
    $('download-receipt').download = `prooflane-${String(run.id).replace(/[^a-zA-Z0-9_-]/g, '')}-receipt.json`;
    $('download-receipt').hidden = !verified || !run.receipt_hash;
    $('wb-promote-run').hidden = !verified || !!run.lineage || !!run.case_context;
    for (const button of document.querySelectorAll('.history-button')) button.classList.toggle('selected', button.dataset.runId === String(run.id));
    scenario.render(run);
    updateDraftBinding();
    announce(verified ? `Review complete. ${count(run.summary?.flagged_count)} lines flagged. ${money(run.summary?.total_variance)} price variance. ${run.mode === 'reference' ? 'Reference complete.' : 'Result verified.'}` : 'Review did not pass verification. Inspect the error and events.');
  }

  async function openRun(id) {
    if (state.busy) return;
    setError('form-error', '');
    setBusy(true, 'Loading the saved execution record.');
    try {
      const run = await api(`/api/runs/${safeRunId(id)}`);
      await restoreInputs(run);
      renderRun(run);
      scrollTo($('results-title'));
    } catch (error) {
      setError('form-error', error.message);
      if (state.currentRun) renderRun(state.currentRun);
      else { $('empty-state').hidden = false; statusPill($('run-status'), 'Could not load', 'error'); }
    } finally { setBusy(false); }
  }

  $('review-form').addEventListener('submit', async (event) => {
    event.preventDefault();
    if (state.busy) return;
    setError('form-error', '');
    const selected = mode();
    const question = $('question').value.trim() || DEFAULT_CONTEXT;
    if (!state.csv.trim()) { setError('form-error', 'Load or paste an invoice CSV first.'); return; }
    if ($('question').value.length > 600) { setError('form-error', 'Review context must be 600 characters or fewer.'); $('question').focus(); return; }
    if (!modeAvailable(selected)) { setError('form-error', 'This execution mode is unavailable. Choose an available mode.'); return; }
    if (new TextEncoder().encode(state.csv).byteLength > MAX_CSV_BYTES) { setError('form-error', 'The CSV is larger than 128 KiB.'); return; }
    const payload = { csv: state.csv, filename: state.filename, question, mode: selected };
    if (selected === 'vultr' && $('operator-token').value) payload.operator_token = $('operator-token').value;
    setBusy(true, selected === 'vultr' ? 'The server is coordinating inference, sandbox execution and result verification.' : selected === 'sandbox' ? 'The server is executing the fixed recipe in Docker and checking its output.' : 'The server is calculating invoice variances using trusted reference rules.');
    try {
      const run = await api('/api/runs', { method: 'POST', body: JSON.stringify(payload) });
      $('operator-token').value = '';
      captureBinding();
      renderRun(run);
      await refreshHistory();
    } catch (error) {
      $('operator-token').value = '';
      setError('form-error', error.message);
      statusPill($('run-status'), 'Request failed', 'error');
      $('empty-state').hidden = false;
      $('run-result').hidden = true;
      announce(`Review failed: ${error.message}`);
    } finally { setBusy(false); }
  });

  $('load-sample').addEventListener('click', async () => {
    if (state.busy) return;
    $('load-sample').disabled = true;
    setError('form-error', '');
    try {
      const sample = await api('/api/sample');
      setCsv(sample.csv, sample.filename || 'synthetic-invoices.csv', true);
      $('csv-file').value = '';
      announce('Synthetic sample loaded. These invoices and vendors are fictional.');
    } catch (error) { setError('form-error', error.message); }
    finally { $('load-sample').disabled = state.busy; }
  });

  $('csv-file').addEventListener('change', (event) => loadFile(event.target.files[0]));
  $('csv-content').addEventListener('input', (event) => {
    setError('form-error', '');
    try { setCsv(event.target.value, state.synthetic ? 'edited-invoices.csv' : state.filename, false); }
    catch (error) { state.csv = event.target.value; updateRunButton(); updateDraftBinding(); setError('form-error', error.message); }
  });
  for (const input of document.querySelectorAll('input[name="mode"]')) input.addEventListener('change', updateMode);
  $('question').addEventListener('input', updateDraftBinding);
  $('restore-result').addEventListener('click', () => { if (state.currentRun) openRun(state.currentRun.id); });
  for (const name of ['dragenter', 'dragover']) $('upload-zone').addEventListener(name, (event) => { event.preventDefault(); if (!state.busy) $('upload-zone').classList.add('drag-over'); });
  for (const name of ['dragleave', 'drop']) $('upload-zone').addEventListener(name, (event) => { event.preventDefault(); $('upload-zone').classList.remove('drag-over'); });
  $('upload-zone').addEventListener('drop', (event) => loadFile(event.dataTransfer.files[0]));
  $('refresh-history').addEventListener('click', refreshHistory);
  $('wb-promote-run').addEventListener('click', () => { if (state.currentRun && !state.busy && !state.stale) window.dispatchEvent(new CustomEvent('prooflane:promote-run', { detail: { id: state.currentRun.id, name: state.currentRun.filename || 'Embedded-price review' } })); });
  window.addEventListener('prooflane:open-run', event => { if (!state.busy) openRun(event.detail.id); });
  $('close-finding').addEventListener('click', () => $('finding-dialog').close());
  $('finding-dialog').addEventListener('click', (event) => { if (event.target === $('finding-dialog')) { const rect = $('finding-dialog').getBoundingClientRect(); if (event.clientX < rect.left || event.clientX > rect.right || event.clientY < rect.top || event.clientY > rect.bottom) $('finding-dialog').close(); } });

  $('check-containment').addEventListener('click', async () => {
    const button = $('check-containment');
    if (button.disabled) return;
    button.disabled = true;
    statusPill($('containment-status'), 'Running probes', 'neutral');
    setError('containment-error', '');
    $('containment-checks').hidden = true;
    $('containment-execution').hidden = true;
    try {
      const result = await api('/api/containment', { method: 'POST', body: '{}' });
      renderChecks($('containment-checks'), result.checks);
      $('containment-checks').hidden = false;
      statusPill($('containment-status'), result.passed === true ? 'Probes passed' : 'Not passed', result.passed === true ? 'success' : 'error');
      const execution = result.execution || {};
      text($('containment-execution'), `Runtime: ${execution.runtime || 'not reported'}. Elapsed: ${execution.elapsed_ms == null ? 'not reported' : `${count(execution.elapsed_ms)} ms`}. Cleanup: ${execution.cleanup == null ? 'not reported' : typeof execution.cleanup === 'string' ? execution.cleanup : JSON.stringify(execution.cleanup)}.`);
      $('containment-execution').hidden = false;
      announce(result.passed === true ? 'Containment probes passed. Inspect the individual test outcomes.' : 'Containment probes did not all pass. Inspect the outcomes.');
    } catch (error) {
      setError('containment-error', error.message);
      statusPill($('containment-status'), 'Not completed', 'error');
      announce('Containment check could not complete.');
    } finally { button.disabled = false; }
  });

  // Initialize the same-origin session before parallel requests use its cookie.
  if (window.matchMedia('(max-width: 700px)').matches) document.querySelector('.history-section').open = false;
  window.prooflaneSessionReady = (async () => { await refreshHealth(); window.dispatchEvent(new CustomEvent('prooflane:session-ready')); })();
  (async () => { await window.prooflaneSessionReady; await refreshHistory(); })();
})();
