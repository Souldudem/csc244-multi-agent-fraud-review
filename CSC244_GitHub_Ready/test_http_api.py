"""Added integration coverage: real HTTP endpoints on an ephemeral localhost server.

Authorship: packaging/integration tests added to the GitHub-ready compilation.
Do not attribute these tests to either student without their confirmation.
"""
import json
import tempfile
import threading
import unittest
from http.server import ThreadingHTTPServer
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from app import initialise, server_factory


class HttpApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.db_path = str(Path(cls.temp.name) / 'api.sqlite')
        initialise(cls.db_path)
        cls.http = ThreadingHTTPServer(('127.0.0.1', 0), server_factory(cls.db_path))
        cls.port = cls.http.server_address[1]
        cls.thread = threading.Thread(target=cls.http.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.http.shutdown()
        cls.http.server_close()
        cls.thread.join(timeout=4)
        cls.temp.cleanup()

    def get_json(self, path):
        with urlopen(f'http://127.0.0.1:{self.port}{path}', timeout=3) as response:
            self.assertEqual(response.status, 200)
            return json.load(response)

    def post_json(self, path, body):
        req = Request(f'http://127.0.0.1:{self.port}{path}',
                      data=json.dumps(body).encode('utf-8'),
                      headers={'Content-Type': 'application/json'}, method='POST')
        with urlopen(req, timeout=3) as response:
            self.assertEqual(response.status, 200)
            return json.load(response)

    def test_01_dashboard_get_exposes_review_data(self):
        d = self.get_json('/api/dashboard?transaction_id=F-001')
        self.assertEqual(d['active']['risk'], 'HIGH')
        self.assertEqual(len(d['active']['assessments']), 4)
        self.assertNotIn('planted_label', d['selected'])

    def test_02_static_frontend_is_served(self):
        with urlopen(f'http://127.0.0.1:{self.port}/', timeout=3) as response:
            self.assertEqual(response.status, 200)
            self.assertIn(b'html', response.read().lower())

    def test_03_review_post_adds_persistent_run(self):
        initial = self.get_json('/api/dashboard?transaction_id=F-001')
        before = initial['metrics']['total_runs']
        created = self.post_json('/api/review', {'transaction_id': 'F-001'})
        after = self.get_json('/api/dashboard?transaction_id=F-001')
        self.assertTrue(created['success'])
        self.assertEqual(created['run_id'], after['active']['run_id'])
        self.assertEqual(after['metrics']['total_runs'], before+1)

    def test_04_accountant_disposition_persists_over_http(self):
        d = self.get_json('/api/dashboard?transaction_id=V-001')
        run_id = d['active']['run_id']
        self.post_json('/api/accountant-review', {
            'run_id': run_id, 'decision': 'REQUEST_MORE_EVIDENCE',
            'notes': 'Verify onboarding record before disposition'})
        after = self.get_json('/api/dashboard?transaction_id=V-001')
        self.assertEqual(after['active']['human_review']['decision'], 'REQUEST_MORE_EVIDENCE')

    def test_05_invalid_request_is_rejected(self):
        req = Request(f'http://127.0.0.1:{self.port}/api/review',
                      data=b'{"transaction_id":"UNKNOWN"}',
                      headers={'Content-Type': 'application/json'}, method='POST')
        with self.assertRaises(HTTPError) as err:
            urlopen(req, timeout=3)
        self.assertEqual(err.exception.code, 400)


if __name__ == '__main__':
    unittest.main()
