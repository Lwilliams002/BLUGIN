// Blu Gin — hero slider, signature plates carousel, mobile nav, live hours, reveals.

// Live hours in Miami time.
(() => {
  const el = document.getElementById('live');
  if (!el) return;
  const OPEN = 8 * 60 + 30, CLOSE = 24 * 60;
  const fmt = new Intl.DateTimeFormat('en-US', { timeZone: 'America/New_York', hour: 'numeric', minute: 'numeric', hour12: false });
  const now = () => { const p = fmt.formatToParts(new Date()); return (Number(p.find((x) => x.type === 'hour').value) % 24) * 60 + Number(p.find((x) => x.type === 'minute').value); };
  const span = (m) => { const h = Math.floor(m / 60), r = m % 60; return h === 0 ? `${r} min` : r === 0 ? `${h} h` : `${h} h ${r} min`; };
  const render = () => {
    const t = now();
    if (t >= OPEN && t < CLOSE) { el.dataset.state = 'open'; el.textContent = `Open now · ${span(CLOSE - t)} until midnight`; }
    else { el.dataset.state = 'closed'; el.textContent = `Closed now · opens at 8:30 am`; }
  };
  try { render(); setInterval(render, 30000); } catch (e) {}
})();

// Mobile navigation.
(() => {
  const btn = document.querySelector('.nav-toggle'), nav = document.getElementById('mobile-nav');
  if (!btn || !nav) return;
  btn.addEventListener('click', () => { const open = nav.classList.toggle('is-open'); btn.setAttribute('aria-expanded', String(open)); btn.setAttribute('aria-label', open ? 'Close the menu' : 'Open the menu'); });
  nav.querySelectorAll('a').forEach((a) => a.addEventListener('click', () => { nav.classList.remove('is-open'); btn.setAttribute('aria-expanded', 'false'); }));
})();

// Hero slider.
(() => {
  const slides = [...document.querySelectorAll('#hero-slides .slide')];
  if (!slides.length) return;
  const thumbs = [...document.querySelectorAll('.thumbs button')];
  let i = 0, timer;
  const show = (n) => {
    i = (n + slides.length) % slides.length;
    slides.forEach((s, k) => s.classList.toggle('is-active', k === i));
    thumbs.forEach((t, k) => t.setAttribute('aria-selected', String(k === i)));
  };
  const auto = () => { clearInterval(timer); if (!matchMedia('(prefers-reduced-motion: reduce)').matches) timer = setInterval(() => show(i + 1), 6000); };
  document.querySelectorAll('.hero .arrow').forEach((b) => b.addEventListener('click', () => { show(i + Number(b.dataset.dir)); auto(); }));
  thumbs.forEach((t) => t.addEventListener('click', () => { show(Number(t.dataset.go)); auto(); }));
  auto();
})();

