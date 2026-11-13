import unittest

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


if __name__ == "__main__":
    unittest.main()
