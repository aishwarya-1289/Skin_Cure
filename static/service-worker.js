self.addEventListener('install', function(event) {
    event.waitUntil(
      caches.open('flask-pwa-cache').then(function(cache) {
        return cache.addAll([
            '/',
            '/static/manifest.json',
            '/static/offline.html',
            '/static/tropical-leaves.png',
            '/static/checkImage.jpg'
          // Add other static assets you want to cache
        ]);
      })
    );
  });
  
  self.addEventListener('fetch', function(event) {
    event.respondWith(
      caches.match(event.request).then(function(response) {
        return response || fetch(event.request);
      })
    );
  });
  