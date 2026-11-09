-- Executable local proof-of-concept schema. Target production design is in schema_postgres.sql.
CREATE TABLE IF NOT EXISTS employees (
  id INTEGER PRIMARY KEY, name TEXT NOT NULL, department TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS vendors (
  id INTEGER PRIMARY KEY, name TEXT NOT NULL, is_established INTEGER NOT NULL CHECK (is_established IN (0,1)));
CREATE TABLE IF NOT EXISTS transactions (
  id TEXT PRIMARY KEY, employee_id INTEGER NOT NULL REFERENCES employees(id),
  vendor_id INTEGER NOT NULL REFERENCES vendors(id), amount REAL NOT NULL CHECK (amount > 0),
  transaction_time TEXT NOT NULL, invoice_amount REAL NOT NULL,
  receipt_present INTEGER NOT NULL CHECK (receipt_present IN (0,1)),
  manager_approved INTEGER NOT NULL CHECK (manager_approved IN (0,1)),
  cfo_approved INTEGER NOT NULL CHECK (cfo_approved IN (0,1)),
  split_group TEXT, planted_label TEXT NOT NULL);
CREATE INDEX IF NOT EXISTS ix_tx_vendor_amount ON transactions(vendor_id, amount);
CREATE INDEX IF NOT EXISTS ix_tx_split ON transactions(split_group);
CREATE TABLE IF NOT EXISTS agent_assessments (
  id INTEGER PRIMARY KEY AUTOINCREMENT, run_id TEXT NOT NULL,
  transaction_id TEXT NOT NULL REFERENCES transactions(id),
  role TEXT NOT NULL, risk TEXT NOT NULL CHECK (risk IN ('LOW','MEDIUM','HIGH')),
  support_score REAL NOT NULL CHECK (support_score BETWEEN 0 AND 1),
  rationale TEXT NOT NULL, evidence_json TEXT NOT NULL, created_at TEXT NOT NULL,
  UNIQUE(run_id, role));
CREATE TABLE IF NOT EXISTS agent_messages (
  id INTEGER PRIMARY KEY AUTOINCREMENT, run_id TEXT NOT NULL,
  transaction_id TEXT NOT NULL REFERENCES transactions(id),
  sender_role TEXT NOT NULL, message TEXT NOT NULL, created_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS consensus (
  run_id TEXT PRIMARY KEY, transaction_id TEXT NOT NULL REFERENCES transactions(id),
  final_risk TEXT NOT NULL CHECK(final_risk IN ('LOW','MEDIUM','HIGH')),
  agreement REAL NOT NULL CHECK(agreement BETWEEN 0 AND 1),
  recommendation TEXT NOT NULL, created_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS accountant_reviews (
  id INTEGER PRIMARY KEY AUTOINCREMENT, run_id TEXT NOT NULL REFERENCES consensus(run_id),
  decision TEXT NOT NULL, reviewer_notes TEXT, reviewed_at TEXT NOT NULL);
