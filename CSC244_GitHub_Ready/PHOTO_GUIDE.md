# CSC 244 Phase 2 — What to photograph

All images in `screenshots/` were rendered using the prototype HTML/CSS/JavaScript and live records retrieved from the running local Python/SQLite backend. You can also take new photographs of your own Windows screen while the application is running.

## Launch

1. Extract the **entire ZIP folder**, keeping all filenames together.
2. Install Python 3.9 or newer if needed.
3. Double-click **launch_dashboard.bat** on Windows. The demo will open at http://127.0.0.1:8501; if the tab opens before the server, refresh.
4. Keep the server terminal open. On the dashboard, click on any sample case in the left panel. **Run agent review** generates a real new assessment in SQLite.

## Five recommended photos (photos or Windows screenshots)

| Photo | Where to look | What it proves |
| --- | --- | --- |
| 1 | Dashboard header and risk counters, F-001 | Working web UI, six synthetic cases and high/medium/low risk classification |
| 2 | F-001, agent vote cards | Four independent role-specific checks; HIGH consensus based on 4/4 HIGH votes |
| 3 | S-001 | Split-purchase aggregation: two transactions ($4,800 and $4,700), SQL group sum $9,500, 3/4 HIGH votes |
| 4 | Bottom of F-001 page after saving accountant decision | SQLite-stored agent discussion messages and human-in-the-loop audit record |
| 5 | PowerShell after `py -3 -m unittest -v test_prototype.py test_app.py` and `py -3 show_audit.py` | Ten passing tests and executed SQL JOIN/GROUP BY/audit queries |

Screenshots 01–06 in the package show examples of results captured from the working project. You can use Windows **Win + Shift + S** to take screenshots (or take camera photos, if required).

## Scripts to demonstrate

```powershell
cd CSC244_Phase2_Prototype
py -3 app.py
```

In a **second PowerShell** window:

```powershell
cd CSC244_Phase2_Prototype
py -3 -m unittest -v test_prototype.py test_app.py
py -3 show_audit.py
```

## Academic accuracy

This is a preliminary deterministic **rule-based multi-agent workflow**, not an LLM-driven multi-agent debate. The Coordinator calculates consensus after four independent assessments; an auditable exchange of votes is stored in SQLite. LangGraph, PostgreSQL, real document retrieval, and a second debating/revision round remain later milestones. All transactions are synthetic; risk flags do not establish actual fraud.
