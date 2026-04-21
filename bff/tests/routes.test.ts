import { describe, it, expect, beforeAll, afterAll, vi } from 'vitest';
import type { FastifyInstance } from 'fastify';
import { buildApp } from '../src/app.js';

describe('BFF — protección y forwarding', () => {
  let app: FastifyInstance;

  beforeAll(async () => {
    app = await buildApp();
  });

  afterAll(async () => {
    await app.close();
    vi.restoreAllMocks();
  });

  it('rechaza /api/users sin Authorization', async () => {
    const res = await app.inject({ method: 'GET', url: '/api/users/' });
    expect(res.statusCode).toBe(401);
    expect(res.json()).toEqual({ error: 'missing_token' });
  });

  it('rechaza /api/agent/ask sin Authorization', async () => {
    const res = await app.inject({ method: 'POST', url: '/api/agent/ask', payload: { question: 'x' } });
    expect(res.statusCode).toBe(401);
  });

  it('deja pasar /api/auth/login y reenvía al auth-service', async () => {
    const fetchSpy = vi.spyOn(globalThis, 'fetch').mockResolvedValue(
      new Response(JSON.stringify({ access_token: 'abc' }), {
        status: 200,
        headers: { 'content-type': 'application/json' },
      }),
    );

    const res = await app.inject({
      method: 'POST',
      url: '/api/auth/login',
      payload: { email: 'a@b.c', password: 'x' },
    });

    expect(res.statusCode).toBe(200);
    expect(fetchSpy).toHaveBeenCalledTimes(1);
    const calledUrl = fetchSpy.mock.calls[0]?.[0];
    expect(String(calledUrl)).toContain('/auth/login');
    fetchSpy.mockRestore();
  });
});
