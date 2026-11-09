"""Executable SQL evidence for the CSC 244 database course.

Run: py -3 show_audit.py
Prints real queries and their current SQLite results; suitable for classroom photos.
"""
import argparse
from pathlib import Path
from app import initialise
from prototype import ROOT, open_db

QUERIES = [
    ("1 / RELATIONAL JOIN: transaction + employee + vendor", """
SELECT t.id AS case_id, e.department, v.name AS vendor, t.amount,
       t.receipt_present AS receipt, t.manager_approved AS manager_ok
FROM transactions t
JOIN employees e ON e.id=t.employee_id
JOIN vendors v ON v.id=t.vendor_id
ORDER BY t.id;
"""),
    ("2 / SPLIT-PURCHASE AGGREGATION (GROUP BY and HAVING)", """
SELECT split_group, COUNT(*) AS purchase_count,
       ROUND(SUM(amount),2) AS combined_amount
FROM transactions
WHERE split_group IS NOT NULL
GROUP BY split_group
HAVING COUNT(*) > 1 AND SUM(amount) > 5000;
"""),
    ("3 / MOST RECENT RISK DECISIONS (correlated subquery)", """
SELECT c.transaction_id, c.final_risk, c.agreement,
       c.recommendation
FROM consensus c
WHERE c.rowid = (
  SELECT MAX(other.rowid) FROM consensus other
  WHERE other.transaction_id = c.transaction_id
)
ORDER BY c.transaction_id;
"""),
    ("4 / F-001 AUDIT: individual agent votes + evidence reference", """
SELECT a.role, a.risk, a.support_score,
       SUBSTR(a.evidence_json,1,58) AS evidence_excerpt
FROM agent_assessments a
JOIN consensus c ON c.run_id=a.run_id
WHERE c.transaction_id='F-001'
  AND c.rowid=(SELECT MAX(rowid) FROM consensus WHERE transaction_id='F-001')
ORDER BY a.id;
"""),
    ("5 / HUMAN ACCOUNTANT DISPOSITIONS", """
SELECT c.transaction_id, r.decision, r.reviewer_notes
FROM accountant_reviews r JOIN consensus c ON c.run_id=r.run_id
ORDER BY r.id DESC LIMIT 5;
"""),
]

def view(cursor, width=31):
    cols=[x[0] for x in cursor.description]
    data=cursor.fetchall()
    col_widths=[]
    for i,col in enumerate(cols):
        n=max([len(str(col))]+[len(str(r[i])) for r in data])
        col_widths.append(min(width,n))
    def line(cells):
        return ' | '.join(str(v)[:col_widths[i]].ljust(col_widths[i]) for i,v in enumerate(cells))
    print(line(cols));print('-+-'.join('-'*n for n in col_widths))
    for row in data:print(line(row))
    print(f"{len(data)} row(s) returned\n")

def main():
    p=argparse.ArgumentParser(description='Execute actual SQLite audit queries')
    p.add_argument('--db',default=str(ROOT/'dashboard_demo.sqlite'))
    args=p.parse_args()
    initialise(args.db)
    db=open_db(args.db)
    print('CSC 244 — SQL Database Evidence | Synthetic demonstration')
    print('Database:', Path(args.db).name)
    try:
        for title,sql in QUERIES:
            print('\n' + '='*86+'\n'+title+'\n'+'='*86)
            print(sql.strip())
            view(db.execute(sql))
    finally:
        db.close()

if __name__=='__main__':main()
