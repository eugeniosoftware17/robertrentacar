document.addEventListener('DOMContentLoaded', function () {
  var form = document.getElementById('vehiculosBuscarForm');
  var input = form && form.querySelector('input[name="q"]');
  if (!form || !input) return;

  var timer = null;
  input.addEventListener('input', function () {
    clearTimeout(timer);
    timer = setTimeout(function () {
      form.requestSubmit();
    }, 350);
  });

  if (!input.value) {
    input.focus();
  }
});
