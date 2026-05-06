// Vercel Web Analytics bootstrap — queues calls until /_vercel/insights/script.js loads.
window.va = window.va || function () { (window.vaq = window.vaq || []).push(arguments); };

// Track outbound link clicks. Leaves <a href> values untouched.
document.addEventListener('click', function (e) {
  var link = e.target.closest && e.target.closest('a');
  if (!link) return;
  var href = link.getAttribute('href') || '';
  if (!/^(https?:|mailto:)/i.test(href)) return;

  var hostname = '';
  try { hostname = new URL(href, location.href).hostname; } catch (_) {}
  var isOutbound = href.toLowerCase().indexOf('mailto:') === 0 || (hostname && hostname !== location.hostname);
  if (!isOutbound) return;

  window.va('event', {
    name: 'outbound_click',
    href: href,
    page: location.pathname
  });
});
