import { timingSafeEqual } from 'node:crypto';
import { mongoDb } from '@/lib/sql-mongo';

export const dynamic = 'force-dynamic';
export async function GET(request: Request) {
  const supplied = Buffer.from(request.headers.get('x-portal-key') || '');
  const expected = Buffer.from(process.env.PORTAL_BRIDGE_KEY || '');
  if (expected.length < 43 || supplied.length !== expected.length || !timingSafeEqual(supplied, expected)) {
    return Response.json({ error: 'Not found' }, { status: 404 });
  }
  try {
    await (await mongoDb()).command({ ping: 1 });
    return Response.json({ status: 'ok' }, { headers: { 'Cache-Control': 'no-store' } });
  } catch {
    return Response.json({ status: 'unavailable' }, { status: 503 });
  }
}
