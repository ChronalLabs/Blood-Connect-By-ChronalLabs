from django.test import TestCase
from django.urls import reverse

from users.models import CustomUser


class DonorSearchAccessTests(TestCase):
    """Donor search should only be available to authenticated users."""

    def setUp(self):
        self.search_url = reverse("search_donors")

    def test_anonymous_users_are_redirected_to_login(self):
        response = self.client.get(self.search_url)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, f"/users/login/?next={self.search_url}")

    def test_authenticated_users_can_open_search(self):
        user = CustomUser.objects.create_user(
            username="donor_search_user",
            password="TestPass123!",
            role="donor",
        )
        self.client.force_login(user)

        response = self.client.get(self.search_url)

        self.assertEqual(response.status_code, 200)
