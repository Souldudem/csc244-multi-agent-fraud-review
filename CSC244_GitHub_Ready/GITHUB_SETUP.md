# GitHub setup and partner collaboration (PowerShell)

**Best approach: private repository** until both partners confirm the project files and academic requirements. This package is not automatically uploaded anywhere.

## A. First-time repository owner
1. Create a **new empty private** repository at https://github.com/new; suggest `csc244-multi-agent-fraud-review`.
2. In GitHub, do **not** pre-create a README, .gitignore or license; they are already here.
3. Extract the GitHub-ready ZIP into a folder (not an already nested repository), open PowerShell there, then run:

```powershell
git init
git branch -M main
git add .
git status
git commit -m "Import tested Phase 2 baseline and team demo setup"
git remote add origin https://github.com/YOUR-ACCOUNT/csc244-multi-agent-fraud-review.git
git push -u origin main
```

If Git requests your identity, use `git config --global user.name "Your Name"` and `git config --global user.email "your.email@example.com"`. GitHub authenticates through its browser/credential manager, GitHub CLI, or a personal access token; ordinary account passwords cannot be used for `git push` over HTTPS.

## B. Invite partner
Repo > Settings > Collaborators > Add people > enter partner's GitHub username. They accept invite. Partner runs:

```powershell
git clone https://github.com/YOUR-ACCOUNT/csc244-multi-agent-fraud-review.git
cd csc244-multi-agent-fraud-review
git switch -c feature/partner-work
# add the partner's actual code and tests
py -3 scripts/run_tests.py
git add .
git commit -m "Add partner feature and verified tests"
git push -u origin feature/partner-work
```

Open a pull request from `feature/partner-work` into `main`. Both review the changed files and the **Actions** test checks before merging. The project owner should also work on a separate `feature/database-...` branch rather than committing unrelated new features directly to `main`.

## C. Run a clean copy on any Windows computer
```powershell
git clone https://github.com/YOUR-ACCOUNT/csc244-multi-agent-fraud-review.git
cd csc244-multi-agent-fraud-review
py -3 scripts/run_tests.py
py -3 app.py
```

Browse to http://127.0.0.1:8501. Use a separate PowerShell window for `py -3 show_audit.py`. SQLite runtime outputs are ignored by Git and regenerated locally. No package install is necessary.

## D. Show individual evidence to professor
```powershell
git log --graph --oneline --all --max-count=25
git log --author="PARTNER NAME" --oneline
git show --stat COMMIT_HASH
git status
```
Commit authorship and file changes are evidence, not necessarily a precise labor percentage. Confirm ownership in `docs/TEAM_CONTRIBUTIONS_TEMPLATE.md`. Keep original commits wherever available rather than copying others' code into your personal commit.

## E. CI and troubleshooting
- Repo > Actions > `CSC244 test suite` displays checks for every push to `main`, pull request and manual invocation.
- Each job uploads `.reports/tests.txt` as a downloadable test artifact.
- If `git push` fails with 'repository not found', verify the URL, invite and access; if 'non-fast-forward', pull the latest changes and reconcile.
- If `py` is not found, install Python from https://www.python.org/downloads/ and use `python` instead.
- If port 8501 is occupied, run `py -3 app.py --port 8502` and open http://127.0.0.1:8502.
- If there is a test failure, check `.reports/tests.txt` and do not present a green result until rerun.
- GitHub Actions runs tests, **not** a permanently hosted dashboard. For classmates/professor, clone locally. A local live demo runs only while `app.py` is running.
- Never upload real financial records, credentials or secrets; project includes only demonstration data.
