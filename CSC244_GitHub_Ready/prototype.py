"""CSC 244 Phase 2 proof of concept: role-based financial risk review.

Uses only Python's standard library and SQLite so it runs without API keys,
LLMs or a PostgreSQL server. PostgreSQL/LangGraph/Streamlit are Phase 3 targets.
The outputs identify review risk, not proven fraud.
"""
from __future__ import annotations

import argparse
import json
import sqlite3
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ROLES = ("Employee", "Manager", "CFO", "Fraud Analysis")


@dataclass
class Assessment:
    role: str
    risk: str
    support_score: float  # heuristic evidence strength, not a probability
    evidence: list[str]
    rationale: str


def open_db(database: str = ":memory:") -> sqlite3.Connection:
    conn = sqlite3.connect(database)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.executescript((ROOT / "schema_sqlite.sql").read_text(encoding="utf-8"))
    return conn


def seed_demo(conn: sqlite3.Connection) -> None:
    """Insert six known scenarios without duplicating existing rows."""
    employees = [(1, "Sam Rivera", "Operations"), (2, "Jordan Lee", "IT")]
    vendors = [(1, "Office Supply Co", 1), (2, "Brand New Vendor LLC", 0)]
    transactions = [
        # id, employee, vendor, amount, recorded time, invoice amount, receipt, mgr, cfo, split group, labelled case
        ("L-001", 1, 1, 850.0, "2026-10-01T13:00:00", 850.0, 1, 1, 0, None, "legitimate"),
        ("F-001", 2, 2, 12000.0, "2026-10-02T02:20:00", 9800.0, 0, 0, 0, None, "suspicious"),
        ("S-001", 1, 1, 4800.0, "2026-10-03T10:00:00", 4800.0, 1, 1, 0, "G-001", "suspicious"),
        ("S-002", 1, 1, 4700.0, "2026-10-03T10:05:00", 4700.0, 1, 1, 0, "G-001", "suspicious"),
        ("M-001", 1, 1, 2450.0, "2026-10-04T11:00:00", 2450.0, 0, 1, 0, None, "needs_review"),
        ("V-001", 2, 2, 1750.0, "2026-10-05T14:00:00", 1750.0, 1, 1, 0, None, "needs_review"),
    ]
    conn.executemany("INSERT OR IGNORE INTO employees VALUES (?,?,?)", employees)
    conn.executemany("INSERT OR IGNORE INTO vendors VALUES (?,?,?)", vendors)
    conn.executemany("""INSERT OR IGNORE INTO transactions
    (id, employee_id, vendor_id, amount, transaction_time, invoice_amount,
     receipt_present, manager_approved, cfo_approved, split_group, planted_label)
    VALUES (?,?,?,?,?,?,?,?,?,?,?)""", transactions)
    conn.commit()


def transaction_context(conn: sqlite3.Connection, tx_id: str) -> dict:
    row = conn.execute("""SELECT t.*, e.department, v.name as vendor_name,
           v.is_established FROM transactions t
           JOIN employees e ON t.employee_id = e.id
           JOIN vendors v ON t.vendor_id = v.id WHERE t.id = ?""", (tx_id,)).fetchone()
    if row is None:
        raise ValueError(f"Unknown transaction ID: {tx_id}")
    data = dict(row)
    split = conn.execute("""SELECT COUNT(*) AS n, COALESCE(SUM(amount),0) AS total
        FROM transactions WHERE split_group = ? AND split_group IS NOT NULL""",
        (data["split_group"],)).fetchone()
    data["split_count"] = split["n"] if data["split_group"] else 0
    data["split_total"] = split["total"] if data["split_group"] else 0
    same = conn.execute("""SELECT id FROM transactions WHERE id <> ?
        AND vendor_id = ? AND amount = ? ORDER BY transaction_time""",
        (tx_id, data["vendor_id"], data["amount"])).fetchall()
    data["matching_transaction_ids"] = [r["id"] for r in same]
    data["outside_hours"] = not (7 <= int(data["transaction_time"][11:13]) < 20)
    data["invoice_mismatch"] = abs(data["amount"] - data["invoice_amount"]) > 0.01
    data["split_suspected"] = data["split_count"] > 1 and data["split_total"] > 5000
    return data


def output(role: str, points: int, evidence: list[str], reason: str) -> Assessment:
    rating = "HIGH" if points >= 2 else "MEDIUM" if points == 1 else "LOW"
    support = round(min(0.95, 0.55 + 0.12 * max(points, 1)), 2)
    return Assessment(role, rating, support, evidence or ["TX:reviewed"], reason)


def employee_agent(t: dict) -> Assessment:
    p, ev = 0, []
    if not t["receipt_present"]:
        p += 1; ev.append(f"TX:{t['id']}:missing_receipt")
    if t["invoice_mismatch"]:
        p += 1; ev.append(f"TX:{t['id']}:invoice_amount")
    if t["outside_hours"]:
        p += 1; ev.append(f"TX:{t['id']}:transaction_time")
    return output("Employee", p, ev, "Checks available receipts, invoice support and purchase timing.")


