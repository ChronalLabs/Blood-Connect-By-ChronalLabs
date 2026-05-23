from django.test import TestCase
from django.urls import reverse
from .models import CustomUser
from hospitals.models import HospitalProfile, BloodStock


class HospitalLoginTests(TestCase):
    def setUp(self):
        self.hospital_user = CustomUser.objects.create_user(
            username="hospital1",
            password="safepassword123",
            role="hospital",
            first_name="City",
            last_name="Hospital",
            email="hospital1@example.com",
        )
        self.hospital_profile = HospitalProfile.objects.create(
            user=self.hospital_user,
            hospital_name="City Hospital",
            address="123 Main St",
            city="Mumbai",
            state="Maharashtra",
            pincode="400001",
            contact_number="9999999999",
        )
        BloodStock.objects.create(hospital=self.hospital_profile)

        self.regular_user = CustomUser.objects.create_user(
            username="user1",
            password="safepassword123",
            role="donor",
            first_name="Regular",
            last_name="User",
        )

    def test_hospital_login_page_renders(self):
        response = self.client.get(reverse("hospital_login"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Hospital Login")

    def test_hospital_login_redirects_hospital_user(self):
        response = self.client.post(
            reverse("hospital_login"),
            {"username": "hospital1", "password": "safepassword123"},
        )
        self.assertRedirects(response, reverse("hospital_dashboard"))
        self.assertTrue(response.wsgi_request.user.is_authenticated)
        self.assertEqual(response.wsgi_request.user.role, "hospital")

    def test_hospital_login_blocks_non_hospital_user(self):
        response = self.client.post(
            reverse("hospital_login"),
            {"username": "user1", "password": "safepassword123"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Please login using the regular user login")
        self.assertFalse(response.wsgi_request.user.is_authenticated)
