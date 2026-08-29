(function () {
  // Oculta el botón flotante de WhatsApp mientras el usuario interactúa
  // con algún campo del formulario, para que nunca tape un campo.
  var form = document.querySelector('.sitio-form');
  var wa = document.querySelector('.sitio-wa-flotante');
  if (form && wa) {
    form.addEventListener('focusin', function () {
      wa.classList.add('sitio-wa-flotante--oculto');
    });
    form.addEventListener('focusout', function () {
      wa.classList.remove('sitio-wa-flotante--oculto');
    });
  }

  // Resumen de precio dinámico según las fechas elegidas.
  var inpInicio = document.getElementById('id_fecha_inicio');
  var inpFin = document.getElementById('id_fecha_fin');
  var totalEl = document.getElementById('reservaTotalEstimado');
  if (!inpInicio || !inpFin || !totalEl) return;

  var tarifa = parseFloat(window.SITIO_TARIFA_DIA) || 0;
  var plantilla = window.SITIO_TEXTO_PRECIO_TPL || '';

  function parseDate(valor) {
    if (!valor) return null;
    var partes = valor.split('-');
    if (partes.length !== 3) return null;
    var fecha = new Date(Number(partes[0]), Number(partes[1]) - 1, Number(partes[2]));
    return isNaN(fecha.getTime()) ? null : fecha;
  }

  function formatoMoneda(numero) {
    return numero.toLocaleString('es-DO', { maximumFractionDigits: 0 });
  }

  function actualizarTotal() {
    var inicio = parseDate(inpInicio.value);
    var fin = parseDate(inpFin.value);
    if (!inicio || !fin || fin < inicio) {
      totalEl.textContent = '';
      return;
    }
    var dias = Math.round((fin - inicio) / 86400000) + 1;
    var total = dias * tarifa;
    var texto = plantilla
      .replace('__TARIFA__', formatoMoneda(tarifa))
      .replace('__TOTAL__', formatoMoneda(total));
    totalEl.textContent = dias + ' ' + texto;
  }

  inpInicio.addEventListener('change', actualizarTotal);
  inpFin.addEventListener('change', actualizarTotal);
  actualizarTotal();
})();
