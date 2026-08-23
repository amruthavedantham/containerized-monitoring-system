import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import app, compute_prediction

class TestMLService(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_ml_health(self):
        response = self.app.get('/health')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()['status'], 'ok')

    def test_predict_get_default(self):
        response = self.app.get('/predict')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn('anomaly_score', data)
        self.assertIn('risk_level', data)
        self.assertIn('risk_code', data)

    def test_predict_post_features(self):
        features = {
            "request_rate_per_sec": 8.5,
            "error_rate_per_sec": 0.0,
            "p90_latency_seconds": 0.21,
            "requests_in_progress": 3.0
        }
        response = self.app.post('/predict', json={"features": features})
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['risk_level'], 'Normal')

    def test_compute_prediction_high_risk(self):
        # All zeros feature vector produces High Risk (out of baseline bounds)
        features = {
            "request_rate_per_sec": 0.0,
            "error_rate_per_sec": 0.0,
            "p90_latency_seconds": 0.01,
            "requests_in_progress": 0.0
        }
        result = compute_prediction(features)
        self.assertGreaterEqual(result['anomaly_score'], 0.75)
        self.assertEqual(result['risk_level'], 'High Risk')
        self.assertEqual(result['risk_code'], 2)

if __name__ == '__main__':
    unittest.main()
