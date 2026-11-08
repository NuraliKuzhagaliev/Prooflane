import { test } from 'node:test';
import assert from 'node:assert/strict';
import { money, signedMoney } from '../web/format.js';

test('preserves cents at the maximum supported input product', () => {
  assert.equal(money('99999899990000.01'), '$99,999,899,990,000.01');
});

test('preserves cents for the aggregate of 500 maximum rows', () => {
  assert.equal(money('49999949995000005.00'), '$49,999,949,995,000,005.00');
});

test('formats ordinary, fractional and zero amounts', () => {
  assert.equal(money('1480.00'), '$1,480.00');
  assert.equal(money('0.60'), '$0.60');
  assert.equal(money('2.5'), '$2.50');
  assert.equal(money('0'), '$0.00');
});

test('invalid or missing amounts remain unavailable', () => {
  for (const value of [null, undefined, '', 'NaN', 'Infinity', '1e3', '-1.00', '1.001', '<b>1</b>']) {
    assert.equal(money(value), '—');
  }
});

test('signed comparison amounts preserve direction and exact cents', () => {
  assert.equal(signedMoney('-320.00'), '−$320.00');
  assert.equal(signedMoney('320'), '+$320.00');
  assert.equal(signedMoney('+0.01'), '+$0.01');
  assert.equal(signedMoney('-49999949995000005.01'), '−$49,999,949,995,000,005.01');
  assert.equal(signedMoney('49999949995000005.01'), '+$49,999,949,995,000,005.01');
});

test('zero deltas are neutral and malformed deltas unavailable', () => {
  for (const value of ['0', '0.00', '-0.00', '+0.0']) assert.equal(signedMoney(value), '$0.00');
  for (const value of [null, undefined, '', '--1', '01.00', '1.001', '1e3', 'NaN', '<b>1</b>']) assert.equal(signedMoney(value), '—');
});
