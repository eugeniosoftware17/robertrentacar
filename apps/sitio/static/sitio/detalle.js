(function () {
  var box = document.getElementById('calendarioReserva');
  if (!box) return;

  var ocupadas = new Set(JSON.parse(box.dataset.ocupadas || '[]'));
  var mantenimiento = new Set(JSON.parse(box.dataset.mantenimiento || '[]'));
  var reservarBase = box.dataset.reservarUrl;
  var minDate = box.dataset.min;

  var inpInicio = document.getElementById('fechaInicio');
  var inpFin = document.getElementById('fechaFin');
  var totalEl = document.getElementById('totalEstimado');
  var btn = document.getElementById('btnReservar');
  var calGrid = document.getElementById('sitio-cal-grid');
  var calTitulo = document.getElementById('sitio-cal-titulo');
  var btnPrev = document.getElementById('sitio-cal-prev');
  var btnNext = document.getElementById('sitio-cal-next');

  var MESES = [
    '', 'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
    'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
  ];

  var calAnio, calMes;

  function parseDate(str) {
    if (!str) return null;
    var p = str.split('-');
    return new Date(parseInt(p[0], 10), parseInt(p[1], 10) - 1, parseInt(p[2], 10));
  }

  function iso(d) {
    var m = String(d.getMonth() + 1).padStart(2, '0');
    var day = String(d.getDate()).padStart(2, '0');
    return d.getFullYear() + '-' + m + '-' + day;
  }

  function isoDesdePartes(anio, mes, dia) {
    return anio + '-' + String(mes).padStart(2, '0') + '-' + String(dia).padStart(2, '0');
  }

  function diasEnMes(anio, mes) {
    return new Date(anio, mes, 0).getDate();
  }

  function primerDiaSemana(anio, mes) {
    var d = new Date(anio, mes - 1, 1).getDay();
    return d === 0 ? 6 : d - 1;
  }

  function diaBloqueado(str) {
    return ocupadas.has(str) || mantenimiento.has(str);
  }

  function rangoSeleccionado(fi, ff) {
    var dias = [];
    if (!fi || !ff) return dias;
    var d1 = parseDate(fi);
    var d2 = parseDate(ff);
    if (!d1 || !d2 || d2 < d1) return dias;
    var cur = new Date(d1);
    while (cur <= d2) {
      dias.push(iso(cur));
      cur.setDate(cur.getDate() + 1);
    }
    return dias;
  }

  function rangoValido(inicio, fin) {
    if (!inicio || !fin || fin < inicio) return false;
    var d = new Date(inicio);
    while (d <= fin) {
      if (diaBloqueado(iso(d))) return false;
      d.setDate(d.getDate() + 1);
    }
    return true;
  }

  function diasEntre(inicio, fin) {
    return Math.floor((fin - inicio) / 86400000) + 1;
  }

  function renderCalendario() {
    if (!calGrid) return;
    calTitulo.textContent = MESES[calMes] + ' ' + calAnio;

    var seleccion = rangoSeleccionado(inpInicio.value, inpFin.value);
    var hoy = iso(new Date());
    var totalDias = diasEnMes(calAnio, calMes);
    var offset = primerDiaSemana(calAnio, calMes);
    var html = '';

    for (var i = 0; i < offset; i++) {
      html += '<div class="sitio-cal-dia vacio"></div>';
    }

    for (var dia = 1; dia <= totalDias; dia++) {
      var fecha = isoDesdePartes(calAnio, calMes, dia);
      var clases = ['sitio-cal-dia'];
      var bloqueado = diaBloqueado(fecha);

      if (bloqueado) clases.push('ocupado');
      if (seleccion.indexOf(fecha) !== -1) clases.push('seleccion');
      if (fecha === hoy) clases.push('hoy');
      if (minDate && fecha < minDate) clases.push('pasado');

      var titulo = bloqueado ? 'No disponible' : 'Disponible';
      html += '<button type="button" class="' + clases.join(' ') + '" data-fecha="' + fecha + '" title="' + titulo + '"';
      if (bloqueado || (minDate && fecha < minDate)) html += ' disabled';
      html += '>' + dia + '</button>';
    }

    calGrid.innerHTML = html;
  }

  function sincronizarMes() {
    var ref = inpInicio.value || inpFin.value;
    if (ref) {
      var p = ref.split('-');
      calAnio = parseInt(p[0], 10);
      calMes = parseInt(p[1], 10);
    } else {
      var hoy = new Date();
      calAnio = hoy.getFullYear();
      calMes = hoy.getMonth() + 1;
    }
  }

  function actualizar() {
    var di = parseDate(inpInicio.value);
    var df = parseDate(inpFin.value);
    renderCalendario();

    if (!di || !df) {
      totalEl.textContent = 'Selecciona fechas en el calendario o en los campos.';
      btn.classList.add('sitio-btn--disabled');
      btn.href = '#';
      return;
    }
    if (!rangoValido(di, df)) {
      totalEl.textContent = 'Hay días no disponibles en ese rango. Elige otras fechas.';
      btn.classList.add('sitio-btn--disabled');
      btn.href = '#';
      return;
    }
    var dias = diasEntre(di, df);
    var tarifa = parseFloat(window.SITIO_TARIFA_DIA) || 0;
    totalEl.textContent =
      dias + ' día(s) · estimado USD$ ' + (dias * tarifa).toLocaleString('es-DO');
    btn.classList.remove('sitio-btn--disabled');
    btn.href =
      reservarBase +
      '?desde=' +
      encodeURIComponent(inpInicio.value) +
      '&hasta=' +
      encodeURIComponent(inpFin.value);
  }

  function seleccionarFecha(fecha) {
    if (diaBloqueado(fecha) || (minDate && fecha < minDate)) return;

    if (!inpInicio.value || (inpInicio.value && inpFin.value)) {
      inpInicio.value = fecha;
      inpFin.value = fecha;
    } else if (fecha >= inpInicio.value) {
      inpFin.value = fecha;
    } else {
      inpInicio.value = fecha;
      inpFin.value = fecha;
    }
    sincronizarMes();
    actualizar();
  }

  [inpInicio, inpFin].forEach(function (el) {
    el.addEventListener('change', function () {
      sincronizarMes();
      actualizar();
    });
  });

  if (minDate) {
    inpInicio.min = minDate;
    inpFin.min = minDate;
  }

  if (btnPrev) {
    btnPrev.addEventListener('click', function () {
      if (calMes === 1) { calAnio -= 1; calMes = 12; }
      else calMes -= 1;
      renderCalendario();
    });
  }

  if (btnNext) {
    btnNext.addEventListener('click', function () {
      if (calMes === 12) { calAnio += 1; calMes = 1; }
      else calMes += 1;
      renderCalendario();
    });
  }

  if (calGrid) {
    calGrid.addEventListener('click', function (e) {
      var celda = e.target.closest('[data-fecha]');
      if (!celda || celda.disabled) return;
      seleccionarFecha(celda.getAttribute('data-fecha'));
    });
  }

  var params = new URLSearchParams(window.location.search);
  if (params.get('desde')) inpInicio.value = params.get('desde');
  if (params.get('hasta')) inpFin.value = params.get('hasta');

  sincronizarMes();
  actualizar();

  document.querySelectorAll('.sitio-galeria-thumb').forEach(function (thumb) {
    thumb.addEventListener('click', function () {
      var main = document.getElementById('galeriaMain');
      if (main) main.src = thumb.dataset.src;
      document.querySelectorAll('.sitio-galeria-thumb').forEach(function (t) {
        t.classList.remove('is-active');
      });
      thumb.classList.add('is-active');
    });
  });
})();
