# Presentation speaker guide (28-minute target + 5-minute Q&A)

Presenters are placeholders until both teammates verify actual ownership. Do not assert personal authorship based only on the uploaded ZIP.

- Slides 1–3 (3 min): project goal, synthetic-data scope, what is implemented vs planned. Avoid calling deterministic reviewers LLM agents.
- Slides 4–6 (5 min): SQL evidence, reviewer function responsibilities, coordinator risk rule. Database implementer should explain SQL personally if they wrote it.
- Slide 7 (2 min): walk through seeded scenarios; explain why a LOW example matters.
- Slides 8–10 (4 min): captured screenshots and running browser interactions. Explain screenshots are from the uploaded Phase 2 baseline.
- Slides 11–12 (3 min): baseline test files: 10 passed; new HTTP tests: 5 passed. Distinguish tests added during compilation.
- Slides 13–14 (3 min): GitHub collaboration, CI, individual code/PR evidence. Fill in actual team members and share percentages before class.
- Slide 15 (6 min): live demo: run server, select split purchase, show SQL audit, save human review, rerun all 15 tests. Share speaking tasks according to actual authored code.
- Slide 16 (2 min): limitations and future development; leave 5 minutes for Q&A.

Likely professor questions and defensible responses:
1. **Are these autonomous agents?** No, independent deterministic role-based reviewers and a coordinator; no LLM deliberation or post-discussion re-vote.
2. **Why is it a database project?** It demonstrates relational evidence joins, group aggregation, foreign-key-backed audit records, saved runs, and human review persistence.
3. **Is fraud proven?** No, the system prioritizes suspicious synthetic transactions for human review.
4. **Does PostgreSQL run?** No, schema_postgres.sql is a proposed design; the executable database is SQLite.
5. **What does GitHub do?** Collaboration, history, pull requests, and CI; the web app runs locally on 127.0.0.1, not on GitHub Pages.
6. **Who wrote which tests?** Show real source history and updated TEAM_CONTRIBUTIONS_TEMPLATE.md; do not guess.
