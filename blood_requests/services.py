import math
from donors.models import DonorProfile
from django.db.models import Q

def calculate_haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance in kilometers between two points 
    on the earth (specified in decimal degrees)
    """
    if None in (lat1, lon1, lat2, lon2):
        return float('inf')

    # Convert decimal degrees to radians 
    lat1, lon1, lat2, lon2 = map(math.radians, [float(lat1), float(lon1), float(lat2), float(lon2)])

    # Haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a)) 
    r = 6371 # Radius of earth in kilometers
    return c * r

COMPATIBILITY_MATRIX = {
    'A+': ['A+', 'A-', 'O+', 'O-'],
    'O+': ['O+', 'O-'],
    'B+': ['B+', 'B-', 'O+', 'O-'],
    'AB+': ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'],
    'A-': ['A-', 'O-'],
    'O-': ['O-'],
    'B-': ['B-', 'O-'],
    'AB-': ['AB-', 'A-', 'B-', 'O-']
}

def get_compatible_blood_types(requested_blood_type):
    """Returns a list of blood types that can donate to the requested type."""
    return COMPATIBILITY_MATRIX.get(requested_blood_type, [])

def find_closest_donors(blood_request, limit=5):
    """
    Finds the closest eligible donors for a given blood request.
    """
    req_lat = blood_request.latitude
    req_lon = blood_request.longitude
    
    if req_lat is None or req_lon is None:
        return []

    requested_type = f"{blood_request.blood_group}{blood_request.rh_factor}"
    compatible_types = get_compatible_blood_types(requested_type)
    
    # Extract blood groups and rh factors from compatible types
    q_objects = Q()
    for b_type in compatible_types:
        bg = b_type[:-1]
        rh = b_type[-1]
        q_objects |= Q(blood_group=bg, rh_factor=rh)

    if not q_objects:
        return []

    # Initial query to filter by basic availability and blood type
    potential_donors = DonorProfile.objects.filter(
        availability_status='available',
        user__latitude__isnull=False,
        user__longitude__isnull=False
    ).filter(q_objects)

    matched_donors = []
    
    for donor in potential_donors:
        if not donor.can_donate():
            continue
            
        dist = calculate_haversine_distance(
            req_lat, req_lon, 
            donor.user.latitude, donor.user.longitude
        )
        
        if donor.willing_to_travel and dist <= donor.max_travel_distance:
            matched_donors.append({
                'donor': donor,
                'distance': dist
            })

    # Sort by distance
    matched_donors.sort(key=lambda x: x['distance'])
    
    return matched_donors[:limit]
