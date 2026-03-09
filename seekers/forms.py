from django import forms
from .models import SeekerProfile
from blood_requests.models import BloodRequest

BLOOD_GROUP_CHOICES = [("", "All Blood Groups"), ("A", "A"), ("B", "B"), ("AB", "AB"), ("O", "O")]
RH_CHOICES = [("", "All"), ("+", "Positive (+)"), ("-", "Negative (-)")]

class BloodRequestForm(forms.ModelForm):
    class Meta:
        model = BloodRequest
        fields = ["patient_name", "patient_age", "blood_group", "rh_factor",
                  "units_required", "hospital_name", "hospital_address",
                  "hospital_contact", "urgency_level", "city", "additional_notes", "required_by"]
        widgets = {
            "hospital_address": forms.Textarea(attrs={"rows": 2}),
            "additional_notes": forms.Textarea(attrs={"rows": 3}),
            "required_by": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({"class": "form-control"})

class DonorSearchForm(forms.Form):
    blood_group = forms.ChoiceField(choices=BLOOD_GROUP_CHOICES, required=False)
    rh_factor = forms.ChoiceField(choices=RH_CHOICES, required=False)
    city = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={"placeholder": "Enter city"}))
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({"class": "form-control"})
