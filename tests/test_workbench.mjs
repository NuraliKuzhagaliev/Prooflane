import { test } from 'node:test';
import assert from 'node:assert/strict';
import { decimalCents, validateChange, validateRange, filterMatches, completionLabel, chosenContract, sourceFocus } from '../web/workbench-model.js';

const contract = { id: 'contract:C1', field: 'contract_price', before: '75.00', rows: [2, 3, 9] };
test('source focus preserves original identity after a preceding exclusion', () => {
  const source = { kind: 'contracts', records: [{ invoice_row: 7, status: 'excluded' }, { invoice_row: 8, status: 'matched' }], bindings: [{ invoice_row: 8, row: 7 }] };
  assert.deepEqual(sourceFocus(source, '8'), { row: 7, excludedSourceRow: null });
  assert.deepEqual(sourceFocus(source, 7), { row: null, excludedSourceRow: 7 });
  assert.equal(sourceFocus(source, 6), null);
});
test('source focus never guesses a calculation row for a missing contract binding', () => {
  assert.equal(sourceFocus({ kind: 'contracts', records: [{ invoice_row: 8, status: 'matched' }], bindings: [] }, 8), null);
  assert.deepEqual(sourceFocus({ kind: 'embedded', records: [{ invoice_row: 8, status: 'embedded' }], bindings: [] }, 8), { row: 8, excludedSourceRow: null });
});
test('reference results cannot claim independent execution verification', () => {
  assert.equal(completionLabel({ mode: 'reference', status: 'verified', verification: { passed: true } }), 'Reference complete');
  assert.equal(completionLabel({ mode: 'sandbox', status: 'verified', verification: { passed: true } }), 'Independently verified');
  assert.equal(completionLabel({ mode: 'sandbox', status: 'failed', verification: { passed: false } }), 'Not complete');
});
test('decimal draft comparisons preserve cents beyond Number precision', () => {
  assert.equal(decimalCents('49999949995000005.01'), 4999994999500000501n);
  assert.equal(decimalCents('75'), decimalCents('75.00'));
});
test('drafts reject no-ops, repeated targets, over-capacity and invalid quantities', () => {
  assert.match(validateChange(contract, '75', []), /different value/);
  assert.match(validateChange(contract, '80', [{ target: 'contract:C1', value: '70' }]), /already/);
  assert.match(validateChange(contract, '80', Array(12).fill({ target: 'other' })), /12/);
  assert.match(validateChange({ ...contract, field: 'quantity' }, '1.5', []), /whole number/);
  assert.match(validateChange(contract, '100000000.00', []), /99999999/);
  assert.equal(validateChange(contract, '80.01', []), '');
});
test('ranges must contain the original and obey field precision', () => {
  assert.equal(validateRange(contract, '65', '85'), '');
  assert.equal(validateRange(contract, '75', '75.00'), '');
  assert.match(validateRange(contract, '76', '85'), /include the original/);
  assert.match(validateRange(contract, '65', '74.99'), /include the original/);
  assert.match(validateRange(contract, '65.001', '85'), /two decimals/);
});
test('source queue separates unresolved, selected and excluded with case-insensitive text search', () => {
  const rows = [{ invoice_id: 'INV1', vendor: 'Atlas', status: 'ambiguous' }, { invoice_id: 'INV2', vendor: 'Nova', status: 'selected' }, { invoice_id: 'INV3', vendor: 'Atlas', status: 'excluded' }];
  assert.equal(filterMatches(rows, 'unresolved', '').length, 1);
  assert.equal(filterMatches(rows, 'matched', '')[0].invoice_id, 'INV2');
  assert.equal(filterMatches(rows, 'all', 'ATLAS').length, 2);
  assert.equal(filterMatches(rows, 'excluded', 'INV3').length, 1);
});
test('contract inspector only identifies the explicitly returned chosen candidate', () => {
  const record = { chosen_contract_id: 'C2R', candidates: [{ contract_id: 'C2' }, { contract_id: 'C2R' }] };
  assert.equal(chosenContract(record).contract_id, 'C2R');
  assert.equal(chosenContract({ ...record, chosen_contract_id: null }), undefined);
});
