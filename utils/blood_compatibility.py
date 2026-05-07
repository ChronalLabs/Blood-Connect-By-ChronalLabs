"""
Blood compatibility matrix, priority scoring, and donor ranking engine.

Compatibility rules:
- RH- patients can ONLY receive RH- blood (sensitization risk)
- RH+ patients can receive both RH- and RH+
- O- is the universal donor (donates to all 8 types)
- AB+ is the universal recipient (receives from all 8 types)
"""
import math

# Full donation compatibility matrix: donor -> list of compatible recipient types
DONATION_MATRIX = {
    ('O', '-'):  [('O','-'), ('O','+'), ('A','-'), ('A','+'), ('B','-'), ('B','+'), ('AB','-'), ('AB','+')],
    ('O', '+'):  [('O','+'), ('A','+'), ('B','+'), ('AB','+')],
    ('A', '-'):  [('A','-'), ('A','+'), ('AB','-'), ('AB','+')],
    ('A', '+'):  [('A','+'), ('AB','+')],
    ('B', '-'):  [('B','-'), ('B','+'), ('AB','-'), ('AB','+')],
    ('B', '+'):  [('B','+'), ('AB','+')],
    ('AB', '-'): [('AB','-'), ('AB','+')],
    ('AB', '+'): [('AB','+')],
}

UNIVERSAL_DONOR = ('O', '-')
UNIVERSAL_RECIPIENT = ('AB', '+')


def get_compatible_donor_types(patient_blood_group, patient_rh):
    """Return list of (blood_group, rh_factor) tuples that can donate to this patient."""
    patient = (patient_blood_group, patient_rh)
    return [donor for donor, recipients in DONATION_MATRIX.items() if patient in recipients]


def get_donation_priority(donor_blood_group, donor_rh, patient_blood_group, patient_rh):
    """
    Return compatibility score (0-100).
    0 = incompatible (excluded), 60/80/90/100 = compatible tiers.
    """
    donor = (donor_blood_group, donor_rh)
    patient = (patient_blood_group, patient_rh)

    if patient not in DONATION_MATRIX.get(donor, []):
        return 0  # incompatible

    if donor == patient:
        return 100  # exact match

    if donor == UNIVERSAL_DONOR:
        return 90  # O- universal donor bonus

    if donor_rh == patient_rh:
        return 80  # same RH, different ABO

    return 60  # compatible but cross-RH or non-ideal


def haversine_distance(lat1, lon1, lat2, lon2):
    """Return distance in km between two lat/lon points."""
    R = 6371
    phi1, phi2 = math.radians(float(lat1)), math.radians(float(lat2))
    dphi = math.radians(float(lat2) - float(lat1))
    dlambda = math.radians(float(lon2) - float(lon1))
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def rank_donors(donors, patient_blood_group, patient_rh, patient_lat=None, patient_lon=None, radius_km=50):
    """
    Rank a queryset/list of DonorProfile objects by final_score descending.

    final_score = (compatibility_score * 0.70) + (proximity_score * 0.30)

    Returns list of dicts with donor + score metadata.
    Donors outside radius_km (when coordinates available) are excluded.
    """
    ranked = []
    for donor in donors:
        compat = get_donation_priority(
            donor.blood_group, donor.rh_factor,
            patient_blood_group, patient_rh
        )
        if compat == 0:
            continue

        distance_km = None
        proximity_score = 50  # neutral when no coordinates

        if (patient_lat is not None and patient_lon is not None and
                donor.user.latitude is not None and donor.user.longitude is not None):
            distance_km = haversine_distance(
                patient_lat, patient_lon,
                donor.user.latitude, donor.user.longitude
            )
            if distance_km > radius_km:
                continue
            proximity_score = max(0, 100 - (distance_km / radius_km * 100))

        final_score = round((compat * 0.70) + (proximity_score * 0.30), 1)
        ranked.append({
            'donor': donor,
            'compatibility_score': compat,
            'proximity_score': round(proximity_score, 1),
            'distance_km': round(distance_km, 1) if distance_km is not None else None,
            'final_score': final_score,
        })

    ranked.sort(key=lambda x: x['final_score'], reverse=True)
    return ranked
