"""
Tests for blood compatibility engine — 64 donor×recipient combinations.
Run with: python manage.py test blood_requests.tests.test_compatibility
"""
from django.test import TestCase
from django.urls import reverse
from utils.blood_compatibility import (
    get_compatible_donor_types,
    get_compatible_recipient_types,
    get_donation_priority,
    rank_donors,
    DONATION_MATRIX,
)
from unittest.mock import MagicMock
from datetime import date, timedelta

from django.core import mail
from django.test import override_settings

from blood_requests.models import BloodRequest, DonorNotification, DonorResponse
from blood_requests.services import notify_compatible_donors
from donors.models import DonorProfile
from users.models import CustomUser


ALL_TYPES = [('O','-'), ('O','+'), ('A','-'), ('A','+'), ('B','-'), ('B','+'), ('AB','-'), ('AB','+')]


def make_donor(bg, rh, lat=None, lon=None, can_donate=True):
    donor = MagicMock()
    donor.blood_group = bg
    donor.rh_factor = rh
    donor.user.latitude = lat
    donor.user.longitude = lon
    donor.can_donate.return_value = can_donate
    return donor


class CompatibilityMatrixTests(TestCase):
    """All 64 donor × recipient combinations."""

    def _assert_compatible(self, donor_bg, donor_rh, patient_bg, patient_rh):
        score = get_donation_priority(donor_bg, donor_rh, patient_bg, patient_rh)
        self.assertGreater(score, 0, f"{donor_bg}{donor_rh} should be compatible with {patient_bg}{patient_rh}")

    def _assert_incompatible(self, donor_bg, donor_rh, patient_bg, patient_rh):
        score = get_donation_priority(donor_bg, donor_rh, patient_bg, patient_rh)
        self.assertEqual(score, 0, f"{donor_bg}{donor_rh} should NOT be compatible with {patient_bg}{patient_rh}")

    def test_all_64_combinations(self):
        """Verify every cell in the compatibility matrix."""
        for donor in ALL_TYPES:
            for patient in ALL_TYPES:
                expected_compatible = patient in DONATION_MATRIX[donor]
                score = get_donation_priority(donor[0], donor[1], patient[0], patient[1])
                if expected_compatible:
                    self.assertGreater(score, 0, f"{donor} -> {patient} should be compatible")
                else:
                    self.assertEqual(score, 0, f"{donor} -> {patient} should be incompatible")

    def test_o_negative_universal_donor(self):
        """O- must be compatible with all 8 recipient types."""
        for patient in ALL_TYPES:
            self._assert_compatible('O', '-', patient[0], patient[1])

    def test_ab_positive_universal_recipient(self):
        """AB+ must accept donations from all 8 donor types."""
        for donor in ALL_TYPES:
            self._assert_compatible(donor[0], donor[1], 'AB', '+')

    def test_ab_positive_donor_restricted(self):
        """AB+ as donor can only donate to AB+."""
        for patient in ALL_TYPES:
            if patient == ('AB', '+'):
                self._assert_compatible('AB', '+', 'AB', '+')
            else:
                self._assert_incompatible('AB', '+', patient[0], patient[1])

    def test_rh_negative_patient_rejects_rh_positive(self):
        """RH- patients must never receive RH+ blood."""
        rh_negative_patients = [t for t in ALL_TYPES if t[1] == '-']
        rh_positive_donors = [t for t in ALL_TYPES if t[1] == '+']
        for patient in rh_negative_patients:
            for donor in rh_positive_donors:
                self._assert_incompatible(donor[0], donor[1], patient[0], patient[1])

    def test_exact_match_scores_100(self):
        for t in ALL_TYPES:
            self.assertEqual(get_donation_priority(t[0], t[1], t[0], t[1]), 100)

    def test_o_negative_to_non_o_negative_scores_90(self):
        for patient in ALL_TYPES:
            if patient != ('O', '-'):
                self.assertEqual(get_donation_priority('O', '-', patient[0], patient[1]), 90)

    def test_same_rh_different_abo_scores_80(self):
        # A- donating to AB- (same RH, different ABO, not O-)
        self.assertEqual(get_donation_priority('A', '-', 'AB', '-'), 80)
        self.assertEqual(get_donation_priority('B', '-', 'AB', '-'), 80)

    def test_cross_rh_compatible_scores_60(self):
        # A- donating to A+ (compatible but cross-RH)
        self.assertEqual(get_donation_priority('A', '-', 'A', '+'), 60)


