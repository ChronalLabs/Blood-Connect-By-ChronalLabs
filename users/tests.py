from django.test import TestCase
from users.forms import UserRegistrationForm
from hospitals.models import HospitalProfile

class HospitalRegistrationTests(TestCase):
    def test_donor_registration_validation(self):
        # Verify donor fields validation
        form_data = {
            'username': 'donor_test',
            'role': 'donor',
            'first_name': 'John',
            'last_name': 'Doe',
            'phone_number': '1234567890',
            'password1': 'SecurePass2026!',
            'password2': 'SecurePass2026!',
        }
        form = UserRegistrationForm(data=form_data)
        self.assertTrue(form.is_valid(), form.errors)

    def test_hospital_registration_validation_missing_fields(self):
        # Verify hospital registration fails if hospital specific fields are missing
        form_data = {
            'username': 'hospital_test',
            'role': 'hospital',
            'first_name': 'Jane', # Contact person
            'last_name': 'Smith', # Designation
            'phone_number': '1234567890',
            'password1': 'SecurePass2026!',
            'password2': 'SecurePass2026!',
        }
        form = UserRegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('hospital_name', form.errors)
        self.assertIn('hospital_type', form.errors)
        self.assertIn('registration_number', form.errors)

    def test_hospital_registration_validation_success(self):
        # Verify hospital registration succeeds with all required fields
        form_data = {
            'username': 'hospital_test',
            'role': 'hospital',
            'first_name': 'Jane', # Contact person
            'last_name': 'Smith', # Designation
            'phone_number': '1234567890',
            'address': '123 Hospital St',
            'city': 'Mumbai',
            'state': 'Maharashtra',
            'pincode': '400001',
            'hospital_name': 'City Health Hospital',
            'hospital_type': 'private',
            'registration_number': 'HOSP-12345',
            'password1': 'SecurePass2026!',
            'password2': 'SecurePass2026!',
        }
        form = UserRegistrationForm(data=form_data)
        self.assertTrue(form.is_valid(), form.errors)


class SeedDataCommandTests(TestCase):
    """Verify that seed_data custom management command populates and clears correctly."""

    def test_seed_and_clear_command_lifecycle(self):
        from django.core.management import call_command
        from users.models import CustomUser
        from donors.models import DonorProfile
        from seekers.models import SeekerProfile
        from hospitals.models import HospitalProfile, BloodStock
        from blood_requests.models import BloodRequest

        # 1. Run seed command
        call_command('seed_data')

        # Check that expected users and objects were created
        self.assertTrue(CustomUser.objects.filter(username='demo_admin').exists())
        self.assertTrue(CustomUser.objects.filter(username='demo_hospital_mumbai_1').exists())
        self.assertTrue(CustomUser.objects.filter(username='demo_donor_mumbai_1').exists())
        self.assertTrue(CustomUser.objects.filter(username='demo_seeker_mumbai_1').exists())

        # Check profile count
        self.assertGreater(HospitalProfile.objects.count(), 0)
        self.assertGreater(DonorProfile.objects.count(), 0)
        self.assertGreater(SeekerProfile.objects.count(), 0)
        self.assertGreater(BloodStock.objects.count(), 0)
        self.assertGreater(BloodRequest.objects.count(), 0)

        # 2. Check Idempotency: Run seed command again and verify counts are stable
        user_count_before = CustomUser.objects.count()
        call_command('seed_data')
        user_count_after = CustomUser.objects.count()
        self.assertEqual(user_count_before, user_count_after, "Seeding is not idempotent; new users were created!")

        # 3. Clear data using the --clear flag
        call_command('seed_data', clear=True)

        # Verify all demo users and their profiles are removed
        self.assertFalse(CustomUser.objects.filter(username__startswith='demo_').exists())
        self.assertEqual(HospitalProfile.objects.filter(hospital_name__startswith='demo_').count(), 0)
        self.assertEqual(BloodRequest.objects.filter(requester__username__startswith='demo_').count(), 0)

