const BASE = import.meta.env.VITE_API_URL ?? 'http://localhost:8000';

function getToken() {
  return localStorage.getItem('cc_token') ?? '';
}

function authHeaders() {
  return {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${getToken()}`,
  };
}

async function request(path, options = {}) {
  const res = await fetch(`${BASE}${path}`, {
    ...options,
    headers: authHeaders(),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail ?? `HTTP ${res.status}`);
  }
  return res.json();
}

export const api = {
  // Auth
  login:    (email, password) =>
    fetch(`${BASE}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    }).then(r => r.json()),

  me: () => request('/auth/me'),

  // Patient
  checkinQuestions: () => request('/checkin/questions'),
  submitCheckin:    (data) => request('/checkin', {
    method: 'POST',
    body: JSON.stringify(data),
  }),
  checkinHistory:   () => request('/checkin/history'),
  chat:             (message) => request('/chat', {
    method: 'POST',
    body: JSON.stringify({ message }),
  }),
  chatHistory:      () => request('/chat/history'),
  reminders:        () => request('/reminders'),

  // Caregiver
  caregiverAlerts:  () => request('/alerts/caregiver'),
  caregiverPatient: () => request('/caregiver/patient'),
  resolveAlert:     (id) => request(`/alerts/${id}/resolve`, {
    method: 'PATCH',
  }),

  // Admin
  facilityStats:    () => request('/facility/stats'),
  facilityPatients: () => request('/facility/patients'),
  facilityAlerts:   () => request('/facility/alerts'),
  triggerReminders: () => request('/reminders/trigger', {
    method: 'POST',
  }),

  // Demo
  simulate: () => request('/demo/simulate', { method: 'POST' }),
};