"""
BloodConnect Hospital Models
Hospital profiles, blood stock management, and employee verification
"""
from django.db import models
from django.conf import settings


class HospitalProfile(models.Model):
    """Hospital profile with blood bank information"""
    
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='hospital_profile'
    )
    
    hospital_name = models.CharField(max_length=200)
    registration_number = models.CharField(max_length=50, blank=True, unique=True, null=True)
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.CharField(max_length=6)
    contact_number = models.CharField(max_length=15)
    emergency_contact = models.CharField(max_length=15, blank=True)
    email = models.EmailField(blank=True)
    website = models.URLField(blank=True)
    
    # Location
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    
    # Features
    blood_bank_available = models.BooleanField(default=True)
    has_24hr_service = models.BooleanField(default=False)
    verified = models.BooleanField(default=False)
    verified_at = models.DateTimeField(null=True, blank=True)
    
    description = models.TextField(blank=True)
    logo = models.ImageField(upload_to='hospital_logos/', blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Hospital Profile'
        verbose_name_plural = 'Hospital Profiles'
    
    def __str__(self):
        return self.hospital_name


class HospitalEmployee(models.Model):
    """Verified employees of a hospital"""
    
    ROLE_CHOICES = [
        ('doctor', 'Doctor'),
        ('nurse', 'Nurse'),
        ('technician', 'Lab Technician'),
        ('admin', 'Administrator'),
        ('blood_bank_officer', 'Blood Bank Officer'),
    ]
    
    hospital = models.ForeignKey(HospitalProfile, on_delete=models.CASCADE, related_name='employees')
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=30, choices=ROLE_CHOICES)
    contact_number = models.CharField(max_length=15)
    email = models.EmailField(blank=True)
    employee_id = models.CharField(max_length=50, blank=True)
    verified = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.name} - {self.hospital.hospital_name}"


class BloodStock(models.Model):
    """Blood stock levels for a hospital"""
    
    hospital = models.OneToOneField(HospitalProfile, on_delete=models.CASCADE, related_name='blood_stock')
    
    # Blood units available (in bags/units)
    a_positive = models.PositiveIntegerField(default=0, verbose_name='A+')
    a_negative = models.PositiveIntegerField(default=0, verbose_name='A-')
    b_positive = models.PositiveIntegerField(default=0, verbose_name='B+')
    b_negative = models.PositiveIntegerField(default=0, verbose_name='B-')
    o_positive = models.PositiveIntegerField(default=0, verbose_name='O+')
    o_negative = models.PositiveIntegerField(default=0, verbose_name='O-')
    ab_positive = models.PositiveIntegerField(default=0, verbose_name='AB+')
    ab_negative = models.PositiveIntegerField(default=0, verbose_name='AB-')
    
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Blood Stock'
        verbose_name_plural = 'Blood Stocks'
    
    def __str__(self):
        return f"Blood Stock - {self.hospital.hospital_name}"
    
    def get_stock(self, blood_group, rh_factor):
        """Get stock for specific blood type"""
        field_map = {
            ('A', '+'): 'a_positive', ('A', '-'): 'a_negative',
            ('B', '+'): 'b_positive', ('B', '-'): 'b_negative',
            ('O', '+'): 'o_positive', ('O', '-'): 'o_negative',
            ('AB', '+'): 'ab_positive', ('AB', '-'): 'ab_negative',
        }
        field = field_map.get((blood_group, rh_factor))
        return getattr(self, field, 0) if field else 0
    
    def as_dict(self):
        return {
            'A+': self.a_positive, 'A-': self.a_negative,
            'B+': self.b_positive, 'B-': self.b_negative,
            'O+': self.o_positive, 'O-': self.o_negative,
            'AB+': self.ab_positive, 'AB-': self.ab_negative,
        }
