import { test } from 'node:test';
import assert from 'node:assert/strict';
import { LOCATION_KEY, OPERATION_KEY, navigationState, operationState, readSession, writeSession } from '../web/review-session.js';
const id = 'a38c3e0e-1727-4912-af5f-64896e64da2c';
const memory = () => { const values = new Map(); return { getItem: key => values.get(key) || null, setItem: (key, value) => values.set(key, value), removeItem: key => values.delete(key) }; };
test('resume persists only a valid review ID and reading location, dropping sources and credentials', () => {
  const storage = memory();
  writeSession(storage, LOCATION_KEY, { id, view: 'explore', pane: 'alternatives', csv: 'PRIVATE', operator_token: 'SECRET', changes: [{ value: '5' }] }, navigationState);
  assert.deepEqual(readSession(storage, LOCATION_KEY, navigationState), { id, view: 'explore', pane: 'alternatives' });
  assert.doesNotMatch(storage.getItem(LOCATION_KEY), /PRIVATE|SECRET|changes/);
});
test('invalid or malformed saved navigation never creates a request target', () => {
  for (const value of [null, {}, { id: '../other', view: 'overview' }, { id, view: 'unknown' }]) assert.equal(navigationState(value), null);
  const storage = memory(); storage.setItem(LOCATION_KEY, '{');
  assert.equal(readSession(storage, LOCATION_KEY, navigationState), null);
});
test('denied browser storage does not prevent the review from running', () => {
  const storage = { getItem() { throw Error('denied'); }, setItem() { throw Error('denied'); }, removeItem() { throw Error('denied'); } };
  assert.equal(readSession(storage, LOCATION_KEY, navigationState), null);
  assert.equal(writeSession(storage, LOCATION_KEY, { id, view: 'overview' }, navigationState), false);
  assert.equal(readSession(null, LOCATION_KEY, navigationState), null);
});
test('pending recovery stores an operation identity without payloads or tokens and can be cleared', () => {
  const storage = memory();
  writeSession(storage, OPERATION_KEY, { id, kind: 'baseline', body: { operator_token: 'SECRET' } }, operationState);
  assert.deepEqual(readSession(storage, OPERATION_KEY, operationState), { id, kind: 'baseline' });
  assert.doesNotMatch(storage.getItem(OPERATION_KEY), /SECRET|body/);
  writeSession(storage, OPERATION_KEY, null, operationState);
  assert.equal(readSession(storage, OPERATION_KEY, operationState), null);
});
