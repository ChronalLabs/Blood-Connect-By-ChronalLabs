from django import forms
from .models import SeekerProfile
from blood_requests.models import BloodRequest

from bloodconnect.i18n import apply_field_labels, translate_choices, translate_text as t

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
        apply_field_labels(self.fields, {
            "patient_name": "Patient Name",
            "patient_age": "Patient Age",
            "blood_group": "Blood Group",
            "rh_factor": "RH",
            "units_required": "Units Required",
            "hospital_name": "Hospital Name",
            "hospital_address": "Hospital Address",
            "hospital_contact": "Hospital Contact",
            "urgency_level": "Urgency Level",
            "city": "City",
            "additional_notes": "Additional Notes",
            "required_by": "Required By",
        })
        for field in self.fields.values():
            field.widget.attrs.update({"class": "form-control"})

class DonorSearchForm(forms.Form):
    blood_group = forms.ChoiceField(choices=BLOOD_GROUP_CHOICES, required=False)
    rh_factor = forms.ChoiceField(choices=RH_CHOICES, required=False)
    city = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={"placeholder": "Enter city"}))
    radius_km = forms.IntegerField(
        required=False, min_value=1, max_value=500,
        initial=50,
        widget=forms.NumberInput(attrs={"placeholder": "Radius (km)"})
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["blood_group"].choices = translate_choices(BLOOD_GROUP_CHOICES)
        self.fields["rh_factor"].choices = translate_choices(RH_CHOICES)
        apply_field_labels(self.fields, {
            "blood_group": "Blood Group",
            "rh_factor": "RH",
            "city": "Search by city",
            "radius_km": "Radius (km)",
        })
        self.fields["city"].widget.attrs["placeholder"] = t("Enter city")
        self.fields["radius_km"].widget.attrs["placeholder"] = t("Radius (km)")
        for field in self.fields.values():
            field.widget.attrs.update({"class": "form-control"})
