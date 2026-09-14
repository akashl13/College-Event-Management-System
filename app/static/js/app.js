document.addEventListener('DOMContentLoaded', () => {
  document.body.classList.add('page-ready');
  const root = document.documentElement;
  const nav = document.querySelector('.campus-nav');
  const toggle = document.querySelector('.theme-toggle');
  const navToggle = document.querySelector('.nav-toggle');
  const storedTheme = localStorage.getItem('event-campus-theme');
  const systemTheme = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  root.dataset.theme = storedTheme || systemTheme;
  const updateThemeButton = () => {
    if (!toggle) return;
    const dark = root.dataset.theme === 'dark';
    toggle.setAttribute('aria-pressed', String(dark));
    toggle.setAttribute('aria-label', dark ? 'Enable light theme' : 'Enable dark theme');
    toggle.textContent = dark ? '☼' : '◐';
  };
  updateThemeButton();
  toggle?.addEventListener('click', () => {
    root.dataset.theme = root.dataset.theme === 'light' ? 'dark' : 'light';
    localStorage.setItem('event-campus-theme', root.dataset.theme);
    updateThemeButton();
  });
  navToggle?.addEventListener('click', () => {
    const open = nav.classList.toggle('menu-open');
    navToggle.setAttribute('aria-expanded', String(open));
  });
  nav?.querySelectorAll('a').forEach(link => link.addEventListener('click', () => {
    nav.classList.remove('menu-open');
    navToggle?.setAttribute('aria-expanded', 'false');
  }));
  document.addEventListener('keydown', event => {
    if (event.key === 'Escape') {
      nav?.classList.remove('menu-open');
      navToggle?.setAttribute('aria-expanded', 'false');
    }
  });
  const updateNav = () => nav?.classList.toggle('scrolled', window.scrollY > 30);
  updateNav();
  window.addEventListener('scroll', updateNav, { passive: true });

  document.querySelectorAll('form').forEach(form => form.addEventListener('submit', () => {
    const button = form.querySelector('button[type="submit"], button:not([data-bs-dismiss])');
    if (button && form.checkValidity()) { button.disabled = true; button.dataset.originalText = button.textContent; button.textContent = 'Working...'; }
  }));
  document.querySelectorAll('.tilt-card').forEach(card => {
    card.addEventListener('pointermove', event => {
      if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
      const box = card.getBoundingClientRect();
      const rotateX = ((event.clientY - box.top) / box.height - .5) * -5;
      const rotateY = ((event.clientX - box.left) / box.width - .5) * 5;
      card.style.transform = `perspective(900px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateY(-5px)`;
    });
    card.addEventListener('pointerleave', () => { card.style.transform = ''; });
  });
  document.querySelectorAll('.magnetic').forEach(button => {
    button.addEventListener('pointermove', event => {
      if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
      const box = button.getBoundingClientRect();
      const x = (event.clientX - box.left - box.width / 2) * .08;
      const y = (event.clientY - box.top - box.height / 2) * .08;
      button.style.transform = `translate(${x}px, ${y}px)`;
    });
    button.addEventListener('pointerleave', () => { button.style.transform = ''; });
  });
  if (window.gsap) {
    if (window.ScrollTrigger) gsap.registerPlugin(ScrollTrigger);
    gsap.from('.hero-copy > *', { opacity: 0, y: 24, duration: .8, stagger: .08, ease: 'power3.out' });
    gsap.from('.location-card', { opacity: 0, y: 20, duration: .7, stagger: .08, delay: .35, ease: 'power2.out' });
    gsap.from('.category-card, .campus-event-card', { opacity: 0, y: 18, duration: .6, stagger: .05, scrollTrigger: { trigger: '.category-section', start: 'top 80%' } });
  }
  initCountdown();
  initTimeline();
  if (document.querySelector('#campus-canvas') && window.THREE) initCampusScene();
});

function initCountdown() {
  const section = document.querySelector('[data-countdown]');
  if (!section || !section.dataset.countdown) return;
  const target = new Date(`${section.dataset.countdown}T00:00:00`).getTime();
  const tick = () => {
    const distance = Math.max(0, target - Date.now());
    const values = { days: Math.floor(distance / 86400000), hours: Math.floor(distance / 3600000) % 24, minutes: Math.floor(distance / 60000) % 60, seconds: Math.floor(distance / 1000) % 60 };
    Object.entries(values).forEach(([key, value]) => { const element = section.querySelector(`[data-count="${key}"]`); if (element) element.textContent = String(value).padStart(2, '0'); });
  };
  tick();
  window.setInterval(tick, 1000);
}

