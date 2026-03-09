from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, EmergencyContact


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ["username", "email", "first_name", "last_name", "role", "is_verified", "date_joined"]
    list_filter = ["role", "is_verified", "is_active"]
    search_fields = ["username", "email", "first_name", "last_name", "phone_number"]
    fieldsets = UserAdmin.fieldsets + (
        ("BloodConnect Info", {
            "fields": ("role", "phone_number", "secondary_phone", "address",
                       "city", "state", "pincode", "aadhar_card_number",
                       "latitude", "longitude", "is_verified", "profile_picture")
        }),
    )


@admin.register(EmergencyContact)
class EmergencyContactAdmin(admin.ModelAdmin):
    list_display = ["user", "name", "phone_number", "relationship"]
    search_fields = ["user__username", "name", "phone_number"]
