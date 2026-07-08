import type { VercelRequest, VercelResponse } from '@vercel/node';

interface ChatRequestBody {
  query?: string;
  conversation_id?: string;
  user?: string;
}

export default async function handler(req: VercelRequest, res: VercelResponse) {
  if (req.method !== 'POST') {
    res.status(405).json({ error: 'Method not allowed' });
    return;
  }

  const { query, conversation_id, user } = (req.body ?? {}) as ChatRequestBody;

  if (typeof query !== 'string' || query.trim() === '') {
    res.status(400).json({ error: 'query is required' });
    return;
  }

  const DIFY_API_URL = process.env.DIFY_API_URL;
  const DIFY_API_KEY = process.env.DIFY_API_KEY;

  if (!DIFY_API_URL || !DIFY_API_KEY) {
    res.status(500).json({ error: 'Dify API is not configured on the server' });
    return;
  }

  try {
    const difyResponse = await fetch(`${DIFY_API_URL}/chat-messages`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${DIFY_API_KEY}`,
      },
      body: JSON.stringify({
        inputs: {},
        query,
        response_mode: 'blocking',
        conversation_id: conversation_id ?? '',
        user: user ?? 'anonymous',
      }),
    });

    const data = await difyResponse.json();

    if (!difyResponse.ok) {
      console.error('Dify API returned an error:', difyResponse.status, JSON.stringify(data));
    }

    res.status(difyResponse.status).json(data);
  } catch (error) {
    console.error('Dify proxy request failed:', error);
    res.status(502).json({ error: 'Failed to reach Dify API' });
  }
}
