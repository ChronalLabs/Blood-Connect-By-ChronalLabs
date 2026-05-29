"""
BloodConnect Hospital Tests

Tests for the stock-based blood request fulfillment feature.
Follows the existing project test style (TestCase, no third-party test libs).
"""
from django.test import TestCase, Client
from django.urls import reverse

from users.models import CustomUser
from hospitals.models import HospitalProfile, BloodStock
from blood_requests.models import BloodRequest
from hospitals.services import fulfill_request_from_stock


# ── Helpers ───────────────────────────────────────────────────────────────────

def make_hospital_user(username="hosp1", hospital_name="City Hospital"):
    """Create a hospital CustomUser + HospitalProfile + BloodStock."""
    user = CustomUser.objects.create_user(
        username=username,
        password="TestPass123!",
        role="hospital",
        first_name="Test",
        last_name="Hospital",
    )
    hospital = HospitalProfile.objects.create(
        user=user,
        hospital_name=hospital_name,
        address="123 Test Street",
        city="Mumbai",
        state="Maharashtra",
        pincode="400001",
        contact_number="9876543210",
        verified=True,
    )
    blood_stock = BloodStock.objects.create(hospital=hospital)
    return user, hospital, blood_stock


def make_seeker_user(username="seeker1"):
    """Create a seeker CustomUser."""
    return CustomUser.objects.create_user(
        username=username,
        password="TestPass123!",
        role="seeker",
        first_name="Test",
        last_name="Seeker",
    )


def make_blood_request(requester, linked_hospital=None, blood_group="B", rh_factor="+", units=2):
    """Create an open BloodRequest."""
    return BloodRequest.objects.create(
        requester=requester,
        linked_hospital=linked_hospital,
        patient_name="Test Patient",
        blood_group=blood_group,
        rh_factor=rh_factor,
        units_required=units,
        hospital_name=linked_hospital.hospital_name if linked_hospital else "Unknown Clinic",
        hospital_address="123 Test St",
        urgency_level="urgent",
        status="open",
    )


# ── Service Layer Tests ───────────────────────────────────────────────────────

class FulfillFromStockServiceTests(TestCase):
    """Unit tests for hospitals.services.fulfill_request_from_stock."""

    def setUp(self):
        self.seeker_user = make_seeker_user()
        self.hosp_user, self.hospital, self.blood_stock = make_hospital_user()

    def test_fulfill_success_exact_match(self):
        """Hospital with sufficient B+ stock can fulfill a B+ request."""
        self.blood_stock.b_positive = 10
        self.blood_stock.save()

        blood_request = make_blood_request(
            self.seeker_user, linked_hospital=self.hospital,
            blood_group="B", rh_factor="+", units=2
        )

        success, message = fulfill_request_from_stock(self.hospital, blood_request)

        self.assertTrue(success)
        blood_request.refresh_from_db()
        self.assertEqual(blood_request.status, "fulfilled")
        self.assertEqual(blood_request.units_fulfilled, 2)
        self.assertIsNotNone(blood_request.fulfilled_at)
        self.blood_stock.refresh_from_db()
        self.assertEqual(self.blood_stock.b_positive, 8)  # 10 - 2

    def test_fulfill_insufficient_stock(self):
        """Fulfillment fails when stock is less than units required."""
        self.blood_stock.b_positive = 1  # only 1, need 2
        self.blood_stock.save()

        blood_request = make_blood_request(
            self.seeker_user, linked_hospital=self.hospital,
            blood_group="B", rh_factor="+", units=2
        )

        success, message = fulfill_request_from_stock(self.hospital, blood_request)

        self.assertFalse(success)
        self.assertIn("Insufficient", message)
        # Nothing should have changed in DB.
        blood_request.refresh_from_db()
        self.assertEqual(blood_request.status, "open")
        self.assertEqual(blood_request.units_fulfilled, 0)
        self.blood_stock.refresh_from_db()
        self.assertEqual(self.blood_stock.b_positive, 1)

    def test_fulfill_closed_request_rejected(self):
        """Fulfillment of an already-fulfilled request is rejected."""
        self.blood_stock.b_positive = 10
        self.blood_stock.save()

        blood_request = make_blood_request(
            self.seeker_user, linked_hospital=self.hospital,
            blood_group="B", rh_factor="+", units=2
        )
        blood_request.status = "fulfilled"
        blood_request.save()

        success, message = fulfill_request_from_stock(self.hospital, blood_request)

        self.assertFalse(success)
        self.blood_stock.refresh_from_db()
        self.assertEqual(self.blood_stock.b_positive, 10)  # unchanged

    def test_fulfill_zero_units_remaining(self):
        """Fulfillment is rejected when units_remaining is already 0."""
        self.blood_stock.o_negative = 10
        self.blood_stock.save()

        blood_request = make_blood_request(
            self.seeker_user, linked_hospital=self.hospital,
            blood_group="O", rh_factor="-", units=3
        )
        blood_request.units_fulfilled = 3  # already fully fulfilled
        blood_request.save()

        success, message = fulfill_request_from_stock(self.hospital, blood_request)

        self.assertFalse(success)
        self.assertIn("already been fully fulfilled", message)

    def test_fulfill_all_eight_blood_types(self):
        """Service correctly handles all 8 blood type field mappings."""
        blood_types = [
            ("A", "+", "a_positive"),
            ("A", "-", "a_negative"),
            ("B", "+", "b_positive"),
            ("B", "-", "b_negative"),
            ("O", "+", "o_positive"),
            ("O", "-", "o_negative"),
            ("AB", "+", "ab_positive"),
            ("AB", "-", "ab_negative"),
        ]
        for bg, rh, field_name in blood_types:
            with self.subTest(blood_type=f"{bg}{rh}"):
                # Reset stock for this sub-test.
                BloodStock.objects.filter(pk=self.blood_stock.pk).update(**{field_name: 5})
                self.blood_stock.refresh_from_db()

                blood_request = make_blood_request(
                    self.seeker_user, linked_hospital=self.hospital,
                    blood_group=bg, rh_factor=rh, units=2
                )
                success, _ = fulfill_request_from_stock(self.hospital, blood_request)
                self.assertTrue(success, f"Failed for {bg}{rh}")
                self.blood_stock.refresh_from_db()
                self.assertEqual(getattr(self.blood_stock, field_name), 3)  # 5 - 2


