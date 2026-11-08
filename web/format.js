// API money values are exact nonnegative decimal strings. Keep them as strings:
// converting to Number can round cents even within the supported CSV bounds.
export function money(value) {
  const match = /^(0|[1-9]\d*)(?:\.(\d{1,2}))?$/.exec(String(value ?? ''));
  if (!match) return '—';
  const whole = match[1].replace(/\B(?=(\d{3})+(?!\d))/g, ',');
  return `$${whole}.${(match[2] || '').padEnd(2, '0')}`;
}

// Signed comparisons preserve decimal strings too, including beyond Number's
// safe integer range. A zero delta has no directional sign.
export function signedMoney(value) {
  const match = /^([+-]?)(0|[1-9]\d*)(?:\.(\d{1,2}))?$/.exec(String(value ?? ''));
  if (!match) return '—';
  const amount = `${match[2]}.${(match[3] || '').padEnd(2, '0')}`;
  const sign = /^0\.00$/.test(amount) ? '' : match[1] === '-' ? '−' : '+';
  return `${sign}${money(amount)}`;
}
