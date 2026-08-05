// ============================================================
// NAVBAR.JS — Logica de la barra superior
// ============================================================

function bindClick(id, handler) {
  var el = document.getElementById(id);
  if (el) el.onclick = handler;
}

// ── ABRIR Y CERRAR EL MENU EN MOVIL ─────────────────────────

bindClick('menuToggle', function () {
  document.getElementById('sidebar').classList.add('open');
  document.getElementById('scrim').classList.add('open');
});

bindClick('scrim', function () {
  document.getElementById('sidebar').classList.remove('open');
  document.getElementById('scrim').classList.remove('open');
});

// ── TEMA CLARO U OSCURO ──────────────────────────────────────

bindClick('themeBtn', function () {
  var temaActual = document.documentElement.dataset.theme;
  var oscuro = temaActual !== 'dark';
  document.documentElement.dataset.theme = oscuro ? 'dark' : 'light';
  localStorage.setItem('tema', oscuro ? 'dark' : 'light');
});

var temaGuardado = localStorage.getItem('tema');
if (temaGuardado) {
  document.documentElement.dataset.theme = temaGuardado;
}

// ── MARCAR EL ITEM ACTIVO DEL SIDEBAR ───────────────────────
// Prefiere el enlace más específico para no activar Reservas y Contratos a la vez.

window.addEventListener('load', function () {
  var urlActual = window.location.pathname;
  var mejor = null;
  var mejorLen = -1;

  document.querySelectorAll('.nav-item').forEach(function (item) {
    item.classList.remove('active');
    var href = item.getAttribute('href');
    if (!href) return;

    var activo;
    if (href === '/') {
      activo = urlActual === '/';
    } else {
      var base = href.endsWith('/') ? href : href + '/';
      activo = urlActual === href || urlActual.startsWith(base);
    }

    // Documento de contrato individual → menú Contratos
    if (href.indexOf('/contratos') !== -1 && /\/contrato\/?$/.test(urlActual)) {
      activo = true;
    }

    if (activo && href.length > mejorLen) {
      mejor = item;
      mejorLen = href.length;
    }
  });

  if (mejor) mejor.classList.add('active');
});

// ── BUSCADOR CON ATAJO DE TECLADO ───────────────────────────

document.addEventListener('keydown', function (e) {
  if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
    e.preventDefault();
    document.getElementById('globalSearch')?.focus();
  }
});

// ── BOTON NUEVA RESERVA ──────────────────────────────────────

bindClick('btnNuevaReserva', function () {
  var url = this.getAttribute('data-url');
  if (url) window.location.href = url;
});

// ── NOTIFICACIONES DE RESERVAS WEB ───────────────────────────

(function () {
  var wrap = document.getElementById('notifWrap');
  var btn = document.getElementById('notifBtn');
  var panel = document.getElementById('notifPanel');
  if (!wrap || !btn || !panel) return;

  function cerrarPanel() {
    panel.hidden = true;
    btn.setAttribute('aria-expanded', 'false');
    btn.classList.remove('is-active');
    wrap.classList.remove('is-open');
  }

  function posicionarPanel() {
    var rect = btn.getBoundingClientRect();
    var margen = 8;
    var ancho = Math.min(320, window.innerWidth - 24);
    var top = rect.bottom + margen;
    var right = Math.max(12, window.innerWidth - rect.right);

    panel.style.width = ancho + 'px';
    panel.style.top = top + 'px';
    panel.style.right = right + 'px';
    panel.style.left = 'auto';

    var altoPanel = panel.offsetHeight;
    if (top + altoPanel > window.innerHeight - 12) {
      var arriba = rect.top - altoPanel - margen;
      if (arriba >= 12) {
        panel.style.top = arriba + 'px';
      }
    }
  }

  function abrirPanel() {
    panel.hidden = false;
    btn.setAttribute('aria-expanded', 'true');
    btn.classList.add('is-active');
    wrap.classList.add('is-open');
    posicionarPanel();
  }

  btn.addEventListener('click', function (e) {
    e.stopPropagation();
    if (panel.hidden) {
      abrirPanel();
    } else {
      cerrarPanel();
    }
  });

  document.addEventListener('click', function (e) {
    if (!wrap.contains(e.target)) {
      cerrarPanel();
    }
  });

  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') cerrarPanel();
  });

  window.addEventListener('resize', function () {
    if (!panel.hidden) posicionarPanel();
  });

  window.addEventListener('scroll', function (e) {
    if (panel.hidden) return;
    if (e.target === panel || (e.target && panel.contains(e.target))) return;
    cerrarPanel();
  }, true);
})();
