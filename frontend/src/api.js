const BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export function getToken() {
  return sessionStorage.getItem('token');
}

export function setSession(token, user) {
  sessionStorage.setItem('token', token);
  sessionStorage.setItem('user', JSON.stringify(user));
}

export function clearSession() {
  sessionStorage.clear();
}

export function getUser() {
  const raw = sessionStorage.getItem('user');
  return raw ? JSON.parse(raw) : null;
}

async function request(path, options = {}) {
  const headers = { 'Content-Type': 'application/json', ...(options.headers || {}) };
  const token = getToken();
  if (token) headers.Authorization = `Bearer ${token}`;

  const res = await fetch(`${BASE}${path}`, { ...options, headers });
  const data = await res.json().catch(() => ({}));

  if (res.status === 401) {
    clearSession();
    window.location.href = '/login';
  }
  if (!res.ok) throw new Error(data.error || 'Something went wrong. Please try again.');
  return data;
}

export const api = {
  register: (body) => request('/api/auth/register', { method: 'POST', body: JSON.stringify(body) }),
  login: (body) => request('/api/auth/login', { method: 'POST', body: JSON.stringify(body) }),
  listProjects: () => request('/api/projects'),
  createProject: (body) => request('/api/projects', { method: 'POST', body: JSON.stringify(body) }),
  getProject: (id) => request(`/api/projects/${id}`),
  createSite: (id, body) =>
    request(`/api/projects/${id}/sites`, { method: 'POST', body: JSON.stringify(body) }),
  getSite: (id) => request(`/api/sites/${id}`),
  deleteSite: (id) => request(`/api/sites/${id}`, { method: 'DELETE' }),
};
