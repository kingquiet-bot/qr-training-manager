import json
import os
import sqlite3
import tempfile
import unittest
from unittest import mock

import app


class _Response:
    status = 200

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        return False


class _Handler:
    def __init__(self, origin):
        self.headers = {"Origin": origin}
        self.sent_headers = {}

    def send_header(self, name, value):
        self.sent_headers[name] = value


class AppTests(unittest.TestCase):
    def test_generated_otp_is_six_digits(self):
        otp = app.generate_otp()
        self.assertEqual(len(otp), 6)
        self.assertTrue(otp.isdigit())

    def test_init_db_preserves_accounts_and_admin_settings(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            database = os.path.join(temp_dir, "attendance.db")
            with mock.patch.object(app, "DATABASE", database), mock.patch.dict(
                os.environ,
                {
                    "MASTER_SECRET": "test-master-secret",
                    "SMTP_EMAIL": "",
                    "SMTP_PASSWORD": "",
                    "BOOTSTRAP_ADMIN_EMAIL": "",
                    "BOOTSTRAP_ADMIN_PASSWORD": "",
                },
            ):
                app.init_db()
                db = sqlite3.connect(database)
                db.execute(
                    """INSERT INTO accounts
                       (id, email, password_hash, name, role, status, created_at)
                       VALUES ('acc_test', 'person@example.com', 'hash', 'Person',
                               'user', 'pending', '2026-01-01T00:00:00+00:00')"""
                )
                db.execute(
                    """INSERT INTO platform_settings (key, value)
                       VALUES ('platform_smtp_email', 'saved@example.com')"""
                )
                db.commit()
                db.close()

                app.init_db()
                db = sqlite3.connect(database)
                account = db.execute(
                    "SELECT email FROM accounts WHERE id = 'acc_test'"
                ).fetchone()
                smtp_email = db.execute(
                    "SELECT value FROM platform_settings WHERE key = 'platform_smtp_email'"
                ).fetchone()
                db.close()

                self.assertEqual(account[0], "person@example.com")
                self.assertEqual(smtp_email[0], "saved@example.com")

    def test_resend_delivery_uses_https_api(self):
        with mock.patch.object(app, "RESEND_API_KEY", "re_test"), mock.patch.object(
            app, "OTP_FROM_EMAIL", "Training <noreply@example.com>"
        ), mock.patch("app.urllib.request.urlopen", return_value=_Response()) as urlopen:
            sent = app.send_email_with_resend(
                "person@example.com", "Verification", "Code: 123456"
            )

        self.assertTrue(sent)
        request = urlopen.call_args.args[0]
        payload = json.loads(request.data)
        self.assertEqual(request.full_url, "https://api.resend.com/emails")
        self.assertEqual(request.get_header("Authorization"), "Bearer re_test")
        self.assertEqual(payload["to"], ["person@example.com"])

    def test_cors_allows_only_configured_origin(self):
        allowed = _Handler("https://admin.example.com")
        blocked = _Handler("https://attacker.example")
        with mock.patch.object(app, "CORS_ORIGINS", {"https://admin.example.com"}):
            app.send_cors_headers(allowed)
            app.send_cors_headers(blocked)

        self.assertEqual(
            allowed.sent_headers["Access-Control-Allow-Origin"],
            "https://admin.example.com",
        )
        self.assertNotIn("Access-Control-Allow-Origin", blocked.sent_headers)

    def test_render_requires_secure_bootstrap_configuration(self):
        with mock.patch.object(app, "IS_RENDER", True), mock.patch.object(
            app, "HOST", "0.0.0.0"
        ), mock.patch.object(app, "MASTER_SECRET", "stable-secret"), mock.patch.object(
            app, "RESEND_API_KEY", "re_test"
        ), mock.patch.object(
            app, "OTP_FROM_EMAIL", "noreply@example.com"
        ), mock.patch.dict(
            os.environ,
            {"BOOTSTRAP_ADMIN_EMAIL": "", "BOOTSTRAP_ADMIN_PASSWORD": ""},
        ):
            with self.assertRaisesRegex(RuntimeError, "BOOTSTRAP_ADMIN_EMAIL"):
                app.validate_runtime_config()
    def test_send_email_prefers_resend(self):
        with mock.patch("app.get_platform_email_settings", return_value={
            "resend_key": "re_test_key",
            "resend_from": "noreply@example.com",
            "smtp_email": "smtp@example.com",
            "smtp_pass": "pass",
            "smtp_server": "smtp.example.com",
            "smtp_port": 587
        }), mock.patch("app._send_via_resend", return_value=True) as resend_mock, mock.patch("app._send_via_smtp", return_value=True) as smtp_mock:
            sent = app.send_email("recipient@example.com", "Test Subject", "Test Body")
            
        self.assertTrue(sent)
        resend_mock.assert_called_once_with(
            "recipient@example.com", "Test Subject", "Test Body", "re_test_key", "noreply@example.com", None, None
        )
        smtp_mock.assert_not_called()

    def test_send_email_falls_back_to_smtp(self):
        with mock.patch("app.get_platform_email_settings", return_value={
            "resend_key": "",
            "resend_from": "",
            "smtp_email": "smtp@example.com",
            "smtp_pass": "pass",
            "smtp_server": "smtp.example.com",
            "smtp_port": 587
        }), mock.patch("app._send_via_resend", return_value=True) as resend_mock, mock.patch("app._send_via_smtp", return_value=True) as smtp_mock:
            sent = app.send_email("recipient@example.com", "Test Subject", "Test Body")
            
        self.assertTrue(sent)
        smtp_mock.assert_called_once_with(
            "recipient@example.com", "Test Subject", "Test Body", "smtp@example.com", "pass", "smtp.example.com", 587, None, None
        )
        resend_mock.assert_not_called()


if __name__ == "__main__":
    unittest.main()
