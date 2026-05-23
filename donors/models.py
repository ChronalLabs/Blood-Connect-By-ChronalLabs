"""
BloodConnect Donor Models
"""
from django.db import models
from django.conf import settings


class DonorProfile(models.Model):
    BLOOD_GROUP_CHOICES = [
        ('A', 'A'), ('B', 'B'), ('AB', 'AB'), ('O', 'O'),
    ]
    RH_FACTOR_CHOICES = [
        ('+', 'Positive (+)'),
        ('-', 'Negative (-)'),
    ]
    AVAILABILITY_CHOICES = [
        ('available', 'Available'),
        ('unavailable', 'Unavailable'),
        ('cooldown', 'In Cooldown Period'),
    ]
    
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='donor_profile')
    blood_group = models.CharField(max_length=3, choices=BLOOD_GROUP_CHOICES)
    rh_factor = models.CharField(max_length=1, choices=RH_FACTOR_CHOICES)
    age = models.PositiveIntegerField()
    weight = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    any_disease = models.TextField(blank=True)
    previous_injury = models.TextField(blank=True)
    current_health_condition = models.TextField(blank=True)
    medications = models.TextField(blank=True)
    last_blood_donation_date = models.DateField(null=True, blank=True)
    last_donation_hospital = models.CharField(max_length=200, blank=True)
    total_donations = models.PositiveIntegerField(default=0)
    availability_status = models.CharField(max_length=20, choices=AVAILABILITY_CHOICES, default='available')
    willing_to_travel = models.BooleanField(default=True)
    max_travel_distance = models.PositiveIntegerField(default=10)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Donor Profile'
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.blood_group}{self.rh_factor}"
    
    @property
    def blood_type(self):
        return f"{self.blood_group}{self.rh_factor}"
    
    def can_donate(self):
        if not self.last_blood_donation_date:
            return True
        from datetime import date, timedelta
        return date.today() - self.last_blood_donation_date > timedelta(days=90)


class BloodDonationHistory(models.Model):
    donor = models.ForeignKey(DonorProfile, on_delete=models.CASCADE, related_name='donation_history')
    donation_date = models.DateField()
    hospital_name = models.CharField(max_length=200)
    units_donated = models.DecimalField(max_digits=4, decimal_places=2, default=1.0)
    blood_request = models.ForeignKey(
        'blood_requests.BloodRequest', on_delete=models.SET_NULL, null=True, blank=True
    )
    notes = models.TextField(blank=True)
    verified_by_hospital = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-donation_date']
    
    def __str__(self):
        return f"{self.donor.user.get_full_name()} donated on {self.donation_date}"
