import { describe, expect, it, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router-dom';
import Login from './Login';
import { AuthProvider } from '../context/AuthContext';

function renderLogin() {
  return render(
    <MemoryRouter>
      <AuthProvider>
        <Login />
      </AuthProvider>
    </MemoryRouter>,
  );
}

describe('Login page', () => {
  beforeEach(() => {
    localStorage.clear();
    vi.unstubAllGlobals();
  });

  it('shows a backend error message on invalid credentials', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(
      new Response(JSON.stringify({ error: { code: 'invalid_credentials', message: 'bad' } }),
        { status: 401 }),
    ));
    renderLogin();
    await userEvent.click(screen.getByRole('button', { name: /entrar/i }));
    expect(await screen.findByRole('alert')).toHaveTextContent('bad');
  });

  it('stores the token returned by a successful login', async () => {
    vi.stubGlobal('fetch', vi.fn().mockImplementation((url) => {
      if (String(url).endsWith('/api/auth/login')) {
        return Promise.resolve(new Response(
          JSON.stringify({ token: 'jwt-1', user: { id: 1, email: 'a@b.c', role: 'developer' } }),
          { status: 200 }));
      }
      return Promise.resolve(new Response(
        JSON.stringify({ id: 1, email: 'a@b.c', role: 'developer' }), { status: 200 }));
    }));
    renderLogin();
    await userEvent.click(screen.getByRole('button', { name: /entrar/i }));
    await waitFor(() => expect(localStorage.getItem('juniorswipe_token')).toBe('jwt-1'));
  });
});
