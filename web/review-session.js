// Only navigation IDs are retained. Source files, drafts and credentials never
// belong in browser storage. Storage can be unavailable in private contexts.
const UUID = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
const VIEWS = ['sources', 'overview', 'explore', 'evidence'];
export const LOCATION_KEY = 'prooflane.review-location.v1';
export const OPERATION_KEY = 'prooflane.pending-operation.v1';
export function navigationState(value) {
  if (!value || !UUID.test(value.id) || !VIEWS.includes(value.view)) return null;
  return { id: value.id, view: value.view, pane: value.pane === 'alternatives' ? 'alternatives' : 'ranges' };
}
export function operationState(value) {
  if (!value || !UUID.test(value.id) || !['baseline', 'alternative'].includes(value.kind)) return null;
  return { id: value.id, kind: value.kind };
}
export function readSession(storage, key, validate) {
  try { return validate(JSON.parse(storage.getItem(key))); } catch { return null; }
}
export function writeSession(storage, key, value, validate) {
  try {
    const safe = validate(value);
    if (safe) storage.setItem(key, JSON.stringify(safe));
    else storage.removeItem(key);
    return true;
  } catch { return false; }
}
