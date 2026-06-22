from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from django.core.files.uploadedfile import SimpleUploadedFile

User = get_user_model()

class ProfileAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="tester", email="tester@example.com", password="pass1234"
        )
        self.me_url = "/api/profile/me/"
        self.avatar_url = "/api/profile/avatar/"

    def test_unauthorized_request_rejected(self):
        res = self.client.get(self.me_url)
        self.assertEqual(res.status_code, 401)

    def test_authenticated_get_returns_profile(self):
        self.client.force_authenticate(self.user)
        res = self.client.get(self.me_url)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data["email"], "tester@example.com")

    def test_valid_update_succeeds(self):
        self.client.force_authenticate(self.user)
        res = self.client.put(self.me_url, {"display_name": "New Name"})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data["display_name"], "New Name")

    def test_email_is_immutable(self):
        self.client.force_authenticate(self.user)
        self.client.put(self.me_url, {"email": "hacker@example.com"})
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, "tester@example.com")

    def test_avatar_rejects_non_image(self):
        self.client.force_authenticate(self.user)
        bad_file = SimpleUploadedFile(
            "notes.txt", b"this is not an image", content_type="text/plain"
        )
        res = self.client.post(self.avatar_url, {"avatar": bad_file}, format="multipart")
        self.assertEqual(res.status_code, 400)

    def test_avatar_accepts_valid_image(self):
        self.client.force_authenticate(self.user)
        # minimal valid PNG header bytes
        png_bytes = (
            b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR"
            b"\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89"
        )
        good_file = SimpleUploadedFile(
            "avatar.png", png_bytes, content_type="image/png"
        )
        res = self.client.post(self.avatar_url, {"avatar": good_file}, format="multipart")
        self.assertEqual(res.status_code, 200)