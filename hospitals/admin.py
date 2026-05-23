from django.contrib import admin
from .models import HospitalProfile, BloodStock, HospitalEmployee


@admin.register(HospitalProfile)
class HospitalProfileAdmin(admin.ModelAdmin):
    list_display = ["hospital_name", "city", "state", "blood_bank_available", "verified"]
    list_filter = ["verified", "blood_bank_available", "state"]
    search_fields = ["hospital_name", "city", "registration_number"]
    actions = ["verify_hospitals"]
    
    def verify_hospitals(self, request, queryset):
        from django.utils import timezone
        queryset.update(verified=True, verified_at=timezone.now())
        self.message_user(request, f"{queryset.count()} hospitals verified.")
    verify_hospitals.short_description = "Verify selected hospitals"


@admin.register(BloodStock)
class BloodStockAdmin(admin.ModelAdmin):
    list_display = ["hospital", "a_positive", "a_negative", "b_positive", "b_negative",
                    "o_positive", "o_negative", "ab_positive", "ab_negative", "last_updated"]


@admin.register(HospitalEmployee)
class HospitalEmployeeAdmin(admin.ModelAdmin):
    list_display = ["name", "hospital", "role", "verified"]
    list_filter = ["role", "verified"]
