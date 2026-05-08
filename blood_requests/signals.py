from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import BloodRequest
from .tasks import dispatch_emergency_request

@receiver(post_save, sender=BloodRequest)
def trigger_dispatch_on_critical_request(sender, instance, created, **kwargs):
    """
    Triggers the emergency dispatch task when a new critical BloodRequest is created.
    """
    if created and instance.urgency_level == 'critical' and instance.status == 'open':
        # Trigger Celery task
        dispatch_emergency_request.delay(instance.id)
