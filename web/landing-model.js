// The public illustration is a bounded, fictional what-if calculation in cents.
// It never sends data, generates code, or substitutes for an executed review.
export function parsePrice(value) {
  const match = /^(\d{1,2})(?:\.(\d{1,2}))?$/.exec(String(value));
  if (!match) return null;
  const cents = Number(match[1]) * 100 + Number((match[2] || '').padEnd(2, '0'));
  return cents >= 6500 && cents <= 8500 ? cents : null;
}
export function previewAt(priceCents) {
  if (!Number.isInteger(priceCents) || priceCents < 6500 || priceCents > 8500) throw new RangeError('Price outside the fictional example.');
  const rows = [
    { id:'501', quantity:40, billed:8500 },
    { id:'502', quantity:10, billed:8200 },
    { id:'508', quantity:15, billed:7000 },
  ].map(row => ({ ...row, variance:row.quantity * Math.max(0, row.billed - priceCents) }));
  const others = [{ id:'503', variance:9600 }, { id:'504', variance:3200 }, { id:'505', variance:2000 }, { id:'507', variance:0 }];
  const maximum = Math.max(...rows.map(row => row.variance), ...others.map(row => row.variance));
  const first = [...rows, ...others].filter(row => row.variance === maximum).map(row => `INV${row.id}`).sort();
  return { rows, total:rows.reduce((sum, row) => sum + row.variance, 14800), first };
}
export function dollars(cents) {
  return `$${Math.floor(cents / 100).toLocaleString('en-US')}.${String(cents % 100).padStart(2,'0')}`;
}
