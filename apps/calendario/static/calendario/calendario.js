// Calendario v2 — panel, Gantt, teclado, tooltips, preferencias
document.addEventListener('DOMContentLoaded', function () {
  var dataNode = document.getElementById('cal-eventos-data');
  var panel = document.getElementById('calPanel');
  var panelTitulo = document.getElementById('calPanelTitulo');
  var panelSub = document.getElementById('calPanelSub');
  var panelBody = document.getElementById('calPanelBody');
  var panelNueva = document.getElementById('calPanelNueva');
  var btnCerrar = document.getElementById('calPanelCerrar');
  var calMain = document.getElementById('calMain');
  var calGrid = document.getElementById('calGrid');
  var tooltip = document.getElementById('calTooltip');
  var fechaForm = document.getElementById('calFechaForm');
  var btnColor = document.getElementById('calColorModo');
  var btnDensidad = document.getElementById('calDensidad');
  var btnLeyenda = document.getElementById('calLeyendaToggle');
  var leyendaWrap = document.querySelector('.cal-leyenda-wrap');

  if (!dataNode) return;

  var eventos = JSON.parse(dataNode.textContent);
  var MESES = [
    '', 'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
    'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
  ];

  var fechaSeleccionada = null;

  function fmt(n) {
    return 'RD$ ' + Math.round(n).toLocaleString('es-DO');
  }

  function formatearFecha(iso) {
    var partes = iso.split('-');
    return parseInt(partes[2], 10) + ' de ' + MESES[parseInt(partes[1], 10)] + ' ' + partes[0];
  }

  function tipoDiaLabel(tipo) {
    if (tipo === 'entrega') return '🚗 Entrega';
    if (tipo === 'devolucion') return '🏁 Devolución';
    return '';
  }

  function scrollPanelVisible() {
    if (!panel || window.innerWidth > 1100) return;
    panel.classList.add('cal-panel-activo');
    setTimeout(function () {
      panel.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }, 80);
  }

  function renderPanel(fechaIso) {
    if (!panel || !panelTitulo || !panelBody) return;
    fechaSeleccionada = fechaIso;
    var lista = eventos[fechaIso] || [];

    document.querySelectorAll('.cal-celda.cal-seleccionada, .cal-semana-col.cal-seleccionada').forEach(function (el) {
      el.classList.remove('cal-seleccionada');
    });

    var celda = document.querySelector('.cal-celda[data-fecha="' + fechaIso + '"]')
      || document.querySelector('.cal-semana-col[data-fecha="' + fechaIso + '"]');
    if (celda) celda.classList.add('cal-seleccionada');

    panelTitulo.textContent = formatearFecha(fechaIso);
    panelSub.textContent = lista.length + ' reserva' + (lista.length === 1 ? '' : 's') + ' · doble clic para crear';

    if (panelNueva) {
      panelNueva.href = '/reservas/nueva/?fecha_inicio=' + fechaIso + '&fecha_fin=' + fechaIso;
    }

    if (!lista.length) {
      panelBody.innerHTML = '<p class="cal-panel-vacio">No hay reservas para este día.</p>';
      scrollPanelVisible();
      return;
    }

    panelBody.innerHTML = lista.map(function (ev) {
      var tipo = tipoDiaLabel(ev.tipo_dia);
      var acciones = '<div class="cal-panel-links">' +
        '<a href="' + ev.editar_url + '" class="cal-panel-link">Editar</a>' +
        '<a href="' + ev.pago_url + '" class="cal-panel-link">Pago</a>' +
        '<a href="' + ev.contrato_url + '" class="cal-panel-link">Contrato</a>';
      if (ev.puede_entrega) {
        acciones += '<a href="' + ev.entrega_url + '" class="cal-panel-link verde">Entrega</a>';
      }
      if (ev.puede_devolucion) {
        acciones += '<a href="' + ev.devolucion_url + '" class="cal-panel-link verde">Devolución</a>';
      }
      acciones += '</div>';

      return (
        '<div class="cal-panel-item">' +
          '<div class="cal-panel-item-top">' +
            '<div class="cal-panel-item-titulo">' + ev.vehiculo + '</div>' +
            '<span class="cal-panel-badge ' + ev.estado_clase + '">' + ev.estado + '</span>' +
          '</div>' +
          (tipo ? '<span class="cal-panel-tipo">' + tipo + '</span>' : '') +
          '<div class="cal-panel-item-sub">' + ev.cliente + ' · ' + ev.placa + '</div>' +
          '<div class="cal-panel-fechas">' + ev.fecha_inicio + ' → ' + ev.fecha_fin + ' (' + ev.dias + ' días)</div>' +
          '<div class="cal-panel-finanzas">' +
            '<span>Total: <strong>' + fmt(ev.precio_total) + '</strong></span>' +
            '<span>Pagado: <strong>' + fmt(ev.total_pagado) + '</strong></span>' +
            '<span>Saldo: <strong class="cal-saldo">' + fmt(ev.saldo_pendiente) + '</strong></span>' +
          '</div>' +
          '<span class="cal-panel-pago cal-panel-pago-' + ev.estado_pago + '">' + ev.estado_pago_label + '</span>' +
          acciones +
        '</div>'
      );
    }).join('');

    scrollPanelVisible();
  }

  function resetPanel() {
    if (!panel || !panelTitulo || !panelBody) return;
    fechaSeleccionada = null;
    document.querySelectorAll('.cal-celda.cal-seleccionada, .cal-semana-col.cal-seleccionada').forEach(function (el) {
      el.classList.remove('cal-seleccionada');
    });
    panelTitulo.textContent = 'Detalle del día';
    panelSub.textContent = 'Selecciona un día · doble clic para nueva reserva';
    panelBody.innerHTML = '<p class="cal-panel-vacio">Haz clic en un día para ver reservas, pagos y saldos. Usa ← → para cambiar de mes.</p>';
    if (panelNueva) panelNueva.href = '/reservas/nueva/';
  }

  function bindDia(el) {
    el.addEventListener('click', function (e) {
      if (e.target.closest('.cal-evento') || e.target.closest('.cal-mas')) return;
      renderPanel(el.getAttribute('data-fecha'));
    });

    el.addEventListener('dblclick', function (e) {
      if (e.target.closest('.cal-evento')) return;
      var f = el.getAttribute('data-fecha');
      window.location.href = '/reservas/nueva/?fecha_inicio=' + f + '&fecha_fin=' + f;
    });
  }

  document.querySelectorAll('.cal-celda[data-fecha], .cal-semana-col[data-fecha]').forEach(bindDia);

  document.querySelectorAll('.cal-mas').forEach(function (btn) {
    btn.addEventListener('click', function (e) {
      e.stopPropagation();
      renderPanel(btn.getAttribute('data-fecha'));
    });
  });

  if (btnCerrar) btnCerrar.addEventListener('click', resetPanel);

  /* Tooltips */
  function showTooltip(text, x, y) {
    if (!tooltip || !text) return;
    tooltip.textContent = text;
    tooltip.hidden = false;
    tooltip.style.left = x + 'px';
    tooltip.style.top = (y - 10) + 'px';
  }

  function hideTooltip() {
    if (tooltip) tooltip.hidden = true;
  }

  document.querySelectorAll('[data-tooltip]').forEach(function (el) {
    el.addEventListener('mouseenter', function (e) {
      showTooltip(el.getAttribute('data-tooltip'), e.clientX, e.clientY);
    });
    el.addEventListener('mousemove', function (e) {
      if (!tooltip || tooltip.hidden) return;
      tooltip.style.left = e.clientX + 'px';
      tooltip.style.top = (e.clientY - 10) + 'px';
    });
    el.addEventListener('mouseleave', hideTooltip);
  });

  /* Color por vehículo */
  function aplicarColoresVehiculo(activo) {
    if (!calMain) return;
    calMain.classList.toggle('cal-color-vehiculo', activo);
    document.querySelectorAll('.cal-evento[data-color-veh]').forEach(function (el) {
      if (activo) {
        el.style.setProperty('--ev-color', el.getAttribute('data-color-veh'));
      } else {
        el.style.removeProperty('--ev-color');
      }
    });
  }

  var colorVeh = localStorage.getItem('cal-color-veh') === '1';
  if (btnColor) {
    btnColor.textContent = colorVeh ? 'Color: vehículo' : 'Color: estado';
    aplicarColoresVehiculo(colorVeh);
    btnColor.addEventListener('click', function () {
      colorVeh = !colorVeh;
      localStorage.setItem('cal-color-veh', colorVeh ? '1' : '0');
      btnColor.textContent = colorVeh ? 'Color: vehículo' : 'Color: estado';
      aplicarColoresVehiculo(colorVeh);
    });
  }

  /* Densidad */
  var compacto = localStorage.getItem('cal-densidad') === 'compacto';
  if (calGrid) {
    calGrid.classList.toggle('cal-compacto', compacto);
  }
  if (btnDensidad) {
    btnDensidad.textContent = compacto ? 'Compacto' : 'Cómodo';
    btnDensidad.addEventListener('click', function () {
      compacto = !compacto;
      localStorage.setItem('cal-densidad', compacto ? 'compacto' : 'comodo');
      if (calGrid) calGrid.classList.toggle('cal-compacto', compacto);
      btnDensidad.textContent = compacto ? 'Compacto' : 'Cómodo';
    });
  }

  /* Leyenda colapsable */
  if (btnLeyenda && leyendaWrap) {
    var colapsada = localStorage.getItem('cal-leyenda') === '0';
    if (colapsada) leyendaWrap.classList.add('colapsada');
    btnLeyenda.setAttribute('aria-expanded', colapsada ? 'false' : 'true');
    btnLeyenda.addEventListener('click', function () {
      leyendaWrap.classList.toggle('colapsada');
      var c = leyendaWrap.classList.contains('colapsada');
      localStorage.setItem('cal-leyenda', c ? '0' : '1');
      btnLeyenda.setAttribute('aria-expanded', c ? 'false' : 'true');
    });
  }

  /* Selector mes/año auto-submit */
  if (fechaForm) {
    fechaForm.querySelectorAll('select').forEach(function (sel) {
      sel.addEventListener('change', function () { fechaForm.submit(); });
    });
  }

  /* Teclado: flechas mes, Esc cerrar panel */
  document.addEventListener('keydown', function (e) {
    if (e.target.matches('input, textarea, select')) return;

    if (e.key === 'Escape') {
      resetPanel();
      return;
    }

    if (!fechaSeleccionada && e.key !== 'ArrowLeft' && e.key !== 'ArrowRight') return;

    var anioNode = document.getElementById('cal-anio-data');
    var mesNode = document.getElementById('cal-mes-data');
    if (!anioNode || !mesNode) return;

    var anio = parseInt(JSON.parse(anioNode.textContent), 10);
    var mes = parseInt(JSON.parse(mesNode.textContent), 10);

    if (e.key === 'ArrowLeft' || e.key === 'ArrowRight') {
      var params = new URLSearchParams(window.location.search);
      var dir = e.key === 'ArrowLeft' ? -1 : 1;
      mes += dir;
      if (mes < 1) { mes = 12; anio -= 1; }
      if (mes > 12) { mes = 1; anio += 1; }
      params.set('anio', anio);
      params.set('mes', mes);
      if (!params.get('vista')) params.set('vista', 'mes');
      window.location.search = params.toString();
      return;
    }

    if (fechaSeleccionada && (e.key === 'ArrowUp' || e.key === 'ArrowDown')) {
      var d = new Date(fechaSeleccionada + 'T12:00:00');
      d.setDate(d.getDate() + (e.key === 'ArrowUp' ? -7 : 7));
      var iso = d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0') + '-' + String(d.getDate()).padStart(2, '0');
      if (eventos[iso] !== undefined || document.querySelector('[data-fecha="' + iso + '"]')) {
        renderPanel(iso);
      }
    }
  });

  /* Móvil: sugerir vista semana */
  var params = new URLSearchParams(window.location.search);
  if (window.innerWidth < 760 && (!params.get('vista') || params.get('vista') === 'mes')) {
    var toolbar = document.querySelector('.cal-toolbar');
    if (toolbar && !sessionStorage.getItem('cal-hint-semana')) {
      var hint = document.createElement('p');
      hint.className = 'cal-toolbar-resumen';
      hint.innerHTML = 'Tip: en celular prueba la vista <strong>Semana</strong> (arriba).';
      toolbar.appendChild(hint);
      sessionStorage.setItem('cal-hint-semana', '1');
    }
  }
});
