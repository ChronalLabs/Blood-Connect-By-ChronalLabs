"""BloodConnect - Blood Request Form"""
from django import forms
from .models import BloodRequest


class BloodRequestForm(forms.ModelForm):
    class Meta:
        model = BloodRequest
        fields = [
            'blood_group', 'rh_factor', 'units_required', 'urgency_level',
            'hospital_name', 'hospital_address', 'patient_name', 'reason', 'required_by'
        ]
        widgets = {
            'blood_group': forms.Select(attrs={'class': 'form-control'}),
            'rh_factor': forms.Select(attrs={'class': 'form-control'}),
            'units_required': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'urgency_level': forms.Select(attrs={'class': 'form-control'}),
            'hospital_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Hospital name'}),
            'hospital_address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'patient_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Patient name (optional)'}),
            'reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Brief reason for blood requirement'}),
            'required_by': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
        }
