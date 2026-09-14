document.addEventListener('DOMContentLoaded', () => {
  const page = document.querySelector('.directory-page');
  if (!page) return;
  const map = document.querySelector('#campus-map');
  const panelTitle = document.querySelector('#location-title');
  const panelCategory = document.querySelector('#location-category');
  const panelCount = document.querySelector('#location-count');
  const nextTitle = document.querySelector('#next-event-title');
  const nextMeta = document.querySelector('#next-event-meta');
  const eventLink = document.querySelector('#location-events-link');
  const status = document.querySelector('#map-status');
  const venues = {};
  const categoryByVenue = { 'Innovation Lab': 'Technical', 'Main Auditorium': 'Seminar', 'Sports Complex': 'Sports', 'Library': 'Other', 'Amphitheatre': 'Cultural', 'Cafeteria': 'Other', 'Admin Block': 'Other', 'Main Building': 'Other' };
  const venueKeys = Object.keys(categoryByVenue);
  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (window.gsap && !reducedMotion) {
    gsap.from('.map-world > .road, .map-world > .walkway', { opacity: 0, duration: .9, ease: 'power3.out' });
    gsap.from('.map-building', { opacity: 0, y: 8, duration: .55, stagger: .045, delay: .15, ease: 'power3.out' });
    gsap.from('.trees circle, .event-marker', { opacity: 0, duration: .45, stagger: .025, delay: .35, ease: 'power2.out' });
    gsap.from('.map-panel-head, .map-controls, .map-legend', { opacity: 0, duration: .4, delay: .45, ease: 'power2.out' });
  }
  const selectLocation = name => {
    const records = venues[name] || [];
    document.querySelectorAll('.map-building, .event-marker').forEach(item => item.classList.toggle('selected', item.dataset.location === name));
    panelTitle.textContent = name;
    panelCategory.textContent = `${categoryByVenue[name] || 'Campus'} events`;
    panelCount.textContent = records.length;
    const next = records[0];
    nextTitle.textContent = next ? next.title : 'No event scheduled';
    nextMeta.textContent = next ? `${next.date} · ${next.time}` : '';
    eventLink.href = `/events${categoryByVenue[name] ? `?category=${encodeURIComponent(categoryByVenue[name])}` : ''}`;
    status.textContent = name.toUpperCase();
    if (window.gsap && !reducedMotion) {
      gsap.fromTo('.location-panel', { opacity: .65, y: 8 }, { opacity: 1, y: 0, duration: .35, ease: 'power3.out' });
      gsap.fromTo(`#campus-map .map-building[data-location="${CSS.escape(name)}"]`, { scale: 1 }, { scale: 1.025, duration: .5, ease: 'power3.out' });
    }
  };
  const setup = events => {
    venueKeys.forEach(name => { venues[name] = events.filter(event => event.venue.toLowerCase().includes(name.toLowerCase())); });
    document.querySelectorAll('.map-building, .event-marker, .venue-row').forEach(item => {
      item.addEventListener('click', () => selectLocation(item.dataset.location));
      item.addEventListener('keydown', event => { if (event.key === 'Enter' || event.key === ' ') { event.preventDefault(); selectLocation(item.dataset.location); } });
    });
    document.querySelectorAll('.map-filter').forEach(filter => filter.addEventListener('click', () => {
      document.querySelectorAll('.map-filter').forEach(button => button.classList.remove('active'));
      filter.classList.add('active');
      const value = filter.dataset.filter;
      document.querySelectorAll('.event-marker').forEach(marker => {
        const name = marker.dataset.location;
        marker.style.display = value === 'all' || value === 'venue' || categoryByVenue[name] === value ? '' : 'none';
      });
      status.textContent = value === 'all' ? 'ALL LOCATIONS' : value.toUpperCase();
    }));
    document.querySelector('#map-zoom-in')?.addEventListener('click', () => zoomMap(1.12));
    document.querySelector('#map-zoom-out')?.addEventListener('click', () => zoomMap(.9));
    document.querySelector('#map-reset')?.addEventListener('click', () => { map.style.transform = ''; });
    const search = document.querySelector('#campus-search');
    const results = document.querySelector('#search-results');
    search?.addEventListener('input', () => {
      const query = search.value.trim().toLowerCase();
      results.innerHTML = '';
      if (!query) { results.classList.remove('is-open'); return; }
      const matches = [...venueKeys.filter(name => name.toLowerCase().includes(query)), ...events.filter(event => event.title.toLowerCase().includes(query)).map(event => event.venue)].filter((value, index, values) => values.indexOf(value) === index).slice(0, 6);
      matches.forEach(name => { const button = document.createElement('button'); button.className = 'search-result'; button.innerHTML = `${name}<small>${venues[name]?.length || 0} upcoming events</small>`; button.addEventListener('click', () => { selectLocation(name); search.value = name; results.classList.remove('is-open'); }); results.appendChild(button); });
      results.classList.toggle('is-open', matches.length > 0);
    });
    selectLocation('Innovation Lab');
  };
  const zoomMap = factor => { const current = Number(map.dataset.zoom || 1); const next = Math.min(1.35, Math.max(.85, current * factor)); map.dataset.zoom = next; map.style.transform = `scale(${next})`; };
  fetch('/api/events').then(response => response.json()).then(setup).catch(() => setup([]));
});