# ── View / Integration Tests ──────────────────────────────────────────────────

class FulfillRequestViewTests(TestCase):
    """Integration tests for the hospitals.views.fulfill_request view."""

    def setUp(self):
        self.client = Client()
        self.seeker_user = make_seeker_user()
        self.hosp_user, self.hospital, self.blood_stock = make_hospital_user()
        self.blood_stock.a_positive = 10
        self.blood_stock.save()

        self.blood_request = make_blood_request(
            self.seeker_user, linked_hospital=self.hospital,
            blood_group="A", rh_factor="+", units=3
        )
        self.fulfill_url = reverse("fulfill_request", kwargs={"request_id": self.blood_request.pk})

    def test_fulfill_requires_login(self):
        """Anonymous users are redirected to the login page."""
        response = self.client.post(self.fulfill_url)
        self.assertRedirects(response, f"/users/login/?next={self.fulfill_url}")

    def test_fulfill_denied_for_non_hospital_role(self):
        """Seekers cannot access the fulfill view."""
        self.client.login(username="seeker1", password="TestPass123!")
        response = self.client.post(self.fulfill_url)
        # Role check redirects to home.
        self.assertRedirects(response, reverse("home"))

    def test_fulfill_denied_for_wrong_hospital(self):
        """A different hospital cannot fulfill requests linked to another."""
        _, other_hospital, _ = make_hospital_user(username="hosp2", hospital_name="Other Hospital")
        self.client.login(username="hosp2", password="TestPass123!")
        response = self.client.post(self.fulfill_url)
        # Should be redirected to the detail page with an error message.
        self.assertRedirects(response, reverse("request_detail", kwargs={"pk": self.blood_request.pk}))

    def test_fulfill_get_not_allowed(self):
        """GET requests to the fulfill view are rejected (405 Method Not Allowed)."""
        self.client.login(username="hosp1", password="TestPass123!")
        response = self.client.get(self.fulfill_url)
        self.assertEqual(response.status_code, 405)

    def test_fulfill_success_via_view(self):
        """Authenticated hospital with sufficient stock successfully fulfills."""
        self.client.login(username="hosp1", password="TestPass123!")
        response = self.client.post(self.fulfill_url)
        self.assertRedirects(response, reverse("request_detail", kwargs={"pk": self.blood_request.pk}))
        self.blood_request.refresh_from_db()
        self.assertEqual(self.blood_request.status, "fulfilled")
        self.blood_stock.refresh_from_db()
        self.assertEqual(self.blood_stock.a_positive, 7)  # 10 - 3


# ── Hospital Info API Tests ───────────────────────────────────────────────────

class HospitalInfoApiTests(TestCase):
    """Tests for the public hospital JSON endpoint used by auto-fill JS."""

    def setUp(self):
        self.client = Client()
        _, self.hospital, _ = make_hospital_user()
        self.url = reverse("hospital_info_api", kwargs={"pk": self.hospital.pk})

    def test_returns_json_for_verified_hospital(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["name"], self.hospital.hospital_name)
        self.assertEqual(data["city"], self.hospital.city)
        self.assertIn("address", data)
        self.assertIn("contact", data)

    def test_returns_404_for_unverified_hospital(self):
        _, unverified, _ = make_hospital_user(username="hosp_unverified", hospital_name="Unverified Clinic")
        unverified.verified = False
        unverified.save()
        url = reverse("hospital_info_api", kwargs={"pk": unverified.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_does_not_expose_sensitive_fields(self):
        """The API must not leak user, registration number, or employee data."""
        response = self.client.get(self.url)
        data = response.json()
        self.assertNotIn("registration_number", data)
        self.assertNotIn("user", data)
        self.assertNotIn("employees", data)
