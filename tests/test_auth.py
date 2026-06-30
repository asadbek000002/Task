# Stdlib
import unittest
from unittest.mock import patch

# Fastapi
from fastapi.testclient import TestClient

# SQLAlchemy
from sqlalchemy import text

# Project
from core.database import engine
from main import app


class TestAuth(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    @classmethod
    def tearDownClass(cls):
        with engine.connect() as conn:
            conn.execute(text("TRUNCATE TABLE users CASCADE;"))
            conn.commit()

    # ---------- helpers ----------
    def register_user(self, email, username, password="password123"):
        return self.client.post(
            "/api/v1/auth/register",
            json={
                "email": email,
                "username": username,
                "full_name": "Test User",
                "password": password,
            },
        )

    def login_user(self, email, password="password123"):
        return self.client.post(
            "/api/v1/auth/login",
            json={"email": email, "password": password},
        )

    def auth_headers(self, email):
        response = self.login_user(email=email)
        token = response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}

    # ---------- tests ----------
    @patch("apps.users.router.send_verification_email_task.delay")
    def test_register_success(self, mock_send_email):
        email = "user1@example.com"
        username = "user1"
        response = self.register_user(email=email, username=username)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["email"], email)
        self.assertFalse(response.json()["is_verified"])
        mock_send_email.assert_called_once()

    @patch("apps.users.router.send_verification_email_task.delay")
    def test_register_duplicate_email_or_username(self, mock_send_email):
        email = "user2@example.com"
        username = "user2"
        self.register_user(email=email, username=username)

        response = self.register_user(email=email, username="another")
        self.assertEqual(response.status_code, 400)
        self.assertIn("already exists", response.json()["detail"])

        response = self.register_user(email="another@example.com", username=username)
        self.assertEqual(response.status_code, 400)
        self.assertIn("already exists", response.json()["detail"])

    @patch("apps.users.router.send_verification_email_task.delay")
    def test_login_success(self, mock_send_email):
        email = "user3@example.com"
        username = "user3"
        self.register_user(email=email, username=username)
        response = self.login_user(email=email)
        self.assertEqual(response.status_code, 200)
        self.assertIn("access_token", response.json())

    @patch("apps.users.router.send_verification_email_task.delay")
    def test_get_me_with_token(self, mock_send_email):
        email = "user4@example.com"
        username = "user4"
        self.register_user(email=email, username=username)
        headers = self.auth_headers(email=email)
        response = self.client.get("/api/v1/auth/me", headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["email"], email)

    def test_get_me_without_token(self):
        response = self.client.get("/api/v1/auth/me")
        self.assertEqual(response.status_code, 401)

    def test_login_wrong_credentials(self):
        response = self.login_user(email="nonexistent@example.com")
        self.assertEqual(response.status_code, 401)

    def test_get_me_invalid_token(self):
        response = self.client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer invalid_token"},
        )
        self.assertEqual(response.status_code, 401)
