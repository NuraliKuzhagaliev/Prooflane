import { money } from './format.js';

export const fieldLabel = { contract_price: 'Contract price', unit_price: 'Billed unit price', quantity: 'Quantity' };
export const modeLabel = { reference: 'Reference calculation', sandbox: 'Sandbox recipe', vultr: 'Vultr agent' };
export const valueLabel = (field, value) => field === 'quantity' ? String(value ?? '—') : money(value);
export const completed = (run) => run?.status === 'verified' && run?.verification?.passed === true;
export const completionLabel = (run) => !completed(run) ? 'Not complete' : run.mode === 'reference' ? 'Reference complete' : 'Independently verified';
export const decisionLabel = (status) => ({ matched: 'Exact match', selected: 'Selected', ambiguous: 'Ambiguous', unmatched: 'Unmatched', excluded: 'Excluded', embedded: 'Embedded price' })[status] || status;
export const unresolved = (record) => ['ambiguous', 'unmatched'].includes(record.status);
export const chosenContract = (record) => record?.candidates?.find(item => item.contract_id === record.chosen_contract_id);

// Source row numbers survive exclusions; calculation row numbers do not.
export function sourceFocus(source, invoiceRow) {
  const record = source?.records?.find(item => item.invoice_row === Number(invoiceRow));
  if (!record) return null;
  if (record.status === 'excluded') return { row: null, excludedSourceRow: record.invoice_row };
  const binding = source.bindings?.find(item => item.invoice_row === record.invoice_row);
  if (binding) return { row: binding.row, excludedSourceRow: null };
  return source.kind === 'embedded' ? { row: record.invoice_row, excludedSourceRow: null } : null;
}

// Compare decimals as integers with a common scale. No monetary calculation or
// verified result is generated in the browser; this only validates draft input.
export function decimalCents(value) {
  const m = /^(0|[1-9]\d*)(?:\.(\d{1,2}))?$/.exec(String(value));
  if (!m) return null;
  return BigInt(m[1]) * 100n + BigInt((m[2] || '').padEnd(2, '0'));
}

export function validateValue(field, value) {
  if (field === 'quantity') return /^[1-9]\d{0,5}$/.test(value) ? '' : 'Quantity must be a whole number from 1 to 999999.';
  return /^(0|[1-9]\d{0,7})(?:\.\d{1,2})?$/.test(value) ? '' : 'Enter a nonnegative USD price, up to 99999999.99, with at most two decimals.';
}

export function validateChange(target, value, changes, limit = 12) {
  if (!target) return 'Choose a target from the original baseline.';
  if (changes.length >= limit) return `An alternative supports at most ${limit} changes.`;
  if (changes.some(change => change.target === target.id)) return 'This target is already in the draft. Remove it before replacing its value.';
  const invalid = validateValue(target.field, value);
  if (invalid) return invalid;
  if (decimalCents(value) === decimalCents(target.before)) return 'Enter a different value; an alternative must change the original assumption.';
  return '';
}

export function validateRange(target, low, high) {
  if (!target) return 'Choose an assumption target.';
  const invalid = validateValue(target.field, low) || validateValue(target.field, high);
  if (invalid) return invalid;
  if (decimalCents(low) > decimalCents(target.before) || decimalCents(high) < decimalCents(target.before)) return 'The range must include the original value, with low no greater than high.';
  return '';
}

export function filterMatches(records, filter, query) {
  const needle = query.trim().toLowerCase();
  return records.filter(row => (filter === 'all' || filter === 'unresolved' && unresolved(row) || filter === 'matched' && ['matched', 'selected', 'embedded'].includes(row.status) || row.status === filter) && `${row.invoice_id} ${row.vendor} ${row.item_id || ''} ${row.chosen_contract_id || ''}`.toLowerCase().includes(needle));
}
