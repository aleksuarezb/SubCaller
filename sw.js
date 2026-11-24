// Bump CACHE whenever index.html (or any cached file) changes, so iPads pick up the new version.
const CACHE = 'subcaller-v5';
const FILES = ['./', 'index.html', 'manifest.json', 'apple-touch-icon.png', 'icon-192.png', 'icon-512.png']
  .concat(['sub'].concat([...Array(30)].flatMap((_, k) => ['black-', 'white-', 'and-'].map(w => w + (k + 1)))).map(n => 'voice/' + n + '.mp3'));

self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(FILES.map(f => new Request(f, {cache: 'reload'})))).then(() => self.skipWaiting()));
});

self.addEventListener('activate', e => {
  e.waitUntil(caches.keys()
    .then(keys => Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k))))
    .then(() => self.clients.claim()));
});

self.addEventListener('fetch', e => {
  if (e.request.method !== 'GET') return;
  e.respondWith(
    caches.match(e.request, {ignoreSearch: true}).then(hit => hit || fetch(e.request))
  );
});