function initTimeline() {
  const filters = document.querySelectorAll('.timeline-filter');
  const cards = document.querySelectorAll('.campus-event-card[data-date]');
  if (!filters.length || !cards.length) return;
  filters.forEach(filter => filter.addEventListener('click', () => {
    filters.forEach(item => item.classList.remove('active'));
    filter.classList.add('active');
    const windowName = filter.dataset.window;
    const now = new Date(); now.setHours(0, 0, 0, 0);
    cards.forEach(card => {
      const eventDate = new Date(`${card.dataset.date}T00:00:00`);
      const days = Math.round((eventDate - now) / 86400000);
      const visible = windowName === 'all' || (windowName === 'today' && days === 0) || (windowName === 'week' && days >= 0 && days <= 7) || (windowName === 'month' && days >= 0 && days <= 31);
      card.style.display = visible ? '' : 'none';
      if (visible && window.gsap) gsap.fromTo(card, { opacity: 0, y: 10 }, { opacity: 1, y: 0, duration: .3 });
    });
  }));
}

function initCampusScene() {
  const canvas = document.querySelector('#campus-canvas');
  const host = document.querySelector('#campus-scene');
  const scene = new THREE.Scene();
  scene.fog = new THREE.Fog(0x080b12, 18, 42);
  const camera = new THREE.PerspectiveCamera(34, host.clientWidth / host.clientHeight, .1, 100);
  camera.position.set(0, 10, 22);
  const renderer = new THREE.WebGLRenderer({ canvas, alpha: true, antialias: true });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 1.7));
  renderer.setSize(host.clientWidth, host.clientHeight, false);
  const campus = new THREE.Group();
  scene.add(campus);
  scene.add(new THREE.HemisphereLight(0xa7c5ff, 0x0b1018, 2));
  const key = new THREE.DirectionalLight(0xd6ff5f, 2.8); key.position.set(-8, 14, 8); scene.add(key);
  const ground = new THREE.Mesh(new THREE.CylinderGeometry(11, 12, .3, 64), new THREE.MeshStandardMaterial({ color: 0x111925, roughness: .9 }));
  ground.position.y = -1; campus.add(ground);
  const roadMaterial = new THREE.MeshBasicMaterial({ color: 0x26334a });
  [[0, 0, 2, 20], [0, 0, 20, 2], [-6, 0, 10, 2], [6, 0, 10, 2]].forEach(([x, y, sx, sz]) => { const road = new THREE.Mesh(new THREE.BoxGeometry(sx, .08, sz), roadMaterial); road.position.set(x, y-.8, sz > sx ? 0 : 0); campus.add(road); });
  const buildings = [
    [-6, 1.2, -3, 4, 2.4, 3.5, 0x9b7bff], [0, 1.8, -4, 5, 3.6, 3, 0x6de7ff], [6, 1, -2, 3.5, 2, 4, 0xd6ff5f],
    [-5, .8, 4, 4, 1.6, 3, 0xff8f72], [2, 1.5, 4, 5, 3, 3, 0x8290ff], [7, .7, 4, 3, 1.4, 3.5, 0x6de7ff]
  ];
  buildings.forEach(([x, y, z, sx, sy, sz, color]) => {
    const group = new THREE.Group();
    const body = new THREE.Mesh(new THREE.BoxGeometry(sx, sy, sz), new THREE.MeshStandardMaterial({ color: 0x1b2638, roughness: .65, metalness: .15 }));
    body.position.y = sy / 2; group.add(body);
    const light = new THREE.Mesh(new THREE.BoxGeometry(sx * .7, .08, sz * .65), new THREE.MeshBasicMaterial({ color })); light.position.y = sy + .04; group.add(light);
    group.position.set(x, y - 1, z); campus.add(group);
  });
  for (let i = 0; i < 18; i += 1) {
    const tree = new THREE.Group();
    const trunk = new THREE.Mesh(new THREE.CylinderGeometry(.08, .12, .7, 6), new THREE.MeshBasicMaterial({ color: 0x7c6858 })); trunk.position.y = -.45; tree.add(trunk);
    const crown = new THREE.Mesh(new THREE.IcosahedronGeometry(.55, 1), new THREE.MeshStandardMaterial({ color: 0x385c56, roughness: 1 })); tree.add(crown);
    const angle = i * 2.4; tree.position.set(Math.cos(angle) * (7 + i % 3), -.2, Math.sin(angle) * (7 + i % 3)); campus.add(tree);
  }
  let pointerX = 0, pointerY = 0;
  host.addEventListener('pointermove', event => { pointerX = (event.clientX / window.innerWidth - .5) * .8; pointerY = (event.clientY / window.innerHeight - .5) * .35; });
  const resize = () => { camera.aspect = host.clientWidth / host.clientHeight; camera.updateProjectionMatrix(); renderer.setSize(host.clientWidth, host.clientHeight, false); };
  window.addEventListener('resize', resize);
  const clock = new THREE.Clock();
  const animate = () => { const t = clock.getElapsedTime(); campus.rotation.y += (pointerX * .12 - campus.rotation.y) * .025; campus.rotation.x += (-pointerY * .08 - campus.rotation.x) * .025; campus.position.y = Math.sin(t * .5) * .12; renderer.render(scene, camera); requestAnimationFrame(animate); };
  animate();
}
