# FinGuard | CSC 244 Multi-Agent Financial Risk Review

**Status:** runnable Phase 2 baseline prepared for a Phase 3 team presentation, not yet a completed LLM-based multi-agent application. All transactions are **synthetic**. The four role reviewers are deterministic Python rules; logged evidence messages are not a multi-round AI debate. Human review remains authoritative.

## Quick start: Windows PowerShell
Requirements: Python 3.9+ and Git for collaboration (no third-party Python packages, API keys, or hosted server).

```powershell
git clone https://github.com/YOUR-ACCOUNT/YOUR-REPO.git
cd YOUR-REPO
py -3 scripts/run_tests.py
py -3 app.py
```

Open **http://127.0.0.1:8501**. Stop with Ctrl+C. If `py` is unavailable, use `python`. On macOS/Linux, `python3` is common. An optional one-command setup on Windows is `powershell -ExecutionPolicy Bypass -File .\scripts\setup_windows.ps1`.

The first launch automatically creates a fresh ignored `dashboard_demo.sqlite`, populates six synthetic transactions, runs four independent reviewers for each transaction, and saves audit records. The file remains local and is not committed. Do not push real accounting or employee data.

## Demo script 
1. Open the dashboard. Show counters: 6 transactions, 3 high, 2 medium and 1 low in the baseline dataset.
2. Choose **F-001** to inspect a high-value unauthorized scenario.
3. Choose **S-001** to show a $4,800 purchase paired with S-002 ($4,700), total **$9,500**, flagged by database aggregation.
4. Choose **L-001** to show LOW-risk handling and discuss false alerts.
5. Click **Run agent review**, which creates a new persistent review run.
6. Under **Accountant disposition**, save *Request additional evidence* with a note; refresh to confirm persistence.
7. In a separate terminal run `py -3 show_audit.py` to display real SQL joins, split groups, votes and human reviews.
8. Run `py -3 scripts/run_tests.py` to save the exact latest results to `.reports/tests.txt`.

## Repo map
| File or folder | Purpose |
|---|---|
| `prototype.py`, `schema_sqlite.sql`, `schema_postgres.sql` | Rules, consensus, implemented SQLite DDL, proposed PostgreSQL DDL |
| `app.py`, `dashboard.html`, `dashboard.js`, `dashboard.css` | Local dashboard and REST endpoints |
| `test_prototype.py` | 5 original risk and audit tests |
| `test_app.py` | 5 original dashboard/database tests |
| `test_http_api.py` | 5 added real HTTP integration tests; **new compilation work, not attributed to either student** |
| `scripts/run_tests.py` | Reproducible test runner and local evidence log |
| `.github/workflows/tests.yml` | Test matrix for Python 3.10/3.12 on Ubuntu/Windows on push or PR |
| `show_audit.py` | Query audit evidence |
| `screenshots/` | Original captured Phase 2 UI screenshots |
| `docs/` | Original Phase 2 README, instructor installation PDF, contribution template |
| `presentation/` | Instructor-facing slides |

## Tests and scope
Run `py -3 -m unittest discover -p 'test_*.py' -v` or `py -3 scripts/run_tests.py`. Tests use temporary/in-memory SQLite databases and an ephemeral localhost HTTP port; no test touches your personal database. The prior source had 10 tests; this compilation adds 5 HTTP tests. A passing result proves only these controlled synthetic scenarios and code paths, not general fraud accuracy.

## GitHub collaboration
Follow `GITHUB_SETUP.md` for exact commands, feature branches, pull requests, CI results, and how to preserve each student's contribution history. Actual ownership and percentages must be supplied by each team member and confirmed in `docs/TEAM_CONTRIBUTIONS_TEMPLATE.md`.

## Not yet implemented
Production PostgreSQL integration, LangGraph, autonomous LLM debate, revised second-round votes, real bank/ledger imports and deployment-grade authorization. `schema_postgres.sql` is a design artifact, not a deployed database. See `docs/ORIGINAL_PHASE2_README.md` for the source ZIP's original scope.
