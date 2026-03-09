from django.db import models
from django.conf import settings

class SeekerProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="seeker_profile")
    blood_group = models.CharField(max_length=3, blank=True)
    rh_factor = models.CharField(max_length=1, blank=True)
    hospital_name = models.CharField(max_length=200, blank=True)
    patient_name = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Seeker: {self.user.get_full_name() or self.user.username}"
