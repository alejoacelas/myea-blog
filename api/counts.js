import { list } from '@vercel/blob';

export default async function handler(req, res) {
  const counts = { post: {}, page: {} };
  let cursor;
  do {
    const batch = await list({ prefix: 'hits/', cursor, limit: 1000 });
    for (const blob of batch.blobs) {
      const [, kind, id] = blob.pathname.split('/');
      if (!counts[kind] || !id) continue;
      counts[kind][id] = (counts[kind][id] || 0) + 1;
    }
    cursor = batch.cursor;
  } while (cursor);

  res.setHeader('Cache-Control', 's-maxage=60, stale-while-revalidate=300');
  res.status(200).json(counts);
}
