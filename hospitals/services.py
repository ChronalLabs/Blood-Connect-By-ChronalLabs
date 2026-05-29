"""
BloodConnect Hospital Services

Business logic for fulfilling blood requests directly from hospital stock.
Kept separate from views so it can be tested in isolation and reused.
"""
from django.db import transaction
from django.utils import timezone


# Map blood type string (e.g. "A+") → BloodStock field name.
_BLOOD_TYPE_TO_FIELD = {
    'A+': 'a_positive',
    'A-': 'a_negative',
    'B+': 'b_positive',
    'B-': 'b_negative',
    'O+': 'o_positive',
    'O-': 'o_negative',
    'AB+': 'ab_positive',
    'AB-': 'ab_negative',
}


def get_stock_field_name(blood_group: str, rh_factor: str) -> str | None:
    """Return the BloodStock field name for the given blood type, or None."""
    return _BLOOD_TYPE_TO_FIELD.get(f"{blood_group}{rh_factor}")


def fulfill_request_from_stock(hospital, blood_request):
    """
    Fulfill a BloodRequest by deducting units from the hospital's BloodStock.

    Args:
        hospital (HospitalProfile): The hospital performing the fulfillment.
        blood_request (BloodRequest): The request to fulfill.

    Returns:
        tuple[bool, str]: (success, human-readable message).

    Design decisions:
    - All mutations are wrapped in a single atomic transaction so a partial
      deduction can never leave the database in an inconsistent state.
    - We do NOT raise exceptions — callers receive (False, reason) instead,
      keeping view code clean.
    - We only allow exact blood-type matching (medically safest default).
    """
    # Guard: request must still be open with units remaining.
    if blood_request.status != 'open':
        return False, "This blood request is not open."

    units_needed = blood_request.units_remaining
    if units_needed <= 0:
        return False, "This blood request has already been fully fulfilled."

    # Guard: hospital must have a blood stock record.
    blood_stock = getattr(hospital, 'blood_stock', None)
    if blood_stock is None:
        return False, "No blood stock record found for this hospital."

    # Resolve the exact field name for the requested blood type.
    field_name = get_stock_field_name(blood_request.blood_group, blood_request.rh_factor)
    if field_name is None:
        return False, f"Unknown blood type: {blood_request.blood_type}."

    available_units = getattr(blood_stock, field_name, 0)

    # Guard: hospital must have enough stock.
    if available_units < units_needed:
        return False, (
            f"Insufficient stock. Requested {units_needed} unit(s) of "
            f"{blood_request.blood_type}, but only {available_units} available."
        )

    # Perform the atomic mutation.
    with transaction.atomic():
        # Re-fetch with a select_for_update lock to prevent race conditions
        # in concurrent fulfillment attempts.
        blood_stock_locked = hospital.blood_stock.__class__.objects.select_for_update().get(
            pk=blood_stock.pk
        )
        current_available = getattr(blood_stock_locked, field_name)
        if current_available < units_needed:
            return False, (
                f"Stock was updated concurrently. Only {current_available} unit(s) "
                f"of {blood_request.blood_type} now available. Please try again."
            )

        # Deduct stock.
        setattr(blood_stock_locked, field_name, current_available - units_needed)
        blood_stock_locked.save(update_fields=[field_name])

        # Fulfill the request.
        blood_request_locked = blood_request.__class__.objects.select_for_update().get(
            pk=blood_request.pk
        )
        blood_request_locked.units_fulfilled += units_needed
        blood_request_locked.fulfilled_at = timezone.now()
        blood_request_locked.status = 'fulfilled'
        blood_request_locked.save(update_fields=['units_fulfilled', 'fulfilled_at', 'status'])

    return True, (
        f"Successfully fulfilled {units_needed} unit(s) of {blood_request.blood_type} "
        f"from {hospital.hospital_name}'s inventory."
    )
