"""
Tests for blood compatibility engine — 64 donor×recipient combinations.
Run with: python manage.py test blood_requests.tests.test_compatibility
"""
from django.test import TestCase
from utils.blood_compatibility import (
    get_compatible_donor_types,
    get_donation_priority,
    rank_donors,
    DONATION_MATRIX,
)
from unittest.mock import MagicMock


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
