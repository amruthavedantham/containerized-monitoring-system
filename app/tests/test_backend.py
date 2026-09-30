import unittest
import sys
import os

# Add app/src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from app import app

class TestBackendAPI(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_health_endpoint(self):
        response = self.app.get('/health')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {"status": "ok"})

    def test_process_endpoint(self):
        response = self.app.get('/process')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {"result": "processed"})

    def test_error_endpoint(self):
        response = self.app.get('/error')
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.get_json(), {"error": "intentional failure"})

    def test_metrics_endpoint(self):
        response = self.app.get('/metrics')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"http_requests_total", response.data)
        self.assertIn(b"http_errors_total", response.data)

if __name__ == '__main__':
    unittest.main()
