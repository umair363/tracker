-- ============================================
-- ROSHAN SAFAR TRACKER - PostgreSQL Init
-- ============================================

CREATE EXTENSION IF NOT EXISTS "pgcrypto";

CREATE TABLE IF NOT EXISTS donations (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  donor_name TEXT,
  amount NUMERIC NOT NULL,
  method TEXT NOT NULL,
  reference TEXT NOT NULL,
  notes TEXT,
  edit_log JSONB DEFAULT '[]',
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS expenses (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  description TEXT NOT NULL,
  amount NUMERIC NOT NULL,
  category TEXT NOT NULL,
  receipt_url TEXT,
  notes TEXT,
  line_items JSONB DEFAULT NULL,
  edit_log JSONB DEFAULT '[]',
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS settings (
  key TEXT PRIMARY KEY,
  value TEXT NOT NULL
);

INSERT INTO settings (key, value) VALUES ('goal', '500000')
ON CONFLICT (key) DO NOTHING;
