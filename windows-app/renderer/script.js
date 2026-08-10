// Origin-Core Desktop — sidebar navigation + order code generator

// --- titlebar controls ---
document.getElementById('btn-min')?.addEventListener('click', () => window.originCore?.minimize());
document.getElementById('btn-max')?.addEventListener('click', () => window.originCore?.maximize());
document.getElementById('btn-close')?.addEventListener('click', () => window.originCore?.close());

// --- sidebar navigation ---
const navButtons = document.querySelectorAll('.side-nav button[data-view]');
const views = document.querySelectorAll('.view');

navButtons.forEach((btn) => {
  btn.addEventListener('click', () => {
    navButtons.forEach((b) => b.classList.remove('active'));
    btn.classList.add('active');
    views.forEach((v) => v.classList.remove('active'));
    document.getElementById(`view-${btn.dataset.view}`)?.classList.add('active');
  });
});

// --- order code generator (same logic as the website) ---
const TELEGRAM_ID = '@RIDOX_Neonguard';

function randomSegment(len) {
  const chars = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789';
  let out = '';
  for (let i = 0; i < len; i++) out += chars[Math.floor(Math.random() * chars.length)];
  return out;
}

function generateOrderCode(prefix) {
  return `${prefix}-${randomSegment(4)}-${randomSegment(4)}`;
}

function buildPanel(container, code, planName) {
  container.innerHTML = `
    <div class="label">کد سفارش «${planName}»</div>
    <div class="code-row">
      <div class="code-box mono">${code}</div>
      <button class="copy-btn" type="button" aria-label="کپی کد">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <rect x="9" y="9" width="12" height="12" rx="2"/><path d="M5 15V5a2 2 0 0 1 2-2h10"/>
        </svg>
      </button>
    </div>
    <div class="hint">این کد را کپی و برای خرید و تحویل به آیدی <b>${TELEGRAM_ID}</b> ارسال کنید.</div>
  `;
  const copyBtn = container.querySelector('.copy-btn');
  copyBtn.addEventListener('click', async () => {
    try {
      await navigator.clipboard.writeText(code);
    } catch (e) {
      const ta = document.createElement('textarea');
      ta.value = code;
      document.body.appendChild(ta);
      ta.select();
      document.execCommand('copy');
      document.body.removeChild(ta);
    }
    copyBtn.classList.add('copied');
    setTimeout(() => copyBtn.classList.remove('copied'), 1500);
  });
}

document.querySelectorAll('.buy-btn').forEach((btn) => {
  btn.addEventListener('click', () => {
    const prefix = btn.dataset.plan;
    const name = btn.dataset.name;
    const panel = btn.closest('.plan').querySelector('[data-panel]');
    const code = generateOrderCode(prefix);
    buildPanel(panel, code, name);
    panel.classList.add('show');
  });
});
