import test from 'node:test';
import assert from 'node:assert/strict';
import { parsePrice, previewAt, dollars } from '../web/landing-model.js';

test('landing price examples agree with the independently verified fictional case', () => {
  assert.equal(previewAt(7200).total,76800);
  assert.equal(previewAt(8000).total,36800);
  assert.equal(previewAt(6500).total,119300);
  assert.equal(previewAt(8500).total,14800);
  assert.deepEqual(previewAt(8000).rows.map(row=>row.variance),[20000,2000,0]);
});
test('whole-cent boundary changes priority without floating-point rounding', () => {
  assert.deepEqual(previewAt(8259).first,['INV501']);
  assert.deepEqual(previewAt(8260).first,['INV501','INV503']);
  assert.deepEqual(previewAt(8261).first,['INV503']);
  assert.equal(previewAt(8260).rows[0].variance,9600);
});
test('invalid or out-of-bounds prices never become preview results', () => {
  for (const value of ['', '72.001','8e1','NaN','-72','64.99','85.01']) assert.equal(parsePrice(value),null);
  assert.equal(parsePrice('82.60'),8260);
  assert.equal(parsePrice('72'),7200);
  for (const value of [6499,8501,7200.5,NaN]) assert.throws(()=>previewAt(value),RangeError);
});
test('landing display retains cents at the decision boundary', () => {
  assert.equal(dollars(8260),'$82.60');
  assert.equal(dollars(0),'$0.00');
  assert.equal(dollars(119300),'$1,193.00');
});
