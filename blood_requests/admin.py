from django.contrib import admin
from .models import BloodRequest, DonorResponse


@admin.register(BloodRequest)
class BloodRequestAdmin(admin.ModelAdmin):
    list_display = ["patient_name", "blood_group", "rh_factor", "hospital_name",
                    "urgency_level", "status", "created_at"]
    list_filter = ["status", "urgency_level", "blood_group", "rh_factor"]
    search_fields = ["patient_name", "hospital_name", "requester__username"]
    readonly_fields = ["created_at", "updated_at"]


@admin.register(DonorResponse)
class DonorResponseAdmin(admin.ModelAdmin):
    list_display = ["donor", "blood_request", "status", "created_at"]
    list_filter = ["status"]
