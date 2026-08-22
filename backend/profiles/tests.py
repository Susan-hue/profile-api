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
        png_bytes = (
            b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR"
            b"\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89"
        )
        good_file = SimpleUploadedFile(
            "avatar.png", png_bytes, content_type="image/png"
        )
        res = self.client.post(self.avatar_url, {"avatar": good_file}, format="multipart")
        self.assertEqual(res.status_code, 200)


class RegistrationAPITests(APITestCase):
    def setUp(self):
        self.register_url = "/api/profile/register/"
        self.token_url = "/api/token/"

    def test_valid_registration_succeeds_creates_user_and_profile(self):
        payload = {
            "username": "newuser",
            "email": "newuser@example.com",
            "full_name": "New User",
            "password": "ValidStrongPassword123!",
        }
        res = self.client.post(self.register_url, payload)
        self.assertEqual(res.status_code, 201)
        self.assertEqual(res.data["display_name"], "New User")
        self.assertEqual(res.data["email"], "newuser@example.com")
        self.assertIn("id", res.data)
        self.assertNotIn("password", res.data)
        self.assertNotIn("token", res.data)

        self.assertTrue(User.objects.filter(username="newuser").exists())
        user = User.objects.get(username="newuser")
        self.assertEqual(user.profile.display_name, "New User")

    def test_duplicate_username_returns_400(self):
        User.objects.create_user(username="existinguser", email="existing@example.com", password="Pass1234Word!")
        payload = {
            "username": "existinguser",
            "email": "other@example.com",
            "full_name": "Test User",
            "password": "ValidStrongPassword123!",
        }
        res = self.client.post(self.register_url, payload)
        self.assertEqual(res.status_code, 400)
        self.assertIn("username", res.data)

    def test_duplicate_email_returns_400(self):
        User.objects.create_user(username="existinguser", email="existing@example.com", password="Pass1234Word!")
        payload = {
            "username": "uniqueusername",
            "email": "existing@example.com",
            "full_name": "Test User",
            "password": "ValidStrongPassword123!",
        }
        res = self.client.post(self.register_url, payload)
        self.assertEqual(res.status_code, 400)
        self.assertIn("email", res.data)

    def test_weak_password_returns_400(self):
        payload = {
            "username": "weakpassuser",
            "email": "weakpass@example.com",
            "full_name": "Weak Pass User",
            "password": "password123",
        }
        res = self.client.post(self.register_url, payload)
        self.assertEqual(res.status_code, 400)
        self.assertIn("password", res.data)

    def test_missing_required_field_returns_400(self):
        payload = {
            "username": "noemailuser",
            "full_name": "No Email User",
            "password": "ValidStrongPassword123!",
        }
        res = self.client.post(self.register_url, payload)
        self.assertEqual(res.status_code, 400)
        self.assertIn("email", res.data)

    def test_registration_credentials_can_obtain_token(self):
        payload = {
            "username": "loginuser",
            "email": "loginuser@example.com",
            "full_name": "Login User",
            "password": "ValidStrongPassword123!",
        }
        reg_res = self.client.post(self.register_url, payload)
        self.assertEqual(reg_res.status_code, 201)

        login_res = self.client.post(
            self.token_url,
            {"username": "loginuser", "password": "ValidStrongPassword123!"},
        )
        self.assertEqual(login_res.status_code, 200)
        self.assertIn("token", login_res.data)