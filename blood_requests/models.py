"""
BloodConnect Blood Request Models
"""
from django.db import models
from django.conf import settings


class BloodRequest(models.Model):
    BLOOD_GROUP_CHOICES = [
        ('A', 'A'), ('B', 'B'), ('AB', 'AB'), ('O', 'O'),
    ]
    RH_FACTOR_CHOICES = [('+', 'Positive (+)'), ('-', 'Negative (-)')]
    URGENCY_CHOICES = [
        ('critical', 'Critical - Within Hours'),
        ('urgent', 'Urgent - Within 24 Hours'),
        ('moderate', 'Moderate - Within 3 Days'),
        ('normal', 'Normal - Within a Week'),
    ]
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('fulfilled', 'Fulfilled'),
        ('cancelled', 'Cancelled'),
        ('expired', 'Expired'),
    ]
    
    requester = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='blood_requests_made')
    patient_name = models.CharField(max_length=100)
    patient_age = models.PositiveIntegerField(null=True, blank=True)
    blood_group = models.CharField(max_length=3, choices=BLOOD_GROUP_CHOICES)
    rh_factor = models.CharField(max_length=1, choices=RH_FACTOR_CHOICES)
    units_required = models.PositiveIntegerField(default=1)
    units_fulfilled = models.PositiveIntegerField(default=0)
    hospital_name = models.CharField(max_length=200)
    hospital_address = models.TextField()
    hospital_contact = models.CharField(max_length=15, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    city = models.CharField(max_length=100, blank=True)
    urgency_level = models.CharField(max_length=20, choices=URGENCY_CHOICES, default='urgent')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    additional_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    required_by = models.DateTimeField(null=True, blank=True)
    fulfilled_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.blood_group}{self.rh_factor} needed - {self.hospital_name} ({self.status})"
    
    @property
    def blood_type(self):
        return f"{self.blood_group}{self.rh_factor}"
    
    @property
    def units_remaining(self):
        return self.units_required - self.units_fulfilled


class DonorResponse(models.Model):
    STATUS_CHOICES = [
        ('interested', 'Interested'),
        ('confirmed', 'Confirmed'),
        ('donated', 'Donated'),
        ('cancelled', 'Cancelled'),
    ]
    blood_request = models.ForeignKey(BloodRequest, on_delete=models.CASCADE, related_name='donor_responses')
    donor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='donation_responses')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='interested')
    message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('blood_request', 'donor')
    
    def __str__(self):
        return f"{self.donor.username} -> {self.blood_request}"
