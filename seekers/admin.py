from django.contrib import admin
from .models import SeekerProfile

@admin.register(SeekerProfile)
class SeekerProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "blood_group", "rh_factor", "hospital_name"]
    search_fields = ["user__username", "patient_name"]
