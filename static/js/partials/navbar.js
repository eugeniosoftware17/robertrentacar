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
    var margen = 12;
    var mobile = window.innerWidth <= 860;
    var ancho = Math.min(340, window.innerWidth - margen * 2);

    panel.style.width = ancho + 'px';
    panel.style.maxHeight = mobile
      ? Math.min(window.innerHeight * 0.72, 420) + 'px'
      : '';

    if (mobile) {
      panel.style.left = '50%';
      panel.style.right = 'auto';
      panel.style.transform = 'translateX(-50%)';
      var alto = panel.offsetHeight;
      var top = Math.max(64, (window.innerHeight - alto) / 2);
      panel.style.top = top + 'px';
      return;
    }

    panel.style.transform = '';
    panel.style.left = 'auto';
    var rect = btn.getBoundingClientRect();
    var topBtn = rect.bottom + margen;
    var right = Math.max(margen, window.innerWidth - rect.right);

    panel.style.top = topBtn + 'px';
    panel.style.right = right + 'px';

    var altoPanel = panel.offsetHeight;
    if (topBtn + altoPanel > window.innerHeight - margen) {
      var arriba = rect.top - altoPanel - margen;
      if (arriba >= margen) {
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

(function () {
  var input = document.getElementById('globalSearch');
  var panel = document.getElementById('globalSearchPanel');
  var wrap = document.getElementById('globalSearchWrap');
  if (!input || !panel || !wrap) return;

  var url = input.getAttribute('data-search-url');
  var timer = null;
  var controller = null;

  function cerrarBusqueda() {
    panel.hidden = true;
    input.setAttribute('aria-expanded', 'false');
  }

  function renderResultados(items) {
    panel.innerHTML = '';
    if (!items.length) {
      panel.innerHTML = '<p class="topbar-search-empty">Sin resultados</p>';
      panel.hidden = false;
      input.setAttribute('aria-expanded', 'true');
      return;
    }

    items.forEach(function (item) {
      var link = document.createElement('a');
      link.className = 'topbar-search-item';
      link.href = item.url;
      link.innerHTML = '<em>' + item.tipo + '</em><strong>' + item.titulo + '</strong><span>' + (item.subtitulo || '') + '</span>';
      panel.appendChild(link);
    });
    panel.hidden = false;
    input.setAttribute('aria-expanded', 'true');
  }

  function buscar() {
    var q = input.value.trim();
    if (q.length < 1) {
      cerrarBusqueda();
      return;
    }

    if (controller) controller.abort();
    controller = new AbortController();

    fetch(url + '?q=' + encodeURIComponent(q), {
      headers: { 'X-Requested-With': 'XMLHttpRequest' },
      signal: controller.signal,
    })
      .then(function (r) { return r.json(); })
      .then(function (data) { renderResultados(data.resultados || []); })
      .catch(function (err) {
        if (err.name !== 'AbortError') cerrarBusqueda();
      });
  }

  input.addEventListener('input', function () {
    clearTimeout(timer);
    timer = setTimeout(buscar, 250);
  });

  input.addEventListener('focus', function () {
    if (input.value.trim().length >= 1) buscar();
  });

  document.addEventListener('click', function (e) {
    if (!wrap.contains(e.target)) cerrarBusqueda();
  });

  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') cerrarBusqueda();
  });
})();
