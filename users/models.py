"""
BloodConnect User Models
Custom user model with role-based access for Donors, Seekers, and Hospitals
"""
from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    """Extended user model with role and contact information"""
    
    ROLE_CHOICES = [
        ('donor', 'Blood Donor'),
        ('seeker', 'Blood Seeker'),
        ('hospital', 'Hospital'),
        ('admin', 'Administrator'),
    ]
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='seeker')
    phone_number = models.CharField(max_length=15, blank=True)
    secondary_phone = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    aadhar_card_number = models.CharField(max_length=12, blank=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    
    # Location
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    pincode = models.CharField(max_length=6, blank=True)
    
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"
    
    @property
    def is_donor(self):
        return self.role == 'donor'
    
    @property
    def is_seeker(self):
        return self.role == 'seeker'
    
    @property
    def is_hospital(self):
        return self.role == 'hospital'


class EmergencyContact(models.Model):
    """Emergency contact linked to a user"""
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='emergency_contact')
    name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15)
    secondary_phone = models.CharField(max_length=15, blank=True)
    relationship = models.CharField(max_length=50, blank=True)
    address = models.TextField(blank=True)
    email = models.EmailField(blank=True)
    
    def __str__(self):
        return f"Emergency contact for {self.user.username}: {self.name}"
