"""Local-only, zero-dependency dashboard for the CSC 244 Phase 2 prototype.

Start with: python app.py
Open http://127.0.0.1:8501
The evaluations are deterministic rule-based analyses, NOT autonomous LLMs.
"""
from __future__ import annotations

import argparse
import json
import sqlite3
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Lock
from urllib.parse import urlparse, parse_qs

from prototype import ROOT, open_db, review, seed_demo, transaction_context

ASSETS = {"/": ("dashboard.html", "text/html; charset=utf-8"),
          "/dashboard.css": ("dashboard.css", "text/css; charset=utf-8"),
          "/dashboard.js": ("dashboard.js", "text/javascript; charset=utf-8")}
DECISIONS = {"INVESTIGATE", "REQUEST_MORE_EVIDENCE", "CLOSE_AS_EXPLAINED"}
LOCK = Lock()


def initialise(db_path: str) -> None:
    with LOCK:
        db = open_db(db_path)
        try:
            seed_demo(db)
            # First launch gets real, reproducible, stored assessments for the six demo cases.
            # Later starts do not silently create duplicate assessment runs.
            n = db.execute("SELECT COUNT(*) FROM consensus").fetchone()[0]
            if not n:
                for row in db.execute("SELECT id FROM transactions ORDER BY id").fetchall():
                    review(db, row["id"])
        finally:
            db.close()


def dashboard_data(db_path: str, tx_id: str | None = None) -> dict:
    db = open_db(db_path)
    try:
        tx_rows = db.execute("""SELECT t.id,t.amount,t.transaction_time,t.planted_label,
        e.name AS employee_name,e.department,v.name AS vendor_name,
        (SELECT c.final_risk FROM consensus c WHERE c.transaction_id=t.id
            ORDER BY c.created_at DESC, c.rowid DESC LIMIT 1) AS current_risk,
        (SELECT c.run_id FROM consensus c WHERE c.transaction_id=t.id
            ORDER BY c.created_at DESC, c.rowid DESC LIMIT 1) AS latest_run
        FROM transactions t JOIN employees e ON e.id=t.employee_id
        JOIN vendors v ON v.id=t.vendor_id ORDER BY t.id""").fetchall()
        transactions = [dict(row) for row in tx_rows]
        if not transactions:
            raise ValueError("No seeded transactions")
        if tx_id is None:
            tx_id = "F-001"
        if tx_id not in {r["id"] for r in transactions}:
            raise ValueError(f"Unknown transaction ID: {tx_id}")
        record = transaction_context(db, tx_id)
        # Strip planted answer from the case view to prevent leaking test labels into agent judgement.
        record.pop("planted_label", None)
        latest = db.execute("""SELECT * FROM consensus WHERE transaction_id = ?
                           ORDER BY created_at DESC, rowid DESC LIMIT 1""", (tx_id,)).fetchone()
        active = None
        if latest:
            run_id = latest["run_id"]
            assessments = [dict(row) for row in db.execute("""SELECT role,risk,support_score,rationale,evidence_json,created_at
                        FROM agent_assessments WHERE run_id=? ORDER BY id""", (run_id,)).fetchall()]
            for a in assessments:
                a["evidence"] = json.loads(a.pop("evidence_json"))
            messages = [dict(row) for row in db.execute("""SELECT sender_role,message,created_at FROM agent_messages
                        WHERE run_id=? ORDER BY id""", (run_id,)).fetchall()]
            human = db.execute("""SELECT decision,reviewer_notes,reviewed_at FROM accountant_reviews
                           WHERE run_id=? ORDER BY id DESC LIMIT 1""", (run_id,)).fetchone()
            active = {"run_id":run_id,"risk":latest["final_risk"],"agreement":latest["agreement"],
                      "recommendation":latest["recommendation"],"created_at":latest["created_at"],
                      "assessments":assessments,"messages":messages,
                      "human_review":dict(human) if human else None}
        history = [dict(r) for r in db.execute("""SELECT run_id,final_risk,agreement,created_at FROM consensus
            WHERE transaction_id=? ORDER BY rowid DESC LIMIT 8""", (tx_id,)).fetchall()]
        counters = {k: sum(t["current_risk"] == k for t in transactions) for k in ("HIGH","MEDIUM","LOW")}
        n_agents = db.execute("SELECT COUNT(*) FROM agent_assessments").fetchone()[0]
        n_runs = db.execute("SELECT COUNT(*) FROM consensus").fetchone()[0]
        return {"transactions":transactions,"selected":record,"active":active,"history":history,
                "metrics": {**counters,"transactions":len(transactions),"total_runs":n_runs,"agent_assessments":n_agents},
                "data_type":"Synthetic demonstration data",
                "method":"Deterministic rule-based reviewers, not autonomous AI"}
    finally:
        db.close()


