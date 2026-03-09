from django.contrib import admin
from .models import DonorProfile, BloodDonationHistory


@admin.register(DonorProfile)
class DonorProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "blood_group", "rh_factor", "age", "availability_status", "total_donations"]
    list_filter = ["blood_group", "rh_factor", "availability_status"]
    search_fields = ["user__username", "user__first_name", "user__last_name"]


@admin.register(BloodDonationHistory)
class BloodDonationHistoryAdmin(admin.ModelAdmin):
    list_display = ["donor", "donation_date", "hospital_name", "units_donated", "verified_by_hospital"]
    list_filter = ["verified_by_hospital", "donation_date"]
    search_fields = ["donor__user__username", "hospital_name"]