class GetCompatibleDonorTypesTests(TestCase):

    def test_o_negative_patient_only_accepts_o_negative(self):
        types = get_compatible_donor_types('O', '-')
        self.assertEqual(types, [('O', '-')])

    def test_ab_positive_patient_accepts_all_8(self):
        types = get_compatible_donor_types('AB', '+')
        self.assertEqual(len(types), 8)
        for t in ALL_TYPES:
            self.assertIn(t, types)

    def test_a_positive_patient(self):
        types = get_compatible_donor_types('A', '+')
        expected = [('O','-'), ('O','+'), ('A','-'), ('A','+')]
        for t in expected:
            self.assertIn(t, types)
        # Must not include B types
        self.assertNotIn(('B', '+'), types)
        self.assertNotIn(('B', '-'), types)


class GetCompatibleRecipientTypesTests(TestCase):

    def test_o_negative_donor_can_fulfill_all_8_request_types(self):
        types = get_compatible_recipient_types('O', '-')
        self.assertEqual(types, DONATION_MATRIX[('O', '-')])
        self.assertEqual(len(types), 8)

    def test_ab_positive_donor_can_only_fulfill_ab_positive_requests(self):
        types = get_compatible_recipient_types('AB', '+')
        self.assertEqual(types, [('AB', '+')])

    def test_each_donor_type_matches_donation_matrix(self):
        for donor_type, recipient_types in DONATION_MATRIX.items():
            self.assertEqual(
                get_compatible_recipient_types(*donor_type),
                recipient_types,
            )


class RankDonorsTests(TestCase):

    def test_ranked_highest_score_first(self):
        donors = [
            make_donor('A', '+'),   # exact match for A+ patient → 100
            make_donor('O', '-'),   # universal donor → 90
            make_donor('A', '-'),   # same RH diff ABO → 60 (A- to A+)
        ]
        result = rank_donors(donors, 'A', '+')
        scores = [r['final_score'] for r in result]
        self.assertEqual(scores, sorted(scores, reverse=True))
        self.assertEqual(result[0]['compatibility_score'], 100)

    def test_incompatible_donors_excluded(self):
        donors = [make_donor('B', '+'), make_donor('O', '-')]
        result = rank_donors(donors, 'O', '-')
        # B+ cannot donate to O-, only O- can
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['donor'].blood_group, 'O')

    def test_distance_cutoff_excludes_far_donors(self):
        near = make_donor('O', '-', lat=19.0, lon=72.8)
        far = make_donor('O', '-', lat=28.6, lon=77.2)  # ~1400 km away
        result = rank_donors([near, far], 'A', '+', patient_lat=19.0, patient_lon=72.8, radius_km=50)
        self.assertEqual(len(result), 1)
        self.assertAlmostEqual(result[0]['distance_km'], 0.0, places=0)

    def test_empty_when_no_compatible_donors(self):
        donors = [make_donor('AB', '+')]
        result = rank_donors(donors, 'O', '-')
        self.assertEqual(result, [])

    def test_proximity_score_affects_final_score(self):
        near = make_donor('O', '-', lat=19.0, lon=72.8)
        far_but_valid = make_donor('O', '-', lat=19.3, lon=72.8)  # ~33 km
        result = rank_donors([near, far_but_valid], 'A', '+', patient_lat=19.0, patient_lon=72.8, radius_km=50)
        self.assertEqual(len(result), 2)
        self.assertGreater(result[0]['final_score'], result[1]['final_score'])


