from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from blood_requests.models import BloodRequest

User = get_user_model()


class CancelRequestSecurityTests(TestCase):
    def setUp(self):
        self.seeker = User.objects.create_user(
            username="seeker_user",
            password="password123",
            role="seeker",
            first_name="Sam",
            last_name="Seeker",
        )
        self.other = User.objects.create_user(
            username="other_user",
            password="password123",
            role="donor",
        )
        self.request = BloodRequest.objects.create(
            requester=self.seeker,
            patient_name="Patient Zero",
            blood_group="O",
            rh_factor="+",
            units_required=2,
            hospital_name="City Hospital",
            hospital_address="Mumbai",
            status="open",
        )
        self.cancel_url = reverse("cancel_request", args=[self.request.id])

    def test_cancel_requires_post(self):
        self.client.force_login(self.seeker)
        response = self.client.get(self.cancel_url)
        self.assertEqual(response.status_code, 405)
        self.request.refresh_from_db()
        self.assertEqual(self.request.status, "open")

    def test_seeker_can_cancel_with_post(self):
        self.client.force_login(self.seeker)
        response = self.client.post(self.cancel_url)
        self.assertRedirects(response, reverse("my_requests"))
        self.request.refresh_from_db()
        self.assertEqual(self.request.status, "cancelled")

    def test_non_owner_cannot_cancel(self):
        self.client.force_login(self.other)
        response = self.client.post(self.cancel_url)
        self.assertRedirects(response, reverse("home"))
        self.request.refresh_from_db()
        self.assertEqual(self.request.status, "open")
