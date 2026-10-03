(function(){
  var m = /[?&]error=([a-z_]+)/.exec(location.search); if (!m) return;
  var el = document.querySelector('[data-error="' + m[1] + '"]');
  if (el) { el.hidden = false; el.scrollIntoView({block: 'center'}); }
})();
