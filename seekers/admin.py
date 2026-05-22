from django.contrib import admin

from .models import SeekerProfile


@admin.register(SeekerProfile)
class SeekerProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "patient_name",
        "blood_group",
        "rh_factor",
        "hospital_name",
    )

    search_fields = (
        "user__username",
        "user__first_name",
        "user__last_name",
        "patient_name",
        "hospital_name",
    )

    list_filter = (
        "blood_group",
        "rh_factor",
    )

    ordering = ("user__username",)

    list_per_page = 20