import type { VercelRequest, VercelResponse } from '@vercel/node';

interface FeedbackRequestBody {
  message_id?: string;
  rating?: 'like' | 'dislike' | null;
  user?: string;
}

export default async function handler(req: VercelRequest, res: VercelResponse) {
  if (req.method !== 'POST') {
    res.status(405).json({ error: 'Method not allowed' });
    return;
  }

  const { message_id, rating, user } = (req.body ?? {}) as FeedbackRequestBody;

  if (typeof message_id !== 'string' || message_id.trim() === '') {
    res.status(400).json({ error: 'message_id is required' });
    return;
  }

  const DIFY_API_URL = process.env.DIFY_API_URL;
  const DIFY_API_KEY = process.env.DIFY_API_KEY;

  if (!DIFY_API_URL || !DIFY_API_KEY) {
    res.status(500).json({ error: 'Dify API is not configured on the server' });
    return;
  }

  try {
    const difyResponse = await fetch(`${DIFY_API_URL}/messages/${message_id}/feedbacks`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${DIFY_API_KEY}`,
      },
      body: JSON.stringify({
        rating: rating ?? null,
        user: user ?? 'anonymous',
      }),
    });

    const data = await difyResponse.json();

    if (!difyResponse.ok) {
      console.error('Dify feedback API returned an error:', difyResponse.status, JSON.stringify(data));
    }

    res.status(difyResponse.status).json(data);
  } catch (error) {
    console.error('Dify feedback proxy request failed:', error);
    res.status(502).json({ error: 'Failed to reach Dify API' });
  }
}
