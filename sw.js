// Red primero para todo (datos siempre frescos); cache solo como respaldo sin senal.
const CACHE = 'electrolineras-v6';
const BASE = ['./', 'index.html', 'manifest.json', 'precios.json', 'estaciones_epm.json', 'vivo.json', 'otras_redes.json', 'osm.json', 'icon-180.png', 'icon-192.png', 'icon-512.png',
  'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.css',
  'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.js'];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(BASE)).then(() => self.skipWaiting()));
});
self.addEventListener('activate', e => {
  e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== CACHE).map(k => caches.delete(k))))
    .then(() => self.clients.claim()));
});
self.addEventListener('fetch', e => {
  const u = new URL(e.request.url);
  if (e.request.method !== 'GET') return;
  // Datos en vivo (EPM / OpenStreetMap / mosaicos) los maneja la app; no se cachean aqui.
  if (u.origin !== location.origin && !u.hostname.includes('cdnjs')) return;
  e.respondWith(
    fetch(e.request).then(r => {
      if (r.ok) { const copia = r.clone(); caches.open(CACHE).then(c => c.put(e.request.url.split('?')[0], copia)); }
      return r;
    }).catch(() => caches.match(e.request.url.split('?')[0]).then(r => r || caches.match('index.html')))
  );
});