def manager_agent(t: dict) -> Assessment:
    p, ev = 0, []
    if not t["manager_approved"]:
        p += 2; ev.append(f"TX:{t['id']}:manager_approval")
    if t["split_suspected"]:
        p += 2; ev.append(f"GROUP:{t['split_group']}:aggregate_{t['split_total']:.2f}")
    if t["amount"] > 10000:
        p += 1; ev.append(f"TX:{t['id']}:amount_over_10000")
    return output("Manager", p, ev, "Checks approval and potentially split departmental spending.")


def cfo_agent(t: dict) -> Assessment:
    p, ev = 0, []
    if t["amount"] >= 5000 and not t["cfo_approved"]:
        p += 2; ev.append(f"TX:{t['id']}:cfo_approval")
    if t["split_suspected"]:
        p += 2; ev.append(f"GROUP:{t['split_group']}:approval_threshold")
    if t["invoice_mismatch"]:
        p += 1; ev.append(f"TX:{t['id']}:invoice_mismatch")
    if not t["is_established"]:
        p += 1; ev.append(f"VENDOR:{t['vendor_id']}:new_vendor")
    return output("CFO", p, ev, "Checks financial policy thresholds and invoice/vendor controls.")


def fraud_agent(t: dict) -> Assessment:
    p, ev = 0, []
    if t["split_suspected"]:
        p += 2; ev.append(f"GROUP:{t['split_group']}:split_pattern")
    if t["matching_transaction_ids"]:
        p += 2; ev.append("TX:" + ",".join(t["matching_transaction_ids"]))
    if not t["is_established"]:
        p += 1; ev.append(f"VENDOR:{t['vendor_id']}:new_vendor")
    if t["outside_hours"]:
        p += 1; ev.append(f"TX:{t['id']}:after_hours")
    if t["invoice_mismatch"]:
        p += 1; ev.append(f"TX:{t['id']}:amount_mismatch")
    return output("Fraud Analysis", p, ev, "Checks transaction anomalies and cross-record patterns.")


def review(conn: sqlite3.Connection, tx_id: str) -> dict:
    """Independent assessment -> evidence exchange -> deterministic consensus."""
    t = transaction_context(conn, tx_id)
    assessment = [f(t) for f in (employee_agent, manager_agent, cfo_agent, fraud_agent)]
    high_count = sum(v.risk == "HIGH" for v in assessment)
    if high_count >= 3:
        final_risk, recommendation = "HIGH", "Priority accountant review"
    elif any(v.risk != "LOW" for v in assessment):
        final_risk, recommendation = "MEDIUM", "Standard accountant review"
    else:
        final_risk, recommendation = "LOW", "Record and monitor"
    unique_risks = set(a.risk for a in assessment)
    disagreement = len(unique_risks) >= 3 or ("HIGH" in unique_risks and "LOW" in unique_risks)
    if disagreement and final_risk != "HIGH":
        recommendation = "Human review due to agent disagreement"
    agreement = round(max(sum(v.risk == rank for v in assessment) for rank in ("LOW", "MEDIUM", "HIGH")) / 4, 2)
    run_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    for a in assessment:
        conn.execute("""INSERT INTO agent_assessments
        (run_id, transaction_id, role, risk, support_score, rationale, evidence_json, created_at)
        VALUES (?,?,?,?,?,?,?,?)""", (run_id, tx_id, a.role, a.risk, a.support_score,
                                       a.rationale, json.dumps(a.evidence), now))
        conn.execute("""INSERT INTO agent_messages
        (run_id, transaction_id, sender_role, message, created_at)
        VALUES (?,?,?,?,?)""", (run_id, tx_id, a.role,
        f"Independent vote {a.risk}; evidence: {', '.join(a.evidence)}", now))
    conn.execute("""INSERT INTO consensus
    (run_id, transaction_id, final_risk, agreement, recommendation, created_at)
    VALUES (?,?,?,?,?,?)""", (run_id, tx_id, final_risk, agreement, recommendation, now))
    conn.commit()
    return {"run_id": run_id, "transaction_id": tx_id,
            "scenario_label_for_testing_only": t["planted_label"],
            "assessments": [asdict(a) for a in assessment],
            "discussion_round": "Evidence exchange logged; revised votes not implemented in Phase 2",
            "consensus": {"risk": final_risk, "agreement": agreement,
                          "disagreement": disagreement, "recommendation": recommendation}}


def main() -> None:
    parser = argparse.ArgumentParser(description="CSC 244 Phase 2 multi-agent risk prototype")
    parser.add_argument("--db", default="phase2_demo.sqlite", help="Output SQLite database path")
    parser.add_argument("--transaction", default=None, help="Evaluate one transaction ID")
    parser.add_argument("--json", default="phase2_results.json", help="Write JSON results here")
    args = parser.parse_args()
    conn = open_db(args.db)
    seed_demo(conn)
    txs = [args.transaction] if args.transaction else [r[0] for r in conn.execute("SELECT id FROM transactions ORDER BY id")]
    results = [review(conn, x) for x in txs]
    Path(args.json).write_text(json.dumps(results, indent=2), encoding="utf-8")
    print("CSC 244: role-based multi-agent financial risk prototype")
    for r in results:
        votes = ", ".join(a["role"] + ":" + a["risk"] for a in r["assessments"])
        print(f"{r['transaction_id']}: {r['consensus']['risk']} | {r['consensus']['recommendation']} | {votes}")
    print(f"Audited {len(results)} transaction(s) to {args.db}; JSON results: {args.json}")
    conn.close()


if __name__ == "__main__":
    main()
