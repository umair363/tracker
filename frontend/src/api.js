// ─── API Helper ──────────────────────────────────────────────────────────────
// This module replaces the old Supabase client.
// All requests go to /api/* which Nginx proxies to the backend container.

async function request(path, opts = {}) {
  const isFormData = opts.body instanceof FormData;
  const headers = isFormData ? {} : { 'Content-Type': 'application/json' };
  const body = isFormData ? opts.body : (opts.body ? JSON.stringify(opts.body) : undefined);

  const res = await fetch(`/api${path}`, { ...opts, headers, body });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ error: res.statusText }));
    throw new Error(err.error || 'API request failed');
  }
  return res.json();
}

export const api = {
  // Donations
  getDonations:    ()         => request('/donations'),
  addDonation:     (data)     => request('/donations',      { method: 'POST', body: data }),
  updateDonation:  (id, data) => request(`/donations/${id}`, { method: 'PUT',  body: data }),
  deleteDonation:  (id)       => request(`/donations/${id}`, { method: 'DELETE' }),

  // Expenses
  getExpenses:     ()         => request('/expenses'),
  addExpense:      (data)     => request('/expenses',       { method: 'POST', body: data }),
  updateExpense:   (id, data) => request(`/expenses/${id}`,  { method: 'PUT',  body: data }),
  deleteExpense:   (id)       => request(`/expenses/${id}`,  { method: 'DELETE' }),

  // Settings
  getSettings:     ()         => request('/settings'),
  updateGoal:      (value)    => request('/settings', { method: 'PUT', body: { key: 'goal', value: String(value) } }),

  // File upload
  uploadReceipt: async (file) => {
    const fd = new FormData();
    fd.append('receipt', file);
    return request('/upload', { method: 'POST', body: fd });
  },
};
