import json
import os
import unittest

os.environ.setdefault("DATABASE_URL", "sqlite://")
os.environ.setdefault("UPLOAD_FOLDER", "uploads")
os.environ.setdefault("SECRET_KEY", "smoke-secret-key-which-is-long-enough-1234")
os.environ.setdefault("JWT_SECRET_KEY", "smoke-jwt-secret-key-which-is-long-enough")
os.environ.setdefault("CLIENT_URL", "http://localhost:5173")

from app import create_app
from app.extensions import db, socketio
from app.models import User


class EduLinkSmokeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app()
        cls.client = cls.app.test_client()

    @classmethod
    def tearDownClass(cls):
        with cls.app.app_context():
            db.session.remove()
            db.engine.dispose()

    def auth(self, token):
        return {"Authorization": f"Bearer {token}"}

    def post_json(self, path, payload, token=None):
        headers = self.auth(token) if token else None
        return self.client.post(path, json=payload, headers=headers)

    def test_platform_flow(self):
        student = self.post_json(
            "/register",
            {
                "username": "student1",
                "email": "student1@example.com",
                "password": "StrongPass1",
                "location": "Nairobi",
                "school": "Central High",
                "role": "student",
            },
        )
        self.assertEqual(student.status_code, 201, student.get_data(as_text=True))
        student_data = student.get_json()["data"]
        student_id = student_data["user"]["id"]
        student_access = student_data["tokens"]["access_token"]
        student_refresh = student_data["tokens"]["refresh_token"]

        leader = self.post_json(
            "/register",
            {
                "username": "leader1",
                "email": "leader1@example.com",
                "password": "StrongPass1",
                "location": "Mombasa",
                "school": "Central High",
                "role": "club_leader",
            },
        )
        self.assertEqual(leader.status_code, 201, leader.get_data(as_text=True))
        leader_data = leader.get_json()["data"]
        leader_id = leader_data["user"]["id"]
        leader_access = leader_data["tokens"]["access_token"]

        self.assertEqual(self.client.post("/refresh", headers=self.auth(student_refresh)).status_code, 200)
        self.assertEqual(self.client.put(f"/users/{student_id}", json={"bio": "Physics club member"}, headers=self.auth(student_access)).status_code, 200)
        self.assertEqual(self.client.post(f"/users/{student_id}/follow", headers=self.auth(leader_access)).status_code, 200)
        self.assertEqual(self.client.delete(f"/users/{student_id}/follow", headers=self.auth(leader_access)).status_code, 200)

        schools = self.client.get("/schools")
        self.assertEqual(schools.status_code, 200)
        school_id = schools.get_json()["data"][0]["id"]
        self.assertEqual(self.client.post(f"/schools/{school_id}/join", headers=self.auth(leader_access)).status_code, 200)

        club = self.post_json("/clubs", {"name": "Robotics Club", "description": "Builds science fair robots", "school_id": school_id}, leader_access)
        self.assertEqual(club.status_code, 201, club.get_data(as_text=True))
        club_id = club.get_json()["data"]["id"]
        self.assertEqual(self.client.post(f"/clubs/{club_id}/join", headers=self.auth(student_access)).status_code, 200)
        self.assertEqual(self.client.post(f"/clubs/{club_id}/members/{student_id}/approve", headers=self.auth(leader_access)).status_code, 200)

        post = self.client.post(
            "/posts",
            data={"title": "Solar Tracker", "description": "Automatic panel alignment project", "code_snippet": 'print("solar")', "club_id": str(club_id)},
            headers=self.auth(student_access),
        )
        self.assertEqual(post.status_code, 201, post.get_data(as_text=True))
        post_id = post.get_json()["data"]["id"]

        for path in [
            "/posts?feed=global&sort=latest",
            "/posts?feed=global&sort=trending",
            "/search?q=solar",
            f"/chats/threads/{student_id}",
            "/notifications",
            "/dashboard",
        ]:
            response = self.client.get(path, headers=self.auth(student_access) if path.startswith("/notifications") or path.startswith("/dashboard") else self.auth(leader_access) if "/chats/" in path else None)
            self.assertEqual(response.status_code, 200, f"{path} -> {response.get_data(as_text=True)}")

        self.assertEqual(self.client.post(f"/posts/{post_id}/like", headers=self.auth(leader_access)).status_code, 200)
        self.assertEqual(self.post_json(f"/posts/{post_id}/comments", {"content": "Impressive work"}, leader_access).status_code, 201)
        self.assertEqual(self.client.post(f"/posts/{post_id}/share", headers=self.auth(leader_access)).status_code, 200)
        self.assertEqual(self.client.post(f"/posts/{post_id}/bookmark", headers=self.auth(leader_access)).status_code, 200)
        self.assertEqual(self.post_json(f"/chats/threads/{student_id}/messages", {"body": "Hello from the club lead"}, leader_access).status_code, 201)

        socket_client = socketio.test_client(self.app, flask_test_client=self.client)
        socket_client.emit("authenticate", {"token": leader_access})
        self.assertTrue(any(event["name"] == "authenticated" for event in socket_client.get_received()))
        socket_client.emit("join_club", {"club_id": club_id})
        socket_client.emit("club_message", {"sender_id": leader_id, "club_id": club_id, "body": "Realtime hello"})
        self.assertTrue(any(event["name"] == "message_sent" for event in socket_client.get_received()))
        socket_client.disconnect()

        self.assertEqual(self.client.post("/notifications/read-all", headers=self.auth(student_access)).status_code, 200)
        with self.app.app_context():
            user = db.session.get(User, leader_id)
            user.role = "admin"
            db.session.commit()
        admin = self.post_json("/login", {"email": "leader1@example.com", "password": "StrongPass1"})
        admin_access = admin.get_json()["data"]["tokens"]["access_token"]
        self.assertEqual(self.client.get("/admin/overview", headers=self.auth(admin_access)).status_code, 200)
        self.assertEqual(self.client.post("/logout", headers=self.auth(student_access)).status_code, 200)
        self.assertEqual(self.client.get("/users/me", headers=self.auth(student_access)).status_code, 401)


if __name__ == "__main__":
    unittest.main(verbosity=2)
