import { put } from '@vercel/blob';

// One blob per hit, under hits/<kind>/<id>/ — counting is just listing.
const KIND_RE = /^(post|page)$/;
const ID_RE = /^[A-Za-z0-9_-]{1,64}$/;

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'POST only' });
  }
  const { kind, id } = req.body || {};
  if (!KIND_RE.test(kind || '') || !ID_RE.test(id || '')) {
    return res.status(400).json({ error: 'bad kind or id' });
  }
  await put(`hits/${kind}/${id}/h`, '1', {
    access: 'public',
    addRandomSuffix: true,
    contentType: 'text/plain',
  });
  res.status(204).end();
}
