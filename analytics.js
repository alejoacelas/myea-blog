// Vercel Web Analytics bootstrap — queues calls until /_vercel/insights/script.js loads.
window.va = window.va || function () { (window.vaq = window.vaq || []).push(arguments); };

function textFromLink(link, selector) {
  var el = selector ? link.querySelector(selector) : link;
  return el && el.textContent ? el.textContent.trim().replace(/\s+/g, ' ') : '';
}

function googleDocId(href) {
  var match = href.match(/\/document\/d\/([^/]+)/);
  return match ? match[1] : '';
}

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

  if (link.classList.contains('post-link')) {
    window.va('event', {
      name: 'blog_post_click',
      data: {
        post: textFromLink(link, '.post-title') || href,
        doc_id: googleDocId(href)
      }
    });
    return;
  }

  window.va('event', {
    name: 'outbound_click',
    data: {
      link: textFromLink(link) || href,
      href: href
    }
  });
});
