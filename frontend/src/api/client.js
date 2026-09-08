/**
 * Centralised HTTP client for the JuniorSwipe API.
 * - base URL from VITE_API_URL
 * - attaches `Authorization: Bearer <token>`
 * - normalises the `{ error: { code, message } }` envelope
 * - emits `juniorswipe:unauthorized` on 401 so the app can log out
 */
const BASE_URL = (import.meta.env.VITE_API_URL || 'http://localhost:5000').replace(/\/$/, '');

const TOKEN_KEY = 'juniorswipe_token';
const USER_KEY = 'juniorswipe_user';

export const tokenStore = {
  get: () => localStorage.getItem(TOKEN_KEY),
  set: (t) => localStorage.setItem(TOKEN_KEY, t),
  clear: () => {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
  },
  getUser: () => {
    try {
      return JSON.parse(localStorage.getItem(USER_KEY) || 'null');
    } catch {
      return null;
    }
  },
  setUser: (u) => localStorage.setItem(USER_KEY, JSON.stringify(u)),
};

export class ApiError extends Error {
  constructor(message, status, code, details) {
    super(message);
    this.status = status;
    this.code = code;
    this.details = details;
  }
}

async function request(method, path, { body, auth = true, raw = false } = {}) {
  const headers = {};
  const opts = { method, headers };

  if (body !== undefined && !(body instanceof FormData)) {
    headers['Content-Type'] = 'application/json';
    opts.body = JSON.stringify(body);
  } else if (body instanceof FormData) {
    opts.body = body;
  }

  if (auth) {
    const token = tokenStore.get();
    if (token) headers.Authorization = `Bearer ${token}`;
  }

  let res;
  try {
    res = await fetch(`${BASE_URL}${path}`, opts);
  } catch (netErr) {
    throw new ApiError(`No se pudo conectar con la API (${BASE_URL})`, 0, 'network_error');
  }

  if (res.status === 401) {
    tokenStore.clear();
    window.dispatchEvent(new CustomEvent('juniorswipe:unauthorized'));
  }

  if (res.status === 204) return null;
  if (raw) return res;

  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    const err = data.error || {};
    throw new ApiError(err.message || `HTTP ${res.status}`, res.status, err.code, err.details);
  }
  return data;
}

export const api = {
  baseUrl: BASE_URL,
  get: (p, o) => request('GET', p, o),
  post: (p, body, o) => request('POST', p, { ...o, body }),
  put: (p, body, o) => request('PUT', p, { ...o, body }),
  patch: (p, body, o) => request('PATCH', p, { ...o, body }),
  del: (p, o) => request('DELETE', p, o),
  raw: (method, p, o) => request(method, p, { ...o, raw: true }),
};

export const auth = {
  register: (payload) => api.post('/api/auth/register', payload, { auth: false }),
  login: (payload) => api.post('/api/auth/login', payload, { auth: false }),
  me: () => api.get('/api/auth/me'),
};

export const projects = {
  list: (params = '') => api.get(`/api/projects${params}`),
  get: (id) => api.get(`/api/projects/${id}`),
  create: (payload) => api.post('/api/projects', payload),
  update: (id, payload) => api.patch(`/api/projects/${id}`, payload),
  remove: (id) => api.del(`/api/projects/${id}`),
};

export const tasks = {
  list: (params = '') => api.get(`/api/tasks${params}`),
  create: (payload) => api.post('/api/tasks', payload),
  update: (id, payload) => api.patch(`/api/tasks/${id}`, payload),
  remove: (id) => api.del(`/api/tasks/${id}`),
};

export const profile = {
  get: () => api.get('/api/profiles/me'),
  update: (payload) => api.put('/api/profiles/me', payload),
};

export const resumes = {
  list: () => api.get('/api/resumes'),
  create: (formData) => api.post('/api/resumes', formData),
  remove: (id) => api.del(`/api/resumes/${id}`),
};
