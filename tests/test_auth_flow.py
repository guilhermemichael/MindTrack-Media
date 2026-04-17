import os
import tempfile
import unittest
from datetime import UTC, datetime

from app import create_app
from app.extensions import db
from app.models.enums import Classification, Emotion, MediaType
from app.models.media import Media
from app.models.user import User


class TestConfig:
    SECRET_KEY = "test-secret"
    SQLALCHEMY_DATABASE_URI = ""
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    TESTING = True


class AuthFlowTestCase(unittest.TestCase):
    def setUp(self):
        self.db_fd, self.db_path = tempfile.mkstemp(suffix=".db")
        TestConfig.SQLALCHEMY_DATABASE_URI = f"sqlite:///{self.db_path}"
        self.app = create_app(TestConfig)
        self.client = self.app.test_client()

        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
            db.engine.dispose()

        os.close(self.db_fd)
        os.unlink(self.db_path)

    def register_user(self, username="tester", email="tester@example.com", password="secret123"):
        return self.client.post(
            "/api/auth/register",
            json={"username": username, "email": email, "password": password},
        )

    def login_user(self, email="tester@example.com", password="secret123"):
        return self.client.post(
            "/api/auth/login",
            json={"email": email, "password": password},
        )

    def test_register_hashes_password_and_blocks_duplicate_email(self):
        response = self.register_user()
        self.assertEqual(response.status_code, 201)

        with self.app.app_context():
            user = User.query.filter_by(email="tester@example.com").first()
            self.assertIsNotNone(user)
            self.assertNotEqual(user.password_hash, "secret123")
            self.assertGreaterEqual(len(user.password_hash), 20)

        duplicate = self.register_user(username="tester2")
        self.assertEqual(duplicate.status_code, 400)

    def test_dashboard_redirects_when_not_authenticated(self):
        response = self.client.get("/dashboard", follow_redirects=False)

        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.headers["Location"].endswith("/login"))

    def test_api_routes_return_401_when_not_authenticated(self):
        media_response = self.client.post("/api/media/", json={})
        analytics_response = self.client.get("/api/analytics/summary")
        upload_response = self.client.post("/api/upload/csv")

        self.assertEqual(media_response.status_code, 401)
        self.assertEqual(media_response.get_json()["error"], "Nao autorizado")
        self.assertEqual(analytics_response.status_code, 401)
        self.assertEqual(upload_response.status_code, 401)

    def test_login_logout_and_protected_routes(self):
        self.register_user()

        invalid = self.login_user(password="wrong-password")
        self.assertEqual(invalid.status_code, 401)

        login_response = self.login_user()
        self.assertEqual(login_response.status_code, 200)

        dashboard_response = self.client.get("/dashboard")
        self.assertEqual(dashboard_response.status_code, 200)

        media_payload = {
            "name": "Interstellar",
            "media_type": "FILME",
            "duration_min": 169,
            "rating": 9.5,
            "classification": "POSITIVO",
            "mood_before": 5,
            "mood_after": 8,
            "primary_emotion": "MOTIVADO",
        }
        media_response = self.client.post("/api/media/", json=media_payload)
        self.assertEqual(media_response.status_code, 200)

        summary_response = self.client.get("/api/analytics/summary")
        self.assertEqual(summary_response.status_code, 200)
        summary_data = summary_response.get_json()
        self.assertEqual(summary_data["total_medias"], 1)
        self.assertEqual(summary_data["total_duration_min"], 169)
        self.assertGreater(summary_data["avg_rating"], 0)
        self.assertTrue(summary_data["insight"])
        self.assertEqual(len(summary_data["top_efficiency"]), 1)
        self.assertEqual(len(summary_data["recent_entries"]), 1)
        self.assertEqual(len(summary_data["mood_timeline"]), 1)

        logout_response = self.client.post("/api/auth/logout")
        self.assertEqual(logout_response.status_code, 200)

        blocked_response = self.client.get("/api/analytics/summary")
        self.assertEqual(blocked_response.status_code, 401)

    def test_analytics_only_returns_current_user_data(self):
        self.register_user()
        self.login_user()

        with self.app.app_context():
            other_user = User(username="other", email="other@example.com", password_hash="hash")
            db.session.add(other_user)
            db.session.commit()

            db.session.add(
                Media(
                    user_id=other_user.id,
                    name="Other user media",
                    media_type=MediaType.FILME,
                    duration_min=100,
                    rating=4.0,
                    classification=Classification.NEUTRO,
                    mood_before=4,
                    mood_after=4,
                    primary_emotion=Emotion.NEUTRO,
                    watched_at=datetime.now(UTC),
                    delta_mood=0,
                    time_efficiency=2.4,
                )
            )
            db.session.commit()

        own_media_payload = {
            "name": "My media",
            "media_type": "SERIE",
            "duration_min": 50,
            "rating": 8.0,
            "classification": "POSITIVO",
            "mood_before": 3,
            "mood_after": 7,
            "primary_emotion": "FELIZ",
        }
        self.client.post("/api/media/", json=own_media_payload)

        summary_response = self.client.get("/api/analytics/summary")
        self.assertEqual(summary_response.status_code, 200)

        data = summary_response.get_json()
        self.assertEqual(data["total_medias"], 1)
        self.assertEqual(len(data["top_efficiency"]), 1)
        self.assertEqual(data["top_efficiency"][0]["name"], "My media")
        self.assertEqual(data["dominant_type_label"], "Serie")


if __name__ == "__main__":
    unittest.main()
