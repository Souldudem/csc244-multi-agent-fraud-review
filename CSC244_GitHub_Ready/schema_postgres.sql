-- Proposed PostgreSQL Phase 3 relational schema (NOT yet exercised by Phase 2 Python).
CREATE TABLE employees (employee_id BIGSERIAL PRIMARY KEY, name TEXT NOT NULL, department TEXT NOT NULL);
CREATE TABLE vendors (vendor_id BIGSERIAL PRIMARY KEY, name TEXT NOT NULL, established BOOLEAN NOT NULL DEFAULT FALSE);
CREATE TABLE policies (policy_id BIGSERIAL PRIMARY KEY, policy_name TEXT NOT NULL,
  threshold_amount NUMERIC(12,2) NOT NULL CHECK (threshold_amount >= 0),
  effective_date DATE NOT NULL);
CREATE TABLE transactions (
  transaction_id TEXT PRIMARY KEY, employee_id BIGINT NOT NULL REFERENCES employees(employee_id),
  vendor_id BIGINT NOT NULL REFERENCES vendors(vendor_id), amount NUMERIC(12,2) NOT NULL CHECK (amount > 0),
  occurred_at TIMESTAMPTZ NOT NULL, split_group TEXT, planted_label TEXT);
CREATE TABLE invoices (
  invoice_id BIGSERIAL PRIMARY KEY, transaction_id TEXT NOT NULL REFERENCES transactions(transaction_id),
  invoice_amount NUMERIC(12,2) NOT NULL CHECK (invoice_amount >= 0),
  UNIQUE(transaction_id));
CREATE TABLE receipts (
  receipt_id BIGSERIAL PRIMARY KEY, transaction_id TEXT NOT NULL REFERENCES transactions(transaction_id),
  document_ref TEXT NOT NULL, UNIQUE(transaction_id));
CREATE TABLE approvals (
  approval_id BIGSERIAL PRIMARY KEY, transaction_id TEXT NOT NULL REFERENCES transactions(transaction_id),
  approval_role TEXT NOT NULL CHECK (approval_role IN ('Manager','CFO')),
  approved BOOLEAN NOT NULL, approved_at TIMESTAMPTZ,
  UNIQUE(transaction_id, approval_role));
CREATE TABLE review_runs (
  run_id UUID PRIMARY KEY, transaction_id TEXT NOT NULL REFERENCES transactions(transaction_id),
  started_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE agent_assessments (
  assessment_id BIGSERIAL PRIMARY KEY, run_id UUID NOT NULL REFERENCES review_runs(run_id),
  role TEXT NOT NULL CHECK (role IN ('Employee','Manager','CFO','Fraud Analysis')),
  risk TEXT NOT NULL CHECK (risk IN ('LOW','MEDIUM','HIGH')),
  support_score NUMERIC(4,3) NOT NULL CHECK (support_score BETWEEN 0 AND 1),
  evidence JSONB NOT NULL, rationale TEXT NOT NULL, assessed_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(run_id, role));
CREATE TABLE agent_messages (
  message_id BIGSERIAL PRIMARY KEY, run_id UUID NOT NULL REFERENCES review_runs(run_id),
  sender_role TEXT NOT NULL, content TEXT NOT NULL, sent_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE consensus (
  run_id UUID PRIMARY KEY REFERENCES review_runs(run_id),
  final_risk TEXT NOT NULL CHECK (final_risk IN ('LOW','MEDIUM','HIGH')),
  agreement NUMERIC(3,2) NOT NULL CHECK (agreement BETWEEN 0 AND 1),
  recommendation TEXT NOT NULL, computed_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE accountant_reviews (
  review_id BIGSERIAL PRIMARY KEY, run_id UUID NOT NULL REFERENCES review_runs(run_id),
  reviewer_id TEXT NOT NULL, disposition TEXT NOT NULL,
  notes TEXT, reviewed_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP);
CREATE INDEX ix_transaction_vendor_amount ON transactions(vendor_id,amount);
CREATE INDEX ix_transaction_split_group ON transactions(split_group);
CREATE INDEX ix_assessment_risk ON agent_assessments(risk);
