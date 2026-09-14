document.addEventListener('DOMContentLoaded', () => {
  document.body.classList.add('page-ready');
  const nav = document.querySelector('.site-nav');
  const navToggle = document.querySelector('.nav-toggle');
  navToggle?.addEventListener('click', () => {
    const open = nav.classList.toggle('menu-open');
    navToggle.setAttribute('aria-expanded', String(open));
    navToggle.setAttribute('aria-label', open ? 'Close navigation' : 'Open navigation');
  });
  nav?.querySelectorAll('.nav-links a').forEach(link => link.addEventListener('click', () => {
    nav.classList.remove('menu-open');
    navToggle?.setAttribute('aria-expanded', 'false');
  }));
  document.addEventListener('keydown', event => {
    if (event.key === 'Escape') {
      nav?.classList.remove('menu-open');
      navToggle?.setAttribute('aria-expanded', 'false');
    }
  });
  document.querySelectorAll('form').forEach(form => form.addEventListener('submit', () => {
    const button = form.querySelector('button[type="submit"]');
    if (button && form.checkValidity()) {
      button.disabled = true;
      button.dataset.originalText = button.textContent;
      button.textContent = 'Working...';
      button.classList.add('is-loading');
    }
  }));
  initTimelineFilters();
  initCampusMap();
  initAnimations();
});

function initAnimations() {
  if (!window.gsap || window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  if (window.ScrollTrigger) gsap.registerPlugin(ScrollTrigger);
  gsap.from('.hero-home > *, .events-top > *, .detail-hero > *, .dashboard-head > *', { opacity: 0, y: 20, duration: .65, stagger: .08, ease: 'power3.out' });
  document.querySelectorAll('.event-card, .editorial-item, .metric').forEach((item, index) => {
    gsap.from(item, { opacity: 0, y: 16, duration: .5, delay: index * .06, ease: 'power3.out', scrollTrigger: { trigger: item, start: 'top 90%', once: true } });
  });
}

function initTimelineFilters() {
  const filters = document.querySelectorAll('.timeline-filter');
  const cards = document.querySelectorAll('.campus-event-card[data-date]');
  if (!filters.length || !cards.length) return;
  filters.forEach(filter => filter.addEventListener('click', () => {
    filters.forEach(item => item.classList.remove('active'));
    filter.classList.add('active');
    const windowName = filter.dataset.window;
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    cards.forEach(card => {
      const eventDate = new Date(`${card.dataset.date}T00:00:00`);
      const days = Math.round((eventDate - today) / 86400000);
      const visible = windowName === 'all' || (windowName === 'today' && days === 0) || (windowName === 'week' && days >= 0 && days <= 7) || (windowName === 'month' && days >= 0 && days <= 31);
      card.hidden = !visible;
      if (visible && window.gsap) gsap.fromTo(card, { opacity: 0, y: 8 }, { opacity: 1, y: 0, duration: .3 });
    });
  }));
}

function initCampusMap() {
  const page = document.querySelector('.directory-page');
  if (!page) return;
  const map = document.querySelector('#campus-map');
  const panelTitle = document.querySelector('#location-title');
  const panelCount = document.querySelector('#location-count');
  const nextTitle = document.querySelector('#next-event-title');
  const nextMeta = document.querySelector('#next-event-meta');
  const eventLink = document.querySelector('#location-events-link');
  const status = document.querySelector('#map-status');
  const venueNames = [...document.querySelectorAll('.map-building')].map(item => item.dataset.location);
  const venueEvents = {};
  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const selectLocation = name => {
    const records = venueEvents[name] || [];
    document.querySelectorAll('.map-building').forEach(item => item.classList.toggle('selected', item.dataset.location === name));
    panelTitle.textContent = name;
    panelCount.textContent = records.length;
    const next = records[0];
    nextTitle.textContent = next ? next.title : 'No event scheduled';
    nextMeta.textContent = next ? `${next.date} · ${next.time}` : 'Check back soon';
    eventLink.href = `/events${next?.category ? `?category=${encodeURIComponent(next.category)}` : ''}`;
    status.textContent = name.toUpperCase();
    if (window.gsap && !reduceMotion) gsap.fromTo('.location-panel', { opacity: .6, y: 8 }, { opacity: 1, y: 0, duration: .35, ease: 'power3.out' });
  };
  const setup = events => {
    venueNames.forEach(name => { venueEvents[name] = events.filter(event => event.venue.toLowerCase().includes(name.toLowerCase())); });
    document.querySelectorAll('.map-building, .event-marker, .venue-row').forEach(item => {
      item.addEventListener('click', () => selectLocation(item.dataset.location));
      item.addEventListener('keydown', event => { if (event.key === 'Enter' || event.key === ' ') { event.preventDefault(); selectLocation(item.dataset.location); } });
    });
    document.querySelectorAll('.map-filter').forEach(filter => filter.addEventListener('click', () => {
      document.querySelectorAll('.map-filter').forEach(button => button.classList.remove('active'));
      filter.classList.add('active');
      const value = filter.dataset.filter;
      document.querySelectorAll('.event-marker').forEach(marker => { marker.hidden = value !== 'all' && value !== 'venue' && marker.dataset.category !== value; });
      status.textContent = value === 'all' ? 'ALL LOCATIONS' : value.toUpperCase();
    }));
    document.querySelector('#map-zoom-in')?.addEventListener('click', () => zoomMap(1.1));
    document.querySelector('#map-zoom-out')?.addEventListener('click', () => zoomMap(.9));
    document.querySelector('#map-reset')?.addEventListener('click', () => { map.style.transform = ''; map.dataset.zoom = '1'; });
    selectLocation(venueNames[0] || 'Innovation Lab');
  };
  const zoomMap = factor => { const current = Number(map.dataset.zoom || 1); const next = Math.min(1.3, Math.max(.85, current * factor)); map.dataset.zoom = next; map.style.transform = `scale(${next})`; };
  fetch('/api/events').then(response => response.json()).then(setup).catch(() => setup([]));
}
