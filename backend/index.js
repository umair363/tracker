const express = require('express');
const cors = require('cors');
const multer = require('multer');
const path = require('path');
const pool = require('./db');

const app = express();
const PORT = process.env.PORT || 5000;

// ─── Middleware ───────────────────────────────────────────────────────────────
app.use(cors());
app.use(express.json());
app.use('/uploads', express.static(path.join(__dirname, 'uploads')));

// File upload config — save receipts to /uploads folder
const storage = multer.diskStorage({
  destination: './uploads/',
  filename: (req, file, cb) => cb(null, `${Date.now()}-${file.originalname}`)
});
const upload = multer({ storage });

// ─── Health Check ─────────────────────────────────────────────────────────────
app.get('/api/health', async (req, res) => {
  try {
    await pool.query('SELECT 1');
    res.json({ status: 'ok', db: 'connected' });
  } catch (e) {
    res.status(500).json({ status: 'error', db: 'disconnected' });
  }
});

// ─── DONATIONS ────────────────────────────────────────────────────────────────

// Get all donations (newest first)
app.get('/api/donations', async (req, res) => {
  try {
    const { rows } = await pool.query('SELECT * FROM donations ORDER BY created_at DESC');
    res.json(rows);
  } catch (e) {
    console.error('GET /api/donations error:', e.message);
    res.status(500).json({ error: e.message });
  }
});

// Create a new donation
app.post('/api/donations', async (req, res) => {
  try {
    const { donor_name, amount, method, reference, notes } = req.body;
    const { rows } = await pool.query(
      `INSERT INTO donations (donor_name, amount, method, reference, notes)
       VALUES ($1, $2, $3, $4, $5) RETURNING *`,
      [donor_name || null, amount, method, reference, notes || null]
    );
    res.status(201).json(rows[0]);
  } catch (e) {
    console.error('POST /api/donations error:', e.message);
    res.status(500).json({ error: e.message });
  }
});

// Update a donation
app.put('/api/donations/:id', async (req, res) => {
  try {
    const { donor_name, amount, method, reference, notes, edit_log } = req.body;
    const { rows } = await pool.query(
      `UPDATE donations SET donor_name=$1, amount=$2, method=$3, reference=$4,
       notes=$5, edit_log=$6 WHERE id=$7 RETURNING *`,
      [donor_name || null, amount, method, reference, notes || null,
       JSON.stringify(edit_log || []), req.params.id]
    );
    if (rows.length === 0) return res.status(404).json({ error: 'Not found' });
    res.json(rows[0]);
  } catch (e) {
    console.error('PUT /api/donations error:', e.message);
    res.status(500).json({ error: e.message });
  }
});

// Delete a donation
app.delete('/api/donations/:id', async (req, res) => {
  try {
    await pool.query('DELETE FROM donations WHERE id=$1', [req.params.id]);
    res.json({ ok: true });
  } catch (e) {
    console.error('DELETE /api/donations error:', e.message);
    res.status(500).json({ error: e.message });
  }
});

// ─── EXPENSES ─────────────────────────────────────────────────────────────────

// Get all expenses (newest first)
app.get('/api/expenses', async (req, res) => {
  try {
    const { rows } = await pool.query('SELECT * FROM expenses ORDER BY created_at DESC');
    res.json(rows);
  } catch (e) {
    console.error('GET /api/expenses error:', e.message);
    res.status(500).json({ error: e.message });
  }
});

// Create a new expense
app.post('/api/expenses', async (req, res) => {
  try {
    const { description, amount, category, receipt_url, notes, line_items } = req.body;
    const { rows } = await pool.query(
      `INSERT INTO expenses (description, amount, category, receipt_url, notes, line_items)
       VALUES ($1, $2, $3, $4, $5, $6) RETURNING *`,
      [description, amount, category, receipt_url || null, notes || null,
       line_items ? JSON.stringify(line_items) : null]
    );
    res.status(201).json(rows[0]);
  } catch (e) {
    console.error('POST /api/expenses error:', e.message);
    res.status(500).json({ error: e.message });
  }
});

// Update an expense
app.put('/api/expenses/:id', async (req, res) => {
  try {
    const { description, amount, category, receipt_url, notes, line_items, edit_log } = req.body;
    const { rows } = await pool.query(
      `UPDATE expenses SET description=$1, amount=$2, category=$3, receipt_url=$4,
       notes=$5, line_items=$6, edit_log=$7 WHERE id=$8 RETURNING *`,
      [description, amount, category, receipt_url || null, notes || null,
       line_items ? JSON.stringify(line_items) : null,
       JSON.stringify(edit_log || []), req.params.id]
    );
    if (rows.length === 0) return res.status(404).json({ error: 'Not found' });
    res.json(rows[0]);
  } catch (e) {
    console.error('PUT /api/expenses error:', e.message);
    res.status(500).json({ error: e.message });
  }
});

// Delete an expense
app.delete('/api/expenses/:id', async (req, res) => {
  try {
    await pool.query('DELETE FROM expenses WHERE id=$1', [req.params.id]);
    res.json({ ok: true });
  } catch (e) {
    console.error('DELETE /api/expenses error:', e.message);
    res.status(500).json({ error: e.message });
  }
});

// ─── SETTINGS ─────────────────────────────────────────────────────────────────

// Get all settings
app.get('/api/settings', async (req, res) => {
  try {
    const { rows } = await pool.query('SELECT * FROM settings');
    res.json(rows);
  } catch (e) {
    console.error('GET /api/settings error:', e.message);
    res.status(500).json({ error: e.message });
  }
});

// Update a setting (upsert)
app.put('/api/settings', async (req, res) => {
  try {
    const { key, value } = req.body;
    const { rows } = await pool.query(
      `INSERT INTO settings (key, value) VALUES ($1, $2)
       ON CONFLICT (key) DO UPDATE SET value = $2 RETURNING *`,
      [key, value]
    );
    res.json(rows[0]);
  } catch (e) {
    console.error('PUT /api/settings error:', e.message);
    res.status(500).json({ error: e.message });
  }
});

// ─── FILE UPLOAD ──────────────────────────────────────────────────────────────

app.post('/api/upload', upload.single('receipt'), (req, res) => {
  if (!req.file) return res.status(400).json({ error: 'No file provided' });
  const url = `/uploads/${req.file.filename}`;
  res.json({ url });
});

// ─── Start Server ─────────────────────────────────────────────────────────────
app.listen(PORT, '0.0.0.0', () => {
  console.log(`✅ Backend API running on port ${PORT}`);
});
