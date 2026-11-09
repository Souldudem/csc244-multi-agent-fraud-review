# CSC 244 Phase 2: Preliminary Prototype

This is a **real, runnable deterministic proof of concept**, not a completed AI/LLM application. It tests the role-based workflow, risk rules, relational audit trail, and consensus protocol planned in Phase 1. The demo uses synthetic data only. Findings are **review flags**, not accusations or verified fraud.

## Run on Windows (PowerShell)

```powershell
cd CSC244_Phase2_Prototype
py -3 prototype.py
py -3 -m unittest -v test_prototype.py
```

Use `python` instead of `py -3` on macOS/Linux. No external Python packages, API keys, model downloads, or database server required. Output files appear in the current working directory: `phase2_demo.sqlite` and `phase2_results.json`.

Select a transaction: `py -3 prototype.py --transaction F-001`.

## What has been implemented

- Six seeded transactions with known scenario labels, including a clean example, unauthorized purchase, split-purchase pair, missing receipt, and new vendor.
- Four independent deterministic, role-specific reviewers: Employee, Manager, CFO, and Fraud Analysis.
- Coordinator consensus: 3 or more HIGH votes -> HIGH priority; otherwise mixed votes -> MEDIUM review; all LOW -> LOW record.
- Agreement fraction, traceable evidence identifiers, one round of logged evidence exchange, and relational audit records (run ID, 4 assessments, 4 messages, consensus result).
- SQLite schema, proposed normalized PostgreSQL schema and five unit tests.

## Not yet implemented

- LangGraph graph execution or autonomous LLM reasoning.
- Post-discussion voting/reconsideration, actual receipt/document ingestion, independent approval-policy engine, or a Streamlit UI.
- A live PostgreSQL connection. `schema_postgres.sql` describes the **target** schema for Phase 3; the actual demo uses SQLite.
- Evaluation on broad datasets or calibrated risk probabilities. The support score is heuristic, **not** a probability of fraud.

## Evidence and limitations

To inspect the audit database using Python:

```python
import sqlite3
con = sqlite3.connect('phase2_demo.sqlite')
print(con.execute('SELECT transaction_id, final_risk, agreement FROM consensus').fetchall())
```

Next milestones are to port queries to PostgreSQL, coordinate nodes with LangGraph, expose accountant decisions in Streamlit, add stronger data generation and evaluation, and compare against a single-agent baseline.

## NEW: Live browser dashboard (photo-ready evidence)

The Phase 2 demo includes a fully working local browser interface. It needs **only Python 3.9+** (no cloud models, installation packages, web accounts, or database server). Double-click `launch_dashboard.bat` on Windows, or execute:

```powershell
cd CSC244_Phase2_Prototype
py -3 app.py
```

Open **http://127.0.0.1:8501** in Chrome or Edge. Stop the server using Ctrl+C in the terminal.

### What the live dashboard lets you demonstrate

1. Select any of the six seeded synthetic cases (F-001, S-001, S-002, M-001, V-001, L-001).
2. See the stored review, transaction attributes, evidence flags, individual agent votes, agreement ratio, and Coordinator recommendation.
3. Click **Run agent review**. This genuinely calls the four rule-based Python agent functions, computes consensus, and persists a NEW run and its four agent messages to SQLite.
4. Scroll down to **Stored agent discussion**, which displays the latest four real stored audit messages.
5. Use **Accountant disposition** and click **Save accountant decision** to persist a human review (try F-001 + Request additional evidence).
6. Run `py -3 -m unittest -v test_prototype.py test_app.py` to verify the code. Tests use disposable in-memory/temporary databases.

The SQLite database for the web application is `dashboard_demo.sqlite` (created automatically). The original command-line demo is still available with `py -3 prototype.py`.

### Suggested screenshots/photos for your instructor

- 01: Dashboard overview and cases — HIGH/MEDIUM/LOW counters, F-001 selected.
- 02: F-001 result — HIGH coordinator risk, 4 HIGH agent votes, missing invoice support / controls.
- 03: S-001 case — the two linked purchases total $9,500; different agent perspectives.
- 04: Audit and human review — database-backed agent messages and saved accountant decision.
- 05: Terminal with `py -3 -m unittest -v test_prototype.py test_app.py` output showing passed tests.

See `screenshots/` for actual Playwright screenshots of the running app generated during package verification. Images document this local demonstration; they are not AI-generated or fabricated interface mockups.

### Honest implementation boundary

Four independent deterministic reviewers and a coordinator **are functional**. Evidence messages are logged, but there is NOT a true LLM-to-LLM conversational debate or post-discussion re-voting, nor are LangGraph, PostgreSQL, or document retrieval connected yet. Those are subsequent implementation targets. Do not describe this demonstration as a completed autonomous multi-agent AI system.

### SQL implementation evidence

Run `py -3 show_audit.py` while the dashboard has been used. This executes **five actual SQL SELECT queries** that demonstrate JOIN, GROUP BY/HAVING, latest-run SQL, agent assessment records, and the accountant decision trail. Their output can be photographed in PowerShell. `example_sql_output.txt` contains a sample captured from this working prototype.
