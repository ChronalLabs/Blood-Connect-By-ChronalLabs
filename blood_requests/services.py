from django.conf import settings
from django.core.mail import send_mail
from django.db import IntegrityError, transaction
from django.utils import timezone

from .models import DonorNotification


def notify_compatible_donors(blood_request, radius_km=50):
    """
    Notify compatible donors for a new blood request.

    Returns a list of DonorNotification objects created during this call.
    Existing notifications are left untouched to avoid duplicate emails.
    """
    if blood_request.status != 'open' or blood_request.units_remaining <= 0:
        return []

    ranked_donors = blood_request.get_ranked_donors(radius_km=radius_km)
    ranked_donors.sort(
        key=lambda item: (
            not _is_same_city(item['donor'].user.city, blood_request.city),
            -item['final_score'],
        )
    )

    notifications = []
    for item in ranked_donors:
        donor_profile = item['donor']
        notification = _create_notification_once(blood_request, donor_profile.user)
        if notification is None:
            continue

        _send_email_notification(notification, blood_request, donor_profile)
        notifications.append(notification)

    return notifications


def _create_notification_once(blood_request, donor):
    try:
        with transaction.atomic():
            notification, created = DonorNotification.objects.get_or_create(
                blood_request=blood_request,
                donor=donor,
                channel='email',
                defaults={'status': 'skipped'},
            )
    except IntegrityError:
        return None

    if not created:
        return None
    return notification


def _send_email_notification(notification, blood_request, donor_profile):
    donor = donor_profile.user
    if not donor.email:
        notification.status = 'skipped'
        notification.error_message = 'Donor does not have an email address.'
        notification.save(update_fields=['status', 'error_message'])
        return

    subject = f"Urgent blood request: {blood_request.blood_type} needed"
    message = _build_email_message(blood_request, donor_profile)

    try:
        sent_count = send_mail(
            subject,
            message,
            getattr(settings, 'DEFAULT_FROM_EMAIL', None),
            [donor.email],
            fail_silently=False,
        )
    except Exception as exc:
        notification.status = 'failed'
        notification.error_message = str(exc)
        notification.save(update_fields=['status', 'error_message'])
        return

    if sent_count:
        notification.status = 'sent'
        notification.sent_at = timezone.now()
        notification.error_message = ''
        notification.save(update_fields=['status', 'sent_at', 'error_message'])
    else:
        notification.status = 'failed'
        notification.error_message = 'Email backend did not send the message.'
        notification.save(update_fields=['status', 'error_message'])


def _build_email_message(blood_request, donor_profile):
    lines = [
        f"Hello {donor_profile.user.get_full_name() or donor_profile.user.username},",
        "",
        "A compatible blood request has been created near you.",
        "",
        f"Blood type needed: {blood_request.blood_type}",
        f"Urgency: {blood_request.get_urgency_level_display()}",
        f"Units required: {blood_request.units_remaining}",
        f"Hospital: {blood_request.hospital_name}",
        f"City: {blood_request.city or 'Not specified'}",
    ]

    if blood_request.hospital_contact:
        lines.append(f"Hospital contact: {blood_request.hospital_contact}")

    lines.extend([
        "",
        "Please log in to BloodConnect and respond if you are available to donate.",
    ])
    return "\n".join(lines)


def _is_same_city(donor_city, request_city):
    if not donor_city or not request_city:
        return False
    return donor_city.strip().lower() == request_city.strip().lower()
