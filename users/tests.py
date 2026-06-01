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

        user = CustomUser.objects.create_user(username='hosp_coord_user', password='pass123')
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

        user = CustomUser.objects.create_user(username='req_coord_user', password='pass123')
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