class DonorRequestMatchingTests(TestCase):

    def setUp(self):
        self.seeker = CustomUser.objects.create_user(
            username='seeker',
            password='password123',
            role='seeker',
        )

    def _create_donor(self, blood_group, rh_factor, **profile_kwargs):
        user = CustomUser.objects.create_user(
            username=f'donor_{blood_group}{rh_factor}'.replace('+', 'pos').replace('-', 'neg'),
            password='password123',
            role='donor',
        )
        profile = DonorProfile.objects.create(
            user=user,
            blood_group=blood_group,
            rh_factor=rh_factor,
            age=30,
            availability_status='available',
            **profile_kwargs,
        )
        return user, profile

    def _create_request(self, blood_group, rh_factor, **request_kwargs):
        return BloodRequest.objects.create(
            requester=self.seeker,
            patient_name=f'{blood_group}{rh_factor} Patient',
            blood_group=blood_group,
            rh_factor=rh_factor,
            units_required=1,
            hospital_name='City Hospital',
            hospital_address='Main Road',
            status='open',
            **request_kwargs,
        )

    def test_o_negative_donor_dashboard_shows_all_compatible_requests(self):
        donor_user, _ = self._create_donor('O', '-')
        compatible_request = self._create_request('AB', '+')
        exact_request = self._create_request('O', '-')

        self.client.force_login(donor_user)
        response = self.client.get(reverse('donor_dashboard'))

        self.assertEqual(response.status_code, 200)
        self.assertCountEqual(
            list(response.context['open_requests']),
            [compatible_request, exact_request],
        )

    def test_ab_positive_donor_dashboard_hides_incompatible_requests(self):
        donor_user, _ = self._create_donor('AB', '+')
        compatible_request = self._create_request('AB', '+')
        self._create_request('A', '+')

        self.client.force_login(donor_user)
        response = self.client.get(reverse('donor_dashboard'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context['open_requests']), [compatible_request])

    def test_direct_response_rejects_incompatible_blood_type(self):
        donor_user, _ = self._create_donor('AB', '+')
        incompatible_request = self._create_request('O', '-')

        self.client.force_login(donor_user)
        response = self.client.get(reverse('respond_to_request', args=[incompatible_request.id]))

        self.assertRedirects(response, reverse('donor_dashboard'))
        self.assertFalse(DonorResponse.objects.exists())

    def test_direct_response_rejects_donor_in_cooldown(self):
        donor_user, _ = self._create_donor(
            'O',
            '-',
            last_blood_donation_date=date.today() - timedelta(days=30),
        )
        compatible_request = self._create_request('A', '+')

        self.client.force_login(donor_user)
        response = self.client.get(reverse('respond_to_request', args=[compatible_request.id]))

        self.assertRedirects(response, reverse('donor_dashboard'))
        self.assertFalse(DonorResponse.objects.exists())

    def test_direct_response_creates_response_for_eligible_compatible_donor(self):
        donor_user, _ = self._create_donor('O', '-')
        compatible_request = self._create_request('A', '+')

        self.client.force_login(donor_user)
        response = self.client.get(reverse('respond_to_request', args=[compatible_request.id]))

        self.assertRedirects(response, reverse('donor_dashboard'))
        self.assertTrue(
            DonorResponse.objects.filter(
                donor=donor_user,
                blood_request=compatible_request,
                status='interested',
            ).exists()
        )


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class DonorNotificationTests(TestCase):

    def setUp(self):
        self.seeker = CustomUser.objects.create_user(
            username='notification_seeker',
            password='password123',
            role='seeker',
        )

    def _create_donor(
        self,
        username,
        blood_group,
        rh_factor,
        email='donor@example.com',
        availability_status='available',
        last_blood_donation_date=None,
        city='Mumbai',
    ):
        user = CustomUser.objects.create_user(
            username=username,
            password='password123',
            role='donor',
            email=email,
            city=city,
        )
        profile = DonorProfile.objects.create(
            user=user,
            blood_group=blood_group,
            rh_factor=rh_factor,
            age=30,
            availability_status=availability_status,
            last_blood_donation_date=last_blood_donation_date,
        )
        return user, profile

    def _create_request(self, blood_group='A', rh_factor='+', **request_kwargs):
        return BloodRequest.objects.create(
            requester=self.seeker,
            patient_name='Notification Patient',
            blood_group=blood_group,
            rh_factor=rh_factor,
            units_required=1,
            hospital_name='City Hospital',
            hospital_address='Main Road',
            hospital_contact='9999999999',
            city='Mumbai',
            status='open',
            **request_kwargs,
        )

    def test_notifies_only_eligible_compatible_donors(self):
        eligible_user, _ = self._create_donor('eligible_o_neg', 'O', '-', email='eligible@example.com')
        self._create_donor('incompatible_b_pos', 'B', '+', email='incompatible@example.com')
        self._create_donor('unavailable_o_pos', 'O', '+', email='unavailable@example.com', availability_status='unavailable')
        self._create_donor(
            'cooldown_a_pos',
            'A',
            '+',
            email='cooldown@example.com',
            last_blood_donation_date=date.today() - timedelta(days=30),
        )
        blood_request = self._create_request('A', '+')

        notifications = notify_compatible_donors(blood_request)

        self.assertEqual(len(notifications), 1)
        self.assertEqual(notifications[0].donor, eligible_user)
        self.assertEqual(notifications[0].status, 'sent')
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('A+', mail.outbox[0].subject)

    def test_does_not_send_duplicate_notifications_for_same_request(self):
        donor_user, _ = self._create_donor('duplicate_o_neg', 'O', '-', email='duplicate@example.com')
        blood_request = self._create_request('A', '+')

        first_notifications = notify_compatible_donors(blood_request)
        second_notifications = notify_compatible_donors(blood_request)

        self.assertEqual(len(first_notifications), 1)
        self.assertEqual(second_notifications, [])
        self.assertEqual(DonorNotification.objects.filter(donor=donor_user, blood_request=blood_request).count(), 1)
        self.assertEqual(len(mail.outbox), 1)

    def test_skips_email_when_donor_has_no_email_address(self):
        donor_user, _ = self._create_donor('no_email_o_neg', 'O', '-', email='')
        blood_request = self._create_request('A', '+')

        notifications = notify_compatible_donors(blood_request)

        self.assertEqual(len(notifications), 1)
        self.assertEqual(notifications[0].donor, donor_user)
        self.assertEqual(notifications[0].status, 'skipped')
        self.assertEqual(len(mail.outbox), 0)

    def test_prefers_same_city_donors_before_other_compatible_donors(self):
        same_city_user, _ = self._create_donor('same_city_o_neg', 'O', '-', email='same@example.com', city='Mumbai')
        self._create_donor('other_city_a_pos', 'A', '+', email='other@example.com', city='Delhi')
        blood_request = self._create_request('A', '+', city='Mumbai')

        notifications = notify_compatible_donors(blood_request)

        self.assertEqual(notifications[0].donor, same_city_user)
        self.assertEqual(mail.outbox[0].to, ['same@example.com'])

    def test_create_request_triggers_donor_notifications(self):
        donor_user, _ = self._create_donor('flow_o_neg', 'O', '-', email='flow@example.com')
        self.client.force_login(self.seeker)

        response = self.client.post(reverse('create_request'), {
            'patient_name': 'Flow Patient',
            'patient_age': 35,
            'blood_group': 'A',
            'rh_factor': '+',
            'units_required': 1,
            'hospital_name': 'City Hospital',
            'hospital_address': 'Main Road',
            'hospital_contact': '9999999999',
            'urgency_level': 'urgent',
            'city': 'Mumbai',
            'additional_notes': '',
            'required_by': '',
        })

        blood_request = BloodRequest.objects.get(patient_name='Flow Patient')
        self.assertRedirects(response, reverse('seeker_dashboard'))
        self.assertTrue(
            DonorNotification.objects.filter(
                donor=donor_user,
                blood_request=blood_request,
                status='sent',
            ).exists()
        )
        self.assertEqual(len(mail.outbox), 1)
