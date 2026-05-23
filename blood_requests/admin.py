from django.contrib import admin
from .models import BloodRequest, DonorNotification, DonorResponse


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


@admin.register(DonorNotification)
class DonorNotificationAdmin(admin.ModelAdmin):
    list_display = ["donor", "blood_request", "channel", "status", "sent_at", "created_at"]
    list_filter = ["channel", "status"]
    search_fields = ["donor__username", "donor__email", "blood_request__patient_name", "blood_request__hospital_name"]
    readonly_fields = ["created_at", "sent_at"]
