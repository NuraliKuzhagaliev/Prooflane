import { parsePrice, previewAt, dollars } from './landing-model.js';

// Keep previously shared single-file workspace links usable after adding a homepage.
if (location.hash === '#workspace') location.replace('/app#workspace');

const field = document.getElementById('contract-price');
const slider = document.getElementById('price-slider');
const error = document.getElementById('price-error');
const announcement = document.getElementById('price-announcement');
const presets = [...document.querySelectorAll('[data-price]')];
function display(cents, announce = false) {
  const result = previewAt(cents);
  slider.value = String(cents);
  slider.setAttribute('aria-valuetext', `${dollars(cents)} per unit`);
  error.hidden = true;
  field.removeAttribute('aria-invalid');
  document.getElementById('preview-total').value = dollars(result.total);
  const maximum = 80000; // One fixed USD800 scale, including the lowest allowed price.
  for (const row of result.rows) {
    document.getElementById(`variance-${row.id}`).textContent = dollars(row.variance);
    document.getElementById(`bar-${row.id}`).style.width = `${row.variance / maximum * 100}%`;
  }
  const priority = result.first.length === 1 ? `${result.first[0]} is first to review.` : `${result.first.join(' and ')} tie for first.`;
  document.getElementById('preview-priority').textContent = priority;
  for (const preset of presets) preset.setAttribute('aria-pressed', String(Number(preset.dataset.price) === cents));
  if (announce) announcement.textContent = `At ${dollars(cents)} per unit, positive variance is ${dollars(result.total)}. ${priority}`;
}
field.addEventListener('input', () => {
  const cents = parsePrice(field.value);
  if (cents !== null) display(cents);
  else {
    field.setAttribute('aria-invalid','true'); error.hidden = false;
    document.getElementById('preview-total').value = '—';
    for (const id of ['501','502','508']) {
      document.getElementById(`variance-${id}`).textContent = '—';
      document.getElementById(`bar-${id}`).style.width = '0%';
    }
    document.getElementById('preview-priority').textContent = 'Enter a valid price to calculate the review priority.';
  }
});
field.addEventListener('change', () => { const cents = parsePrice(field.value); if (cents !== null) display(cents, true); });
slider.addEventListener('input', () => { const cents = Number(slider.value); field.value = (cents / 100).toFixed(2); display(cents); });
slider.addEventListener('change', () => display(Number(slider.value), true));
for (const preset of presets) preset.addEventListener('click', () => { const cents = Number(preset.dataset.price); field.value = (cents / 100).toFixed(2); display(cents, true); });
display(7200);
