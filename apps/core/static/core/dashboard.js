// Dashboard — Gráfica de barras con datos del servidor
document.addEventListener('DOMContentLoaded', function () {
  var datosNode = document.getElementById('grafica-datos');
  var contenedor = document.getElementById('graficaBarras');

  if (!datosNode || !contenedor) return;

  var datos = JSON.parse(datosNode.textContent);
  if (!datos.length) {
    contenedor.innerHTML = '<div class="dash-vacio">Sin datos de ingresos todavía.</div>';
    return;
  }

  var maximo = Math.max.apply(null, datos.map(function (d) { return d.valor; })) || 1;

  datos.forEach(function (d, i) {
    var altura = maximo > 0 ? (d.valor / maximo) * 150 : 0;
    var col = document.createElement('div');
    col.className = 'dash-barra-col';
    col.innerHTML =
      '<div class="dash-barra" style="height:' + altura + 'px; animation-delay:' + (i * 60) + 'ms" title="USD$ ' + (d.valor * 1000).toLocaleString('es-DO') + '"></div>' +
      '<div class="dash-barra-mes">' + d.mes + '</div>';
    contenedor.appendChild(col);
  });
});
