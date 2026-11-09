"""Integration tests for the live dashboard's database-backed behavior."""
import tempfile
import unittest
from pathlib import Path
from app import dashboard_data, initialise, save_human_review
from prototype import open_db, review

class DashboardTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.dbpath=str(Path(self.tmp.name)/'test-dashboard.sqlite')
        initialise(self.dbpath)

    def tearDown(self):
        self.tmp.cleanup()

    def test_starts_with_reviewed_transactions(self):
        d=dashboard_data(self.dbpath, 'F-001')
        self.assertEqual(d['metrics']['transactions'],6)
        self.assertEqual(d['metrics']['total_runs'],6)
        self.assertEqual(d['metrics']['agent_assessments'],24)
        self.assertEqual((d['metrics']['HIGH'],d['metrics']['MEDIUM'],d['metrics']['LOW']),(3,2,1))

    def test_selected_record_is_from_database(self):
        d=dashboard_data(self.dbpath, 'S-001')
        self.assertEqual(d['selected']['split_total'],9500.0)
        self.assertEqual(d['active']['risk'],'HIGH')
        self.assertEqual(len(d['active']['messages']),4)

    def test_review_run_is_saved(self):
        db=open_db(self.dbpath)
        try:
            new_run=review(db,'F-001')
        finally:
            db.close()
        d=dashboard_data(self.dbpath,'F-001')
        self.assertEqual(d['active']['run_id'],new_run['run_id'])
        self.assertEqual(d['metrics']['total_runs'],7)

    def test_human_decision_is_persisted(self):
        run_id=dashboard_data(self.dbpath,'V-001')['active']['run_id']
        save_human_review(self.dbpath,run_id,'REQUEST_MORE_EVIDENCE','Check new-vendor registration')
        h=dashboard_data(self.dbpath,'V-001')['active']['human_review']
        self.assertEqual(h['decision'],'REQUEST_MORE_EVIDENCE')
        self.assertIn('new-vendor',h['reviewer_notes'])

    def test_invalid_case_and_decision_rejected(self):
        with self.assertRaises(ValueError):
            dashboard_data(self.dbpath,'NOT_A_CASE')
        with self.assertRaises(ValueError):
            save_human_review(self.dbpath,'not-a-run','FRAUD_CONFIRMED','')

if __name__=='__main__':
    unittest.main()
