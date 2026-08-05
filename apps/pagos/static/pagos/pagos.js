// Pagos — resumen financiero de la reserva seleccionada
document.addEventListener('DOMContentLoaded', function () {
  var dataNode = document.getElementById('pagos-reservas-data');
  var panel = document.getElementById('pago-resumen-panel');
  var select = document.getElementById('id_reserva_pago');
  var monto = document.getElementById('id_monto_pago');
  var tipo = document.getElementById('id_tipo_pago');

  if (!dataNode || !panel || !select) return;

  var reservas = JSON.parse(dataNode.textContent);

  function fmt(n) {
    return 'RD$ ' + Math.round(n).toLocaleString('es-DO');
  }

  function actualizar() {
    var info = reservas[select.value];
    if (!info) {
      panel.style.display = 'none';
      return;
    }

    panel.style.display = 'block';
    document.getElementById('pr-cliente').textContent = info.cliente;
    document.getElementById('pr-vehiculo').textContent = info.vehiculo + ' · ' + info.placa;
    document.getElementById('pr-dias').textContent = info.dias + ' día' + (info.dias === 1 ? '' : 's');
    document.getElementById('pr-total').textContent = fmt(info.precio_total);
    document.getElementById('pr-pagado').textContent = fmt(info.total_pagado);
    document.getElementById('pr-saldo').textContent = fmt(info.saldo_pendiente);
    document.getElementById('pr-estado').textContent = info.estado_pago_label;
    document.getElementById('pr-estado').className = 'pago-estado pago-estado-' + info.estado_pago;

    if (monto && !monto.value && info.saldo_pendiente > 0 && tipo) {
      if (tipo.value === 'deposito' || tipo.value === 'parcial') {
        monto.placeholder = 'Saldo: ' + fmt(info.saldo_pendiente);
      }
    }
  }

  select.addEventListener('change', actualizar);
  if (tipo) tipo.addEventListener('change', actualizar);
  actualizar();
});
