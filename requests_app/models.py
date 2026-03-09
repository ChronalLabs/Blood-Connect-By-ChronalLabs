"""BloodConnect - Blood Request Models"""
from django.db import models
from django.conf import settings


class BloodRequest(models.Model):
    """A blood request from seeker or hospital"""

    BLOOD_GROUP_CHOICES = [
        ('A', 'A'), ('B', 'B'), ('O', 'O'), ('AB', 'AB'),
    ]
    RH_CHOICES = [('+', 'Positive (+)'), ('-', 'Negative (-)')]

    URGENCY_CHOICES = [
        (1, 'Normal (within a week)'),
        (2, 'Urgent (within 48 hours)'),
        (3, 'Critical (within 24 hours)'),
        (4, 'Emergency (within hours)'),
    ]
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('fulfilled', 'Fulfilled'),
        ('cancelled', 'Cancelled'),
    ]

    # Requester
    seeker = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='blood_requests'
    )
    seeker_contact = models.CharField(max_length=15)

    # Blood requirement
    blood_group = models.CharField(max_length=3, choices=BLOOD_GROUP_CHOICES)
    rh_factor = models.CharField(max_length=1, choices=RH_CHOICES)
    units_required = models.PositiveIntegerField(default=1)
    urgency_level = models.IntegerField(choices=URGENCY_CHOICES, default=1)

    # Hospital
    hospital_name = models.CharField(max_length=200)
    hospital_address = models.TextField(blank=True)
    patient_name = models.CharField(max_length=100, blank=True)
    reason = models.TextField(blank=True)

    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    accepted_by = models.ForeignKey(
        'donors.DonorProfile',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='accepted_requests'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    required_by = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Blood Request'
        ordering = ['-urgency_level', '-created_at']

    def __str__(self):
        return f"{self.blood_group}{self.rh_factor} - {self.urgency_level} - {self.hospital_name}"

    def get_full_blood_group(self):
        return f"{self.blood_group}{self.rh_factor}"

    def get_urgency_display_class(self):
        classes = {1: 'normal', 2: 'urgent', 3: 'critical', 4: 'emergency'}
        return classes.get(self.urgency_level, 'normal')
