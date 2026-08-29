(function () {
  var toggle = document.getElementById('navToggle');
  var nav = document.getElementById('sitioNav');
  var backdrop = document.getElementById('navBackdrop');
  if (!toggle || !nav) return;

  var ICONO_ABRIR = '☰';
  var ICONO_CERRAR = '✕';

  function abrirMenu() {
    nav.classList.add('is-open');
    if (backdrop) backdrop.classList.add('is-open');
    document.body.classList.add('sitio-body--menu-abierto');
    toggle.textContent = ICONO_CERRAR;
    toggle.setAttribute('aria-expanded', 'true');
  }

  function cerrarMenu() {
    nav.classList.remove('is-open');
    if (backdrop) backdrop.classList.remove('is-open');
    document.body.classList.remove('sitio-body--menu-abierto');
    toggle.textContent = ICONO_ABRIR;
    toggle.setAttribute('aria-expanded', 'false');
  }

  toggle.addEventListener('click', function () {
    if (nav.classList.contains('is-open')) {
      cerrarMenu();
    } else {
      abrirMenu();
    }
  });

  if (backdrop) {
    backdrop.addEventListener('click', cerrarMenu);
  }
})();
