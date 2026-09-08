import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { ApiError, api, projects, tokenStore } from './client';

describe('api client', () => {
  beforeEach(() => {
    localStorage.clear();
    vi.restoreAllMocks();
  });
  afterEach(() => vi.unstubAllGlobals());

  it('attaches the Bearer token from storage', async () => {
    tokenStore.set('abc123');
    const fetchMock = vi.fn().mockResolvedValue(
      new Response(JSON.stringify({ items: [] }), { status: 200 }),
    );
    vi.stubGlobal('fetch', fetchMock);

    await projects.list();

    const [, opts] = fetchMock.mock.calls[0];
    expect(opts.headers.Authorization).toBe('Bearer abc123');
  });

  it('unwraps the error envelope into an ApiError', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(
      new Response(JSON.stringify({ error: { code: 'email_taken', message: 'taken' } }),
        { status: 409 }),
    ));

    await expect(api.post('/api/auth/register', {}, { auth: false }))
      .rejects.toMatchObject({ status: 409, code: 'email_taken', message: 'taken' });
  });

  it('clears the token and emits an event on 401', async () => {
    tokenStore.set('stale');
    const handler = vi.fn();
    window.addEventListener('juniorswipe:unauthorized', handler);
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(
      new Response(JSON.stringify({ error: { code: 'token_expired', message: 'x' } }),
        { status: 401 }),
    ));

    await expect(api.get('/api/projects')).rejects.toBeInstanceOf(ApiError);
    expect(tokenStore.get()).toBeNull();
    expect(handler).toHaveBeenCalled();
    window.removeEventListener('juniorswipe:unauthorized', handler);
  });
});
