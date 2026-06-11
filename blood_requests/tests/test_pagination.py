from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from blood_requests.models import BloodRequest, DonorResponse

User = get_user_model()


class RequestPaginationTests(TestCase):
    def setUp(self):
        self.seeker = User.objects.create_user(
            username="seeker_user",
            password="password123",
            role="seeker",
        )

        for index in range(25):
            BloodRequest.objects.create(
                requester=self.seeker,
                patient_name=f"Patient {index}",
                blood_group="O",
                rh_factor="+",
                units_required=2,
                hospital_name="City Hospital",
                hospital_address="Mumbai",
                status="open",
            )

    def test_request_list_is_paginated(self):
        response = self.client.get(reverse("request_list"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["requests_list"]), 20)
        self.assertEqual(response.context["requests_list"].paginator.count, 25)

        second_page = self.client.get(reverse("request_list"), {"page": 2})
        self.assertEqual(second_page.status_code, 200)
        self.assertEqual(len(second_page.context["requests_list"]), 5)


class RequestDetailPaginationTests(TestCase):
    def setUp(self):
        self.seeker = User.objects.create_user(
            username="seeker_user",
            password="password123",
            role="seeker",
        )
        self.request = BloodRequest.objects.create(
            requester=self.seeker,
            patient_name="Patient X",
            blood_group="A",
            rh_factor="+",
            units_required=2,
            hospital_name="General Hospital",
            hospital_address="Mumbai",
            status="open",
        )

        for index in range(12):
            donor = User.objects.create_user(
                username=f"donor_{index}",
                password="password123",
                role="donor",
            )
            DonorResponse.objects.create(
                blood_request=self.request,
                donor=donor,
                status="interested",
                message=f"Response {index}",
            )

    def test_request_detail_paginated_responses(self):
        response = self.client.get(reverse("request_detail", args=[self.request.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["responses_page"]), 10)
        self.assertEqual(response.context["responses_page"].paginator.count, 12)

        second_page = self.client.get(
            reverse("request_detail", args=[self.request.id]),
            {"responses_page": 2},
        )
        self.assertEqual(second_page.status_code, 200)
        self.assertEqual(len(second_page.context["responses_page"]), 2)
