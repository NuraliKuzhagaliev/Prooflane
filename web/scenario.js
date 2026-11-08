import { money, signedMoney } from './format.js';

const labels = { contract_price: 'Contract price', unit_price: 'Billed unit price', quantity: 'Quantity' };
const modes = { reference: 'Reference calculation · fixed rules, no model or sandbox', sandbox: 'Sandbox recipe · fixed Python in Docker', vultr: 'Vultr agent · generated Python in Docker' };
const $ = (id) => document.getElementById(id);
const set = (id, value) => { $(id).textContent = value == null ? '' : String(value); };
const valueLabel = (field, value) => field === 'quantity' ? String(value) : money(value);
const url = (id, suffix) => `/api/runs/${encodeURIComponent(id)}/${suffix}`;

export function createScenarioWorkspace({ api, execute, openRun, canStart, announce, scrollTo }) {
  let run = null;
  let source = null;
  let selectedFinding = null;
  let loading = false;

  function error(message = '') {
    set('scenario-error', message);
    $('scenario-error').hidden = !message;
  }

  function syncAvailability() {
    const available = !!run && !run.lineage && run.case_context?.kind !== 'alternative' && canStart();
    $('start-scenario').disabled = loading || !available;
    $('run-scenario').disabled = loading || !available;
    $('finding-scenario').disabled = !available;
    $('finding-scenario-note').hidden = available;
    set('finding-scenario-note', run?.case_context?.kind === 'alternative' ? 'This is a case alternative. Return to the case workbench to test another assumption against its original baseline.' : run?.lineage ? 'Return to the original baseline to test another assumption.' : 'Reopen this saved run or review the current draft before testing an assumption.');
  }

  function preview() {
    const row = source?.rows.find((item) => String(item.row) === $('scenario-row').value);
    const field = $('scenario-field').value;
    set('scenario-before', row ? valueLabel(field, row[field]) : '—');
    set('scenario-source', row ? `Original source row ${row.row}: quantity ${row.quantity} · billed unit price ${money(row.unit_price)} · contract price ${money(row.contract_price)}` : '');
    const proposed = $('scenario-value').value.trim();
    set('scenario-after', proposed ? valueLabel(field, proposed) : 'Enter a value');
    $('scenario-value').inputMode = field === 'quantity' ? 'numeric' : 'decimal';
    $('scenario-value').pattern = field === 'quantity' ? '[1-9][0-9]*' : '(0|[1-9][0-9]*)(\\.[0-9]{1,2})?';
    $('scenario-value').title = field === 'quantity' ? 'A positive whole quantity' : 'A nonnegative USD amount with at most two decimal places';
  }

  async function start(rowNumber = null) {
    if (loading || !run || run.lineage || run.case_context?.kind === 'alternative' || !canStart()) return;
    const baseline = run;
    loading = true;
    syncAvailability();
    error();
    set('scenario-status', 'Loading source rows');
    try {
      const result = source || await api(url(baseline.id, 'source'));
      if (run?.id !== baseline.id || !canStart()) return;
      source = result;
      $('scenario-row').replaceChildren(...source.rows.map((row) => {
        const option = document.createElement('option');
        option.value = String(row.row);
        option.textContent = `Row ${row.row} · ${row.invoice_id} · ${row.vendor}`;
        return option;
      }));
      if (rowNumber != null) $('scenario-row').value = String(rowNumber);
      $('scenario-field').value = 'contract_price';
      $('scenario-value').value = '';
      $('scenario-token').value = '';
      $('scenario-token-field').hidden = baseline.mode !== 'vultr';
      $('scenario-token').required = baseline.mode === 'vultr';
      set('scenario-baseline', `Original: ${baseline.filename} · ${baseline.id}`);
      set('scenario-mode', `Same execution mode: ${modes[baseline.mode] || baseline.mode}. No automatic fallback.`);
      $('scenario-entry').hidden = true;
      $('scenario-form').hidden = false;
      set('scenario-status', 'Draft · not executed');
      preview();
      scrollTo($('scenario-workspace'));
      $('scenario-value').focus({ preventScroll: true });
      announce('Choose one source field and enter a proposed value. The original review remains unchanged.');
    } catch (failure) { error(failure.message); set('scenario-status', 'Source unavailable'); }
    finally { loading = false; syncAvailability(); }
  }

  function render(nextRun) {
    run = nextRun;
    source = null;
    selectedFinding = null;
    error();
    $('scenario-form').hidden = true;
    $('scenario-token').value = '';
    const isScenario = !!run.lineage;
    const verified = run.status === 'verified' && run.verification?.passed === true;
    $('scenario-workspace').hidden = run.case_context?.kind === 'alternative' || !verified && !isScenario;
    $('scenario-entry').hidden = isScenario;
    $('comparison-result').hidden = !run.comparison || !verified;
    $('scenario-return').hidden = !isScenario;
    set('scenario-title', isScenario ? 'One change. A separate result.' : 'What if one input changed?');
    set('scenario-status', isScenario ? verified ? run.mode === 'reference' ? 'Reference complete · hypothetical' : 'Verified · hypothetical' : 'Scenario failed' : 'Original preserved');
    $('scenario-status').className = `status-pill ${verified && isScenario ? '' : 'neutral-pill'}`;
    if (isScenario && !verified) error('This scenario did not produce a verified comparison. The original review is unchanged; return to it to try again.');
    if (run.comparison && verified) {
      const c = run.comparison;
      const change = c.change;
      set('comparison-change', `${change.invoice_id} · ${change.vendor} · source row ${change.row}: ${labels[change.field]} ${valueLabel(change.field, change.before)} → ${valueLabel(change.field, change.after)}`);
      set('comparison-before', money(c.baseline.total_variance));
      set('comparison-after', money(c.scenario.total_variance));
      set('comparison-delta', signedMoney(c.delta.total_variance));
      $('comparison-facts').replaceChildren();
      const facts = [
        ['Changed row variance', `${money(change.before_variance)} → ${money(change.after_variance)} (${signedMoney(change.variance_delta)})`],
        ['Total billed', `${money(c.baseline.total_billed)} → ${money(c.scenario.total_billed)} (${signedMoney(c.delta.total_billed)})`],
        ['Flagged lines', `${c.baseline.flagged_count} → ${c.scenario.flagged_count}`],
        ['Unchanged source records', String(c.unchanged_records)],
        ['Execution mode for both', modes[run.mode] || run.mode]
      ];
      for (const [label, value] of facts) {
        const term = document.createElement('dt'); term.textContent = label;
        const detail = document.createElement('dd'); detail.textContent = value;
        $('comparison-facts').append(term, detail);
      }
      set('comparison-scope', 'Hypothetical result based on supplied data. This is not a contract correction, payment instruction or recovered savings.');
      $('baseline-receipt').href = url(c.baseline.run_id, 'receipt');
      $('scenario-receipt').href = url(c.scenario.run_id, 'receipt');
      $('download-comparison').href = url(run.id, 'comparison');
      set('comparison-baseline-hash', c.baseline.receipt_sha256);
      set('comparison-scenario-hash', c.scenario.receipt_sha256);
    }
    syncAvailability();
  }

  $('start-scenario').addEventListener('click', () => start());
  $('finding-scenario').addEventListener('click', () => {
    $('finding-dialog').close();
    start(selectedFinding);
  });
  $('cancel-scenario').addEventListener('click', () => {
    $('scenario-form').hidden = true;
    $('scenario-entry').hidden = false;
    $('scenario-token').value = '';
    error();
    set('scenario-status', 'Original preserved');
    $('start-scenario').focus();
  });
  $('return-baseline').addEventListener('click', () => { if (run?.lineage) openRun(run.lineage.baseline_run_id); });
  $('scenario-row').addEventListener('change', () => { $('scenario-value').value = ''; preview(); });
  $('scenario-field').addEventListener('change', () => { $('scenario-value').value = ''; preview(); });
  $('scenario-value').addEventListener('input', preview);
  $('scenario-form').addEventListener('submit', async (event) => {
    event.preventDefault();
    if (loading || !run || !source || !canStart()) return;
    const original = source.rows.find((item) => String(item.row) === $('scenario-row').value);
    if (!original) { error('Select a source row from this original review.'); return; }
    const field = $('scenario-field').value;
    const value = $('scenario-value').value.trim();
    const normalize = (v) => String(v).replace(/\.0*$/, '').replace(/(\.\d*?)0+$/, '$1');
    if (normalize(value) === normalize(original[field])) {
      error('Enter a different value. A scenario must change one numeric assumption.');
      $('scenario-value').focus();
      return;
    }
    error();
    const payload = { baseline_receipt_sha256: source.baseline_receipt_sha256, row: original.row, field, value };
    if (run.mode === 'vultr') payload.operator_token = $('scenario-token').value;
    $('scenario-token').value = '';
    loading = true;
    syncAvailability();
    try { await execute(run.id, payload); }
    catch (failure) { error(failure.message); announce(`Comparison could not complete: ${failure.message}`); }
    finally { loading = false; syncAvailability(); }
  });
  return { render, syncAvailability, finding: (row) => { selectedFinding = row; syncAvailability(); } };
}
