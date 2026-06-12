from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from blood_requests.models import BloodRequest


User = get_user_model()


class CancelRequestSecurityTests(TestCase):
    def setUp(self):
        self.seeker = User.objects.create_user(
            username="seeker1",
            password="password123",
            role="seeker",
            city="Mumbai",
        )
        self.other_user = User.objects.create_user(
            username="donor1",
            password="password123",
            role="donor",
            city="Mumbai",
        )
        self.blood_request = BloodRequest.objects.create(
            requester=self.seeker,
            patient_name="Test Patient",
            patient_age=30,
            blood_group="A",
            rh_factor="+",
            units_required=2,
            hospital_name="General Hospital",
            hospital_address="Main Street",
            city="Mumbai",
            urgency_level="urgent",
        )

    def test_get_request_does_not_cancel_request(self):
        self.client.force_login(self.seeker)

        response = self.client.get(reverse("cancel_request", args=[self.blood_request.id]))

        self.blood_request.refresh_from_db()
        self.assertEqual(response.status_code, 405)
        self.assertEqual(self.blood_request.status, "open")

    def test_post_request_cancels_request(self):
        self.client.force_login(self.seeker)

        response = self.client.post(reverse("cancel_request", args=[self.blood_request.id]))

        self.blood_request.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.blood_request.status, "cancelled")
