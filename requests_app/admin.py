from django.contrib import admin
from .models import BloodRequest


@admin.register(BloodRequest)
class BloodRequestAdmin(admin.ModelAdmin):
    list_display = ('seeker', 'blood_group', 'rh_factor', 'units_required',
                    'urgency_level', 'hospital_name', 'status', 'created_at')
    list_filter = ('status', 'urgency_level', 'blood_group', 'rh_factor')
    search_fields = ('seeker__name', 'hospital_name', 'patient_name')
    ordering = ('-urgency_level', '-created_at')
    readonly_fields = ('created_at', 'updated_at')
