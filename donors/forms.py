from django import forms
from .models import DonorProfile, BloodDonationHistory


class DonorProfileForm(forms.ModelForm):
    class Meta:
        model = DonorProfile
        fields = ["blood_group", "rh_factor", "age", "weight", "any_disease",
                  "previous_injury", "current_health_condition", "medications",
                  "last_blood_donation_date", "last_donation_hospital",
                  "availability_status", "willing_to_travel", "max_travel_distance"]
        widgets = {
            "last_blood_donation_date": forms.DateInput(attrs={"type": "date"}),
            "any_disease": forms.Textarea(attrs={"rows": 2}),
            "previous_injury": forms.Textarea(attrs={"rows": 2}),
            "current_health_condition": forms.Textarea(attrs={"rows": 2}),
            "medications": forms.Textarea(attrs={"rows": 2}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if not isinstance(field.widget, (forms.CheckboxInput, forms.RadioSelect)):
                field.widget.attrs.update({"class": "form-control"})


class DonationHistoryForm(forms.ModelForm):
    class Meta:
        model = BloodDonationHistory
        fields = ["donation_date", "hospital_name", "units_donated", "notes"]
        widgets = {
            "donation_date": forms.DateInput(attrs={"type": "date"}),
            "notes": forms.Textarea(attrs={"rows": 2}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({"class": "form-control"})
