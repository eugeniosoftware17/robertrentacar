(function () {
  var toggle = document.getElementById('navToggle');
  var nav = document.getElementById('sitioNav');
  if (toggle && nav) {
    toggle.addEventListener('click', function () {
      nav.classList.toggle('is-open');
    });
  }
})();
