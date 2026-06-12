// Self-hosted hit counter: beacons to /api/hit, public totals at /stats.

function sendHit(kind, id) {
  try {
    var payload = JSON.stringify({ kind: kind, id: id });
    if (navigator.sendBeacon) {
      navigator.sendBeacon('/api/hit', new Blob([payload], { type: 'application/json' }));
    } else {
      fetch('/api/hit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: payload,
        keepalive: true
      });
    }
  } catch (_) {}
}

function googleDocId(href) {
  var match = href.match(/\/document\/d\/([^/]+)/);
  return match ? match[1] : '';
}

// Page view
sendHit('page', location.pathname.replace(/[^A-Za-z0-9-]/g, '') || 'home');

// Post link clicks (the Google Doc links on the index)
document.addEventListener('click', function (e) {
  var link = e.target.closest && e.target.closest('a.post-link');
  if (!link) return;
  var docId = googleDocId(link.getAttribute('href') || '');
  if (docId) sendHit('post', docId);
});
