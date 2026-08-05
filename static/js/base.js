// ============================================================
// BASE.JS — JavaScript global del panel
// ============================================================


// ── TEMA CLARO / OSCURO ──────────────────────────────────────
function setTema(dark) {
  document.documentElement.dataset.theme = dark ? 'dark' : 'light';
  localStorage.setItem('tema', dark ? 'dark' : 'light');
}

// Restaurar tema guardado al cargar la página
const temaGuardado = localStorage.getItem('tema') === 'dark';
setTema(temaGuardado);

// Botón de cambio de tema
document.getElementById('themeBtn').onclick = () => {
  setTema(document.documentElement.dataset.theme !== 'dark');
};


// ── SIDEBAR MÓVIL ────────────────────────────────────────────
function abrirSidebar() {
  document.getElementById('sidebar').classList.add('open');
  document.getElementById('scrim').classList.add('open');
}

function cerrarSidebar() {
  document.getElementById('sidebar').classList.remove('open');
  document.getElementById('scrim').classList.remove('open');
}

document.getElementById('menuToggle').onclick = abrirSidebar;
document.getElementById('scrim').onclick = cerrarSidebar;


// ── ÍTEM ACTIVO DEL SIDEBAR ──────────────────────────────────
// Marca el ítem según la URL actual al cargar la página
document.addEventListener('DOMContentLoaded', () => {
  const path = window.location.pathname;
  document.querySelectorAll('.nav-item').forEach(item => {
    if (item.getAttribute('href') && path.startsWith(item.getAttribute('href'))) {
      item.classList.add('active');
    }
  });
});

// Actualiza el ítem activo al navegar con HTMX
document.body.addEventListener('htmx:afterRequest', evt => {
  const url = evt.detail.pathInfo?.requestPath;
  if (!url) return;
  document.querySelectorAll('.nav-item').forEach(item => {
    item.classList.remove('active');
    if (item.getAttribute('href') && url.startsWith(item.getAttribute('href'))) {
      item.classList.add('active');
    }
  });
});


// ── TOAST — Notificación flotante ────────────────────────────
let toastTimer;

function showToast(msg) {
  const toast = document.getElementById('toast');
  document.getElementById('toastMsg').textContent = msg;
  toast.classList.add('show');
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => toast.classList.remove('show'), 2800);
}

// El servidor puede disparar el toast con el header:
// HX-Trigger: {"showToast": "Mensaje aquí"}
document.body.addEventListener('showToast', evt => {
  showToast(evt.detail.value);
});


// ── ATAJOS DE TECLADO ────────────────────────────────────────
document.addEventListener('keydown', e => {
  // Cmd+K o Ctrl+K abre el buscador
  if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'k') {
    e.preventDefault();
    document.getElementById('globalSearch')?.focus();
  }
  // Escape cierra modales y sidebar
  if (e.key === 'Escape') {
    document.querySelectorAll('.overlay').forEach(o => o.classList.remove('open'));
    cerrarSidebar();
  }
});


// ── MODALES ──────────────────────────────────────────────────
// Cierra el modal al hacer clic fuera de él
document.querySelectorAll('.overlay').forEach(overlay => {
  overlay.onclick = e => {
    if (e.target === overlay) overlay.classList.remove('open');
  };
});

// Botones con data-close cierran su modal
document.querySelectorAll('[data-close]').forEach(btn => {
  btn.onclick = () => btn.closest('.overlay').classList.remove('open');
});