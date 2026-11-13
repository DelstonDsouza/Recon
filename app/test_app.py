import os
import unittest
from unittest import mock

import app


class TestApp(unittest.TestCase):
    def test_healthz(self):
        status, _, body = app.route("/healthz")
        self.assertEqual(status, 200)
        self.assertEqual(body, "ok")

    def test_readyz(self):
        status, _, _ = app.route("/readyz")
        self.assertEqual(status, 200)

    def test_version(self):
        status, _, body = app.route("/version")
        self.assertEqual(status, 200)
        self.assertIn("version", body)

    def test_unknown_path(self):
        status, _, _ = app.route("/nope")
        self.assertEqual(status, 404)

    def test_metrics(self):
        status, _, body = app.route("/metrics")
        self.assertEqual(status, 200)
        self.assertIn("http_requests_total", body)

    def test_fail_rate_one_returns_500(self):
        with mock.patch.dict(os.environ, {"FAIL_RATE": "1"}):
            status, _, _ = app.route("/")
        self.assertEqual(status, 500)

    def test_fail_rate_zero_returns_200(self):
        with mock.patch.dict(os.environ, {"FAIL_RATE": "0"}):
            status, _, _ = app.route("/")
        self.assertEqual(status, 200)


if __name__ == "__main__":
    unittest.main()
