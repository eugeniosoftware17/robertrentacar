// Vehículos — JS del módulo
document.addEventListener('DOMContentLoaded', function () {
  var buscar = document.querySelector('.mod-buscar input[name="q"]');
  if (buscar && !buscar.value) {
    buscar.focus();
  }
});
