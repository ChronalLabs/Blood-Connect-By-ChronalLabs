from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from donors.models import DonorProfile

User = get_user_model()


class DonorSearchAuthTests(TestCase):
    def setUp(self):
        self.seeker = User.objects.create_user(
            username="seeker_user",
            password="password123",
            role="seeker",
            first_name="Sam",
            last_name="Seeker",
        )
        self.donor = User.objects.create_user(
            username="donor_user",
            password="password123",
            role="donor",
            first_name="Dana",
            last_name="Donor",
            city="Mumbai",
            phone_number="9999999999",
        )
        DonorProfile.objects.create(
            user=self.donor,
            blood_group="O",
            rh_factor="+",
            age=28,
            availability_status="available",
        )

    def test_search_requires_login(self):
        response = self.client.get(reverse("search_donors"))
        self.assertRedirects(response, f"/users/login/?next={reverse('search_donors')}")

    def test_authenticated_user_can_search(self):
        self.client.force_login(self.seeker)
        response = self.client.get(reverse("search_donors"), {"city": "Mum"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Dana Donor")
        self.assertContains(response, "9999999999")
