from django import forms
from .models import HospitalProfile, BloodStock, HospitalEmployee

from bloodconnect.i18n import apply_field_labels


class HospitalProfileForm(forms.ModelForm):
    class Meta:
        model = HospitalProfile
        fields = ["hospital_name", "hospital_type", "registration_number", "address", "city", "state",
                  "pincode", "contact_number", "emergency_contact", "email", "website",
                  "blood_bank_available", "has_24hr_service", "description", "logo",
                  "verification_document", "latitude", "longitude"]
        widgets = {
            "address": forms.Textarea(attrs={"rows": 3}),
            "description": forms.Textarea(attrs={"rows": 4}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        apply_field_labels(self.fields, {
            "hospital_name": "Hospital Name",
            "hospital_type": "Hospital Type",
            "registration_number": "Registration/License Number",
            "address": "Address",
            "city": "City",
            "state": "State",
            "pincode": "Pincode",
            "contact_number": "Contact Number",
            "emergency_contact": "Emergency Contact Number",
            "email": "Email",
            "website": "Website URL",
            "blood_bank_available": "Blood Bank Available",
            "has_24hr_service": "24 Hour Service",
            "description": "Description",
            "logo": "Logo",
            "verification_document": "Verification Document",
            "latitude": "Latitude",
            "longitude": "Longitude",
        })
        for name, field in self.fields.items():
            if not isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update({"class": "form-control"})


class BloodStockForm(forms.ModelForm):
    class Meta:
        model = BloodStock
        fields = ["a_positive", "a_negative", "b_positive", "b_negative",
                  "o_positive", "o_negative", "ab_positive", "ab_negative"]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        apply_field_labels(self.fields, {
            "a_positive": "A+",
            "a_negative": "A-",
            "b_positive": "B+",
            "b_negative": "B-",
            "o_positive": "O+",
            "o_negative": "O-",
            "ab_positive": "AB+",
            "ab_negative": "AB-",
        })
        for field in self.fields.values():
            field.widget.attrs.update({"class": "form-control", "min": "0"})


class HospitalEmployeeForm(forms.ModelForm):
    class Meta:
        model = HospitalEmployee
        fields = ["name", "role", "contact_number", "email", "employee_id"]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        apply_field_labels(self.fields, {
            "name": "Name",
            "role": "Role",
            "contact_number": "Contact Number",
            "email": "Email",
            "employee_id": "Employee ID",
        })
        for field in self.fields.values():
            field.widget.attrs.update({"class": "form-control"})
