import logging
from celery import shared_task
from .models import BloodRequest
from .services import find_closest_donors

logger = logging.getLogger(__name__)

@shared_task
def dispatch_emergency_request(request_id):
    """
    Celery task to find matched donors and simulate sending notifications.
    """
    try:
        blood_request = BloodRequest.objects.get(id=request_id)
    except BloodRequest.DoesNotExist:
        logger.error(f"BloodRequest with id {request_id} not found.")
        return

    logger.info(f"Starting dispatch for BloodRequest {request_id} ({blood_request.blood_type})")
    
    matched_donors = find_closest_donors(blood_request, limit=5)
    
    if not matched_donors:
        logger.info(f"No compatible donors found within range for BloodRequest {request_id}.")
        return
        
    logger.info(f"Found {len(matched_donors)} eligible donors for BloodRequest {request_id}.")
    
    for match in matched_donors:
        donor_profile = match['donor']
        distance = match['distance']
        user = donor_profile.user
        
        # Simulate sending SMS/Email
        phone = user.phone_number or "No Phone"
        email = user.email or "No Email"
        name = user.get_full_name() or user.username
        
        message = (
            f"\n"
            f"--- SIMULATED DISPATCH NOTIFICATION ---\n"
            f"To: {name} (Donor)\n"
            f"Contact: {phone} | {email}\n"
            f"Distance: {distance:.2f} km\n"
            f"Message: URGENT! A patient needs {blood_request.blood_type} blood at {blood_request.hospital_name}.\n"
            f"Please respond to this request immediately if you can donate.\n"
            f"---------------------------------------\n"
        )
        # Log to console
        print(message)
        logger.info(f"Dispatched simulated notification to user_id={user.id}")

    return f"Dispatched to {len(matched_donors)} donors"
