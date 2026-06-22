from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import Profile

User = get_user_model()

class ProfileAPITests(APITestCase):

    def setUp(self):
        # Create users
        self.user = User.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="testpassword123"
        )
        self.other_user = User.objects.create_user(
            username="otheruser",
            email="otheruser@example.com",
            password="testpassword123"
        )
        
        # URL lookups
        self.me_url = reverse("profile-me")
        self.avatar_url = reverse("profile-avatar")

    def test_unauthorized_access(self):
        """Ensure unauthenticated requests are rejected with 401 Unauthorized."""
        # GET profile
        response = self.client.get(self.me_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # PUT profile
        response = self.client.put(self.me_url, {"display_name": "New Name"})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # POST avatar
        response = self.client.post(self.avatar_url, {})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


    def test_get_profile_authorized(self):
        """Ensure an authenticated user can retrieve their profile details."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.me_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # By default, a profile is created on the fly with display_name = username
        self.assertEqual(response.data["display_name"], self.user.username)
        self.assertEqual(response.data["email"], self.user.email)
        self.assertIsNone(response.data["avatar"])

    def test_update_profile_valid(self):
        """Ensure an authenticated user can update their display name."""
        self.client.force_authenticate(user=self.user)
        response = self.client.put(self.me_url, {"display_name": "Updated Name"})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["display_name"], "Updated Name")
        
        # Verify persistence in database
        profile = Profile.objects.get(user=self.user)
        self.assertEqual(profile.display_name, "Updated Name")

    def test_update_profile_invalid_display_name(self):
        """Ensure display_name validation works and returns 400 on empty values."""
        self.client.force_authenticate(user=self.user)
        
        # Empty display name
        response = self.client.put(self.me_url, {"display_name": ""})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("display_name", response.data)
        
        # Whitespace-only display name
        response = self.client.put(self.me_url, {"display_name": "   "})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("display_name", response.data)

    def test_email_field_is_immutable(self):
        """Ensure that attempts to change the email field are ignored and it remains unchanged."""
        self.client.force_authenticate(user=self.user)
        
        # Try updating email
        response = self.client.put(
            self.me_url, 
            {"display_name": "Updated Name", "email": "hacked@example.com"}
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], "testuser@example.com")
        self.assertEqual(self.user.email, "testuser@example.com")
        
        # Verify that the user model's email is unchanged in database
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, "testuser@example.com")

    def test_avatar_upload_valid_types(self):
        """Ensure PNG, JPEG, and WEBP image uploads are accepted."""
        self.client.force_authenticate(user=self.user)
        
        formats = [
            ("avatar.png", "image/png"),
            ("avatar.jpg", "image/jpeg"),
            ("avatar.webp", "image/webp"),
        ]
        
        for filename, content_type in formats:
            image_file = SimpleUploadedFile(
                filename,
                b"dummy_image_data_here",
                content_type=content_type
            )
            response = self.client.post(
                self.avatar_url,
                {"avatar": image_file},
                format="multipart"
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertIsNotNone(response.data["avatar"])
            
            # Verify file exists on database profile
            profile = Profile.objects.get(user=self.user)
            self.assertTrue(profile.avatar.name.startswith("avatars/"))

    def test_avatar_upload_invalid_type(self):
        """Ensure file type validation rejects non-image formats (e.g. PDF)."""
        self.client.force_authenticate(user=self.user)
        
        pdf_file = SimpleUploadedFile(
            "document.pdf",
            b"fake_pdf_binary_content",
            content_type="application/pdf"
        )
        response = self.client.post(
            self.avatar_url,
            {"avatar": pdf_file},
            format="multipart"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("avatar", response.data)

    def test_avatar_upload_too_large(self):
        """Ensure files exceeding the 5MB size limit are rejected with 400."""
        self.client.force_authenticate(user=self.user)
        
        # Create a file just over 5MB
        limit_size = 5 * 1024 * 1024 + 100
        large_file = SimpleUploadedFile(
            "large_avatar.png",
            b"0" * limit_size,
            content_type="image/png"
        )
        response = self.client.post(
            self.avatar_url,
            {"avatar": large_file},
            format="multipart"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("avatar", response.data)

    def test_avatar_upload_no_file(self):
        """Ensure that POST requesting to avatar endpoint without a file returns 400."""
        self.client.force_authenticate(user=self.user)
        
        response = self.client.post(
            self.avatar_url,
            {},
            format="multipart"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("avatar", response.data)
