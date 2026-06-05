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
