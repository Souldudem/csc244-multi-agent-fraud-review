"""Run with: python -m unittest -v test_prototype.py"""
import unittest
from prototype import open_db, seed_demo, review


class PrototypeTests(unittest.TestCase):
    def setUp(self):
        self.db = open_db()
        seed_demo(self.db)

    def tearDown(self):
        self.db.close()

    def test_normal_case_low(self):
        result = review(self.db, "L-001")
        self.assertEqual(result["consensus"]["risk"], "LOW")
        self.assertEqual(len(result["assessments"]), 4)

    def test_blatant_controls_high(self):
        result = review(self.db, "F-001")
        self.assertEqual(result["consensus"]["risk"], "HIGH")
        self.assertGreaterEqual(sum(a["risk"] == "HIGH" for a in result["assessments"]), 3)

    def test_split_purchases_high(self):
        result = review(self.db, "S-001")
        self.assertEqual(result["consensus"]["risk"], "HIGH")

    def test_missing_receipt_review(self):
        result = review(self.db, "M-001")
        self.assertEqual(result["consensus"]["risk"], "MEDIUM")

    def test_audit_writes(self):
        result = review(self.db, "F-001")
        run_id = result["run_id"]
        n = self.db.execute("SELECT COUNT(*) FROM agent_assessments WHERE run_id=?", (run_id,)).fetchone()[0]
        m = self.db.execute("SELECT COUNT(*) FROM agent_messages WHERE run_id=?", (run_id,)).fetchone()[0]
        c = self.db.execute("SELECT COUNT(*) FROM consensus WHERE run_id=?", (run_id,)).fetchone()[0]
        self.assertEqual((n, m, c), (4, 4, 1))


if __name__ == "__main__":
    unittest.main()
