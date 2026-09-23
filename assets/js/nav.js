(function () {
  var toggle = document.querySelector('.nav-toggle');
  var nav = document.getElementById('site-nav');
  if (toggle && nav) {
    toggle.addEventListener('click', function () {
      var open = nav.classList.toggle('open');
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
  }
  var subs = document.querySelectorAll('.sub-toggle');
  for (var i = 0; i < subs.length; i++) {
    subs[i].addEventListener('click', function (e) { e.preventDefault(); this.parentNode.classList.toggle('sub-open'); });
  }
  var top = document.querySelector('.to-top');
  if (top) {
    top.addEventListener('click', function (e) { e.preventDefault(); window.scrollTo({ top: 0, behavior: 'smooth' }); });
    window.addEventListener('scroll', function () { top.classList.toggle('show', window.scrollY > 400); });
  }
  // 홈 히어로 슬라이더
  var hero = document.querySelector('.hero');
  if (hero) {
    var slides = hero.querySelectorAll('.slide');
    var dots = hero.querySelectorAll('.dot');
    var cap = document.getElementById('hero-caption');
    var idx = 0, timer;
    function show(n) {
      idx = (n + slides.length) % slides.length;
      for (var j = 0; j < slides.length; j++) {
        slides[j].classList.toggle('on', j === idx);
        if (dots[j]) dots[j].classList.toggle('on', j === idx);
        var v = slides[j].querySelector('video');
        if (v) { if (j === idx) { v.play && v.play().catch(function(){}); } else { v.pause && v.pause(); } }
      }
      if (cap) cap.textContent = slides[idx].getAttribute('data-caption') || '';
    }
    function start() { timer = setInterval(function () { show(idx + 1); }, 5000); }
    function stop() { clearInterval(timer); }
    hero.querySelector('.prev').addEventListener('click', function () { stop(); show(idx - 1); start(); });
    hero.querySelector('.next').addEventListener('click', function () { stop(); show(idx + 1); start(); });
    for (var k = 0; k < dots.length; k++) {
      (function (n) { dots[n].addEventListener('click', function () { stop(); show(n); start(); }); })(k);
    }
    show(0); start();
  }
})();