// Signature plates carousel, with direction-aware slide transitions.
(() => {
  const root = document.getElementById('specials-carousel');
  if (!root) return;
  const plates = [
    { img: 'assets/img/web/whole-snapper.jpg', name: 'Whole Florida<br>snapper for two', price: '$59.99', desc: 'Florida caught, deep fried whole under lemon and rosemary, with two sides to share.' },
    { img: 'assets/img/web/lobster-paella.jpg', name: 'Seafood<br>paella', price: '$32.99', desc: 'Cuban style. Yellow rice loaded with mussels, shrimp, calamari and peas, finished on the line.' },
    { img: 'assets/img/web/shrimp-tower.jpg', name: 'Surf and turf<br>mignon', price: '$47.00', desc: 'A thick tenderloin filet topped with jumbo shrimp. Mushroom gravy or blue cheese on the side.' },
    { img: 'assets/img/web/steak-medallions.jpg', name: 'Skirt steak<br>churrasco', price: '$35.00', desc: 'Argentine cut on the grill, topped with the house chimichurri.' },
    { img: 'assets/img/web/mussels.jpg', name: 'Spaghetti<br>frutti di mare', price: '$28.99', desc: 'Mussels, shrimp and calamari over spaghetti in a homemade marinara.' },
    { img: 'assets/img/web/garlic-shrimp.jpg', name: 'Garlic<br>shrimp', price: '$23.99', desc: 'The hearty choice: jumbo shrimp in olive oil and garlic.' },
  ];
  plates.forEach((p) => { const im = new Image(); im.src = p.img; });
  const main = root.querySelector('.arch-img'), name = root.querySelector('.arch-name'), price = root.querySelector('.price-badge');
  const desc = document.getElementById('special-desc'), idx = document.getElementById('special-i'), n = document.getElementById('special-n');
  const prev = root.querySelector('.side-prev img'), next = root.querySelector('.side-next img');
  const moving = [main, name, price, desc];
  const calm = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const EASE = 'cubic-bezier(0.22, 1, 0.36, 1)';
  let i = 0, busy = false, timer;
  n.textContent = plates.length;

  const fill = (p) => {
    main.src = p.img; main.alt = p.name.replace('<br>', ' ');
    name.innerHTML = p.name; price.textContent = p.price; desc.textContent = p.desc; idx.textContent = i + 1;
    prev.src = plates[(i - 1 + plates.length) % plates.length].img; next.src = plates[(i + 1) % plates.length].img;
  };

  // Sequenced by timers rather than animation promises, so the content always swaps even when animations are throttled.
  const show = (k, dir = 1) => {
    if (busy) return;
    i = (k + plates.length) % plates.length;
    const p = plates[i];
    if (calm || !main.animate) { fill(p); return; }
    busy = true;
    const outX = -70 * dir, inX = 90 * dir, rot = 6 * dir;
    const outs = moving.map((el, j) => el.animate(
      [{ transform: 'translateX(0) rotate(0deg)', opacity: 1 }, { transform: `translateX(${outX}px) rotate(${el === main ? -rot : 0}deg)`, opacity: 0 }],
      { duration: 300, delay: j * 40, easing: EASE, fill: 'forwards' }));
    [prev, next].forEach((el) => el.classList.add('is-dim'));
    setTimeout(() => {
      fill(p);
      outs.forEach((a) => a.cancel());
      moving.forEach((el, j) => el.animate(
        [{ transform: `translateX(${inX}px) rotate(${el === main ? rot : 0}deg)`, opacity: 0 }, { transform: 'translateX(0) rotate(0deg)', opacity: 1 }],
        { duration: 520, delay: j * 50, easing: EASE }));
      [prev, next].forEach((el) => el.classList.remove('is-dim'));
      setTimeout(() => { busy = false; }, 700);
    }, 440);
  };

  const auto = () => { clearInterval(timer); if (!calm) timer = setInterval(() => show(i + 1, 1), 5000); };
  root.querySelectorAll('.arch-arrows button').forEach((b) => b.addEventListener('click', () => { const d = Number(b.dataset.dir); show(i + d, d); auto(); }));
  root.addEventListener('mouseenter', () => clearInterval(timer));
  root.addEventListener('mouseleave', auto);
  root.addEventListener('focusin', () => clearInterval(timer));
  root.addEventListener('focusout', auto);
  let x0 = null;
  root.addEventListener('touchstart', (e) => { x0 = e.touches[0].clientX; }, { passive: true });
  root.addEventListener('touchend', (e) => { if (x0 === null) return; const dx = e.changedTouches[0].clientX - x0; x0 = null; if (Math.abs(dx) > 40) { const d = dx < 0 ? 1 : -1; show(i + d, d); auto(); } }, { passive: true });
  fill(plates[0]); auto();
})();

// Reveal sections once as they enter the viewport.
(() => {
  const targets = document.querySelectorAll('[data-reveal]');
  if (!targets.length || !('IntersectionObserver' in window)) { targets.forEach((el) => el.classList.add('is-in')); return; }
  const io = new IntersectionObserver((entries) => { for (const e of entries) if (e.isIntersecting) { e.target.classList.add('is-in'); io.unobserve(e.target); } }, { rootMargin: '0px 0px -8% 0px', threshold: 0.05 });
  targets.forEach((el) => io.observe(el));
})();
