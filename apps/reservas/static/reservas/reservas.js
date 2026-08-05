// Reservas — cálculo de precio y calendario de disponibilidad
document.addEventListener('DOMContentLoaded', function () {
  var buscar = document.querySelector('.mod-buscar input[name="q"]');
  if (buscar && !buscar.value) {
    buscar.focus();
  }

  var tarifasNode = document.getElementById('reservas-tarifas-data');
  var panel = document.getElementById('reserva-precio-panel');
  if (!tarifasNode || !panel) return;

  var tarifas = JSON.parse(tarifasNode.textContent);
  var ocupacionNode = document.getElementById('reservas-ocupacion-data');
  var ocupacion = ocupacionNode ? JSON.parse(ocupacionNode.textContent) : {};

  var vehiculo = document.getElementById('id_vehiculo');
  var inicio = document.getElementById('id_fecha_inicio');
  var fin = document.getElementById('id_fecha_fin');
  var deposito = document.getElementById('id_deposito');

  var calGrid = document.getElementById('reserva-cal-grid');
  var calTitulo = document.getElementById('reserva-cal-titulo');
  var calSub = document.getElementById('reserva-cal-sub');
  var calAlerta = document.getElementById('reserva-cal-alerta');
  var calBloques = document.getElementById('reserva-cal-bloques');
  var submitBtn = document.getElementById('reserva-submit-btn');

  var MESES = [
    '', 'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
    'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
  ];

  var calAnio, calMes;

  function fmt(n) {
    return 'RD$ ' + Math.round(n).toLocaleString('es-DO');
  }

  function calcularDias(fi, ff) {
    if (!fi || !ff) return 0;
    var d1 = new Date(fi + 'T00:00:00');
    var d2 = new Date(ff + 'T00:00:00');
    if (d2 < d1) return 0;
    return Math.round((d2 - d1) / 86400000) + 1;
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

  function isoLocal(d) {
    return d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0') + '-' + String(d.getDate()).padStart(2, '0');
  }

  function rangoSeleccionado(fi, ff) {
    var dias = [];
    if (!fi || !ff) return dias;
    var d1 = new Date(fi + 'T00:00:00');
    var d2 = new Date(ff + 'T00:00:00');
    if (d2 < d1) return dias;
    var cur = new Date(d1);
    while (cur <= d2) {
      dias.push(isoLocal(cur));
      cur.setDate(cur.getDate() + 1);
    }
    return dias;
  }

  function datosVehiculo() {
    var vid = vehiculo ? vehiculo.value : '';
    if (!vid || !ocupacion[vid]) {
      return { dias: [], bloques: [] };
    }
    return ocupacion[vid];
  }

  function hayConflicto() {
    var info = datosVehiculo();
    var seleccion = rangoSeleccionado(
      inicio ? inicio.value : '',
      fin ? fin.value : ''
    );
    if (!seleccion.length) return false;
    return seleccion.some(function (d) {
      return info.dias.indexOf(d) !== -1;
    });
  }

  function actualizarPrecio() {
    var vid = vehiculo ? vehiculo.value : '';
    var tarifa = tarifas[vid] || 0;
    var dias = calcularDias(inicio ? inicio.value : '', fin ? fin.value : '');
    var total = tarifa * Math.max(dias, dias > 0 ? 1 : 0);
    var dep = deposito ? parseFloat(deposito.value) || 0 : 0;
    var saldo = Math.max(total - dep, 0);

    document.getElementById('rp-dias').textContent = dias > 0 ? dias : '—';
    document.getElementById('rp-tarifa').textContent = tarifa ? fmt(tarifa) + '/día' : '—';
    document.getElementById('rp-total').textContent = total > 0 ? fmt(total) : '—';
    document.getElementById('rp-deposito').textContent = dep > 0 ? fmt(dep) : 'RD$ 0';
    document.getElementById('rp-saldo').textContent = total > 0 ? fmt(saldo) : '—';
  }

  function renderBloques() {
    if (!calBloques) return;
    var info = datosVehiculo();
    if (!info.bloques.length) {
      calBloques.innerHTML = '';
      return;
    }
    calBloques.innerHTML = info.bloques.map(function (b) {
      return (
        '<li><strong>#' + b.id + '</strong> ' + b.cliente +
        '<span>' + b.inicio + ' → ' + b.fin + '</span></li>'
      );
    }).join('');
  }

  function renderCalendario() {
    if (!calGrid) return;

    calTitulo.textContent = MESES[calMes] + ' ' + calAnio;

    var vid = vehiculo ? vehiculo.value : '';
    var info = datosVehiculo();
    var seleccion = rangoSeleccionado(
      inicio ? inicio.value : '',
      fin ? fin.value : ''
    );
    var conflicto = hayConflicto();

    if (!vid) {
      calSub.textContent = 'Selecciona un vehículo para ver sus días ocupados';
    } else {
      var label = vehiculo.options[vehiculo.selectedIndex].text;
      calSub.textContent = label + ' · ' + info.dias.length + ' día' + (info.dias.length === 1 ? '' : 's') + ' ocupado' + (info.dias.length === 1 ? '' : 's');
    }

    if (calAlerta) {
      if (conflicto) {
        calAlerta.hidden = false;
        calAlerta.textContent = '⚠ Las fechas seleccionadas chocan con otra reserva de este vehículo.';
      } else {
        calAlerta.hidden = true;
        calAlerta.textContent = '';
      }
    }

    if (submitBtn) {
      submitBtn.disabled = conflicto;
      submitBtn.title = conflicto ? 'Hay conflicto de fechas con otra reserva' : '';
    }

    var totalDias = diasEnMes(calAnio, calMes);
    var offset = primerDiaSemana(calAnio, calMes);
    var hoy = isoLocal(new Date());
    var html = '';

    for (var i = 0; i < offset; i++) {
      html += '<div class="reserva-cal-dia vacio"></div>';
    }

    for (var dia = 1; dia <= totalDias; dia++) {
      var iso = isoDesdePartes(calAnio, calMes, dia);
      var clases = ['reserva-cal-dia'];

      if (info.dias.indexOf(iso) !== -1) clases.push('ocupado');
      if (seleccion.indexOf(iso) !== -1) clases.push('seleccion');
      if (info.dias.indexOf(iso) !== -1 && seleccion.indexOf(iso) !== -1) {
        clases.push('conflicto');
      }
      if (iso === hoy) clases.push('hoy');

      html += '<div class="' + clases.join(' ') + '" data-fecha="' + iso + '" title="' + iso + '">' + dia + '</div>';
    }

    calGrid.innerHTML = html;
    renderBloques();
  }

  function irAMes(anio, mes) {
    calAnio = anio;
    calMes = mes;
    renderCalendario();
  }

  function sincronizarMesConFechas() {
    var ref = (inicio && inicio.value) || (fin && fin.value);
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

  function actualizarTodo() {
    actualizarPrecio();
    renderCalendario();
  }

  sincronizarMesConFechas();
  actualizarTodo();

  [vehiculo, inicio, fin, deposito].forEach(function (el) {
    if (!el) return;
    el.addEventListener('change', function () {
      if (el === inicio || el === fin) sincronizarMesConFechas();
      actualizarTodo();
    });
    el.addEventListener('input', actualizarTodo);
  });

  var btnPrev = document.getElementById('reserva-cal-prev');
  var btnNext = document.getElementById('reserva-cal-next');

  if (btnPrev) {
    btnPrev.addEventListener('click', function () {
      if (calMes === 1) irAMes(calAnio - 1, 12);
      else irAMes(calAnio, calMes - 1);
    });
  }

  if (btnNext) {
    btnNext.addEventListener('click', function () {
      if (calMes === 12) irAMes(calAnio + 1, 12);
      else irAMes(calAnio, calMes + 1);
    });
  }

  if (calGrid) {
    calGrid.addEventListener('click', function (e) {
      var celda = e.target.closest('.reserva-cal-dia[data-fecha]');
      if (!celda) return;
      var fecha = celda.getAttribute('data-fecha');
      if (!inicio || !fin) return;

      if (!inicio.value || (inicio.value && fin.value)) {
        inicio.value = fecha;
        fin.value = fecha;
      } else if (fecha >= inicio.value) {
        fin.value = fecha;
      } else {
        inicio.value = fecha;
        fin.value = fecha;
      }
      actualizarTodo();
    });
  }
});
