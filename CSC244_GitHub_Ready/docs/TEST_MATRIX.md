# Test compilation and provenance

Source: uploaded `CSC244_Phase2_Complete_Working_Demo(1).zip` (received November 9, 2026).

| Test file | Tests | Provenance | Scope |
|---|---:|---|---|
| `test_prototype.py` | 5 | Unchanged uploaded project | legitimate, high controls, split purchase, missing receipt, SQL audit rows |
| `test_app.py` | 5 | Unchanged uploaded project | dashboard counters, SQL-backed split amount, rerun persistence, saved human decision, input validation |
| `test_http_api.py` | 5 | Added by assistant during package assembly | actual localhost GET, static frontend, run POST, accountant POST, invalid request |
| **Total** | **15** | Source + packaging tests | Synthetic/controlled behavior, not fraud-model statistical validation |

The user and partner's respective authorship **cannot be established from this ZIP**; do not label original 10 tests by student until verified with Git history or confirmation. Code/test owners may overlap. The tested implementation uses deterministic Python reviewer functions, SQLite, and a custom stdlib HTTP UI; it does NOT execute PostgreSQL, LangGraph, Streamlit or LLM inference.

## Reproduce
```powershell
py -3 scripts/run_tests.py
py -3 show_audit.py
py -3 app.py
```
Latest results are at `.reports/tests.txt` (local/CI-generated, ignored by Git). Captured verification snapshots in `evidence/` include environment and UTC timestamp; rerun in class. The original uploaded package's `tests_passed.txt` is retained for comparison.