def save_human_review(db_path: str, run_id: str, decision: str, notes: str) -> None:
    if decision not in DECISIONS:
        raise ValueError("Invalid accountant decision")
    if not 1 <= len(run_id) <= 80 or not isinstance(notes, str) or len(notes) > 1000:
        raise ValueError("Review input exceeds allowed length")
    with LOCK:
        db = open_db(db_path)
        try:
            existing = db.execute("SELECT 1 FROM consensus WHERE run_id=?", (run_id,)).fetchone()
            if not existing:
                raise ValueError("Unknown run ID")
            db.execute("INSERT INTO accountant_reviews (run_id,decision,reviewer_notes,reviewed_at) VALUES (?,?,?,?)",
                       (run_id, decision, notes.strip(), datetime.now(timezone.utc).isoformat(timespec="seconds")))
            db.commit()
        finally:
            db.close()


def server_factory(db_path: str):
    class Handler(BaseHTTPRequestHandler):
        def _send_json(self, payload: dict, status: int = 200) -> None:
            data = json.dumps(payload, indent=2).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def do_GET(self):
            url = urlparse(self.path)
            if url.path == "/api/dashboard":
                try:
                    tx = parse_qs(url.query).get("transaction_id", [None])[0]
                    return self._send_json(dashboard_data(db_path, tx))
                except ValueError as exc:
                    return self._send_json({"error":str(exc)}, 400)
            if url.path in ASSETS:
                filename, mime = ASSETS[url.path]
                data = (ROOT / filename).read_bytes()
                self.send_response(200)
                self.send_header("Content-Type", mime)
                self.send_header("Cache-Control", "no-store")
                self.send_header("X-Content-Type-Options", "nosniff")
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                return self.wfile.write(data)
            return self._send_json({"error":"Not found"}, 404)

        def do_POST(self):
            url = urlparse(self.path)
            if url.path not in ("/api/review", "/api/accountant-review"):
                return self._send_json({"error":"Not found"}, 404)
            try:
                n = int(self.headers.get("Content-Length", "0"))
                if n <= 0 or n > 5000:
                    raise ValueError("Invalid request length")
                body = json.loads(self.rfile.read(n).decode("utf-8"))
                if not isinstance(body, dict):
                    raise ValueError("Expected JSON object")
                if url.path == "/api/review":
                    tx_id = body.get("transaction_id", "")
                    if not isinstance(tx_id,str) or len(tx_id)>40:
                        raise ValueError("Invalid transaction ID")
                    with LOCK:
                        db = open_db(db_path)
                        try:
                            result = review(db, tx_id)
                        finally:
                            db.close()
                    return self._send_json({"success":True,"run_id":result["run_id"],"consensus":result["consensus"]})
                save_human_review(db_path, body.get("run_id", ""), body.get("decision", ""), body.get("notes", ""))
                return self._send_json({"success":True})
            except (ValueError, TypeError, json.JSONDecodeError) as exc:
                return self._send_json({"error":str(exc)}, 400)
            except sqlite3.Error:
                return self._send_json({"error":"Database error"}, 500)

        def log_message(self, fmt, *args):
            if self.path.startswith("/api/") and int(args[1]) >= 400 if len(args)>1 and str(args[1]).isdigit() else False:
                super().log_message(fmt, *args)
    return Handler


def main():
    parser = argparse.ArgumentParser(description="CSC 244 local screenshot-ready dashboard")
    parser.add_argument("--db", default=str(ROOT / "dashboard_demo.sqlite"))
    parser.add_argument("--port", type=int, default=8501)
    args = parser.parse_args()
    initialise(args.db)
    server = ThreadingHTTPServer(("127.0.0.1", args.port), server_factory(args.db))
    print("CSC 244 — Financial Risk Review Dashboard")
    print("Open: http://127.0.0.1:%s" % args.port)
    print("Synthetic transactions. Deterministic rule-based agents (not an LLM).")
    print("Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()

if __name__ == "__main__":
    main()
