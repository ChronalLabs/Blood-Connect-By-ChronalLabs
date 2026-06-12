from django.test import TestCase
from django.utils.crypto import get_random_string
from users.forms import UserRegistrationForm
from hospitals.models import HospitalProfile

class HospitalRegistrationTests(TestCase):
    def test_donor_registration_rejects_weak_password(self):
        form_data = {
            'username': 'donor_weak',
            'role': 'donor',
            'first_name': 'John',
            'last_name': 'Doe',
            'phone_number': '1234567890',
            'password1': 'Weak123!',
            'password2': 'Weak123!',
        }
        form = UserRegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('password1', form.errors)
        self.assertIn('12 characters long', form.errors['password1'][0])

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


class CoordinateValidationTests(TestCase):
    """Verify that latitude and longitude coordinate validations function correctly across models."""

    def test_custom_user_coordinate_validation(self):
        from django.core.exceptions import ValidationError
        from decimal import Decimal
        from users.models import CustomUser

        # Valid coordinates should clean without error
        user = CustomUser(
            username='test_coord_user',
            password='password123',
            latitude=Decimal('19.0760'),
            longitude=Decimal('72.8777')
        )
        user.full_clean()  # Should not raise

        # Invalid latitude (> 90) should raise ValidationError
        user.latitude = Decimal('95.000000')
        with self.assertRaises(ValidationError):
            user.full_clean()

        # Invalid longitude (< -180) should raise ValidationError
        user.latitude = Decimal('19.076000')
        user.longitude = Decimal('-185.000000')
        with self.assertRaises(ValidationError):
            user.full_clean()

    def test_hospital_profile_coordinate_validation(self):
        from django.core.exceptions import ValidationError
        from decimal import Decimal
        from users.models import CustomUser
        from hospitals.models import HospitalProfile

        user = CustomUser.objects.create_user(username='hosp_coord_user', password=get_random_string(32))
        hosp = HospitalProfile(
            user=user,
            hospital_name="City Hospital",
            address="Mumbai",
            city="Mumbai",
            state="Maharashtra",
            pincode="400001",
            contact_number="9999988888",
            latitude=Decimal('19.076000'),
            longitude=Decimal('72.877700')
        )
        hosp.full_clean()  # Should not raise

        # Invalid latitude (< -90) should raise ValidationError
        hosp.latitude = Decimal('-95.000000')
        with self.assertRaises(ValidationError):
            hosp.full_clean()

        # Invalid longitude (> 180) should raise ValidationError
        hosp.latitude = Decimal('19.076000')
        hosp.longitude = Decimal('185.000000')
        with self.assertRaises(ValidationError):
            hosp.full_clean()

    def test_blood_request_coordinate_validation(self):
        from django.core.exceptions import ValidationError
        from decimal import Decimal
        from users.models import CustomUser
        from blood_requests.models import BloodRequest

        user = CustomUser.objects.create_user(username='req_coord_user', password=get_random_string(32))
        req = BloodRequest(
            requester=user,
            patient_name="Savitri",
            blood_group="A",
            rh_factor="+",
            hospital_name="City Hospital",
            hospital_address="Mumbai",
            latitude=Decimal('19.076000'),
            longitude=Decimal('72.877700')
        )
        req.full_clean()  # Should not raise

        # Invalid latitude (> 90) should raise ValidationError
        req.latitude = Decimal('90.100000')
        with self.assertRaises(ValidationError):
            req.full_clean()

        # Invalid longitude (< -180) should raise ValidationError
        req.latitude = Decimal('19.076000')
        req.longitude = Decimal('-180.100000')
        with self.assertRaises(ValidationError):
            req.full_clean()
