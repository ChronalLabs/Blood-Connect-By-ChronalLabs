from django import forms
from .models import HospitalProfile, BloodStock, HospitalEmployee


class HospitalProfileForm(forms.ModelForm):
    class Meta:
        model = HospitalProfile
        fields = ["hospital_name", "registration_number", "address", "city", "state",
                  "pincode", "contact_number", "emergency_contact", "email", "website",
                  "blood_bank_available", "has_24hr_service", "description", "logo",
                  "latitude", "longitude"]
        widgets = {
            "address": forms.Textarea(attrs={"rows": 3}),
            "description": forms.Textarea(attrs={"rows": 4}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
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
        for field in self.fields.values():
            field.widget.attrs.update({"class": "form-control", "min": "0"})


class HospitalEmployeeForm(forms.ModelForm):
    class Meta:
        model = HospitalEmployee
        fields = ["name", "role", "contact_number", "email", "employee_id"]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({"class": "form-control"})
