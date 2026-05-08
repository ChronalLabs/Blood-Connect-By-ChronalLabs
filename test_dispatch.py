import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bloodconnect.settings')
django.setup()

from users.models import CustomUser
from donors.models import DonorProfile
from blood_requests.models import BloodRequest

# Clear existing test data
BloodRequest.objects.all().delete()
DonorProfile.objects.all().delete()
CustomUser.objects.filter(username__startswith='test_').delete()

# Create a seeker (requester)
seeker = CustomUser.objects.create_user(
    username='test_seeker', 
    role='seeker',
    latitude=19.0760,  # Mumbai
    longitude=72.8777
)

# Create some compatible donors near Mumbai
donor_user_1 = CustomUser.objects.create_user(
    username='test_donor_1', 
    role='donor', 
    first_name='Rahul', 
    phone_number='+919876543210',
    latitude=19.0800,  # Very close to Mumbai center
    longitude=72.8800
)
DonorProfile.objects.create(
    user=donor_user_1, 
    blood_group='O', 
    rh_factor='-', 
    age=25, 
    availability_status='available',
    willing_to_travel=True,
    max_travel_distance=50
)

# Create an incompatible donor
donor_user_2 = CustomUser.objects.create_user(
    username='test_donor_2', 
    role='donor', 
    first_name='Sneha',
    latitude=19.0760,
    longitude=72.8777
)
DonorProfile.objects.create(
    user=donor_user_2, 
    blood_group='B', 
    rh_factor='+', 
    age=28, 
    availability_status='available',
    willing_to_travel=True,
    max_travel_distance=50
)

# Create a critical Blood Request for O- (Only O- can donate)
# This should trigger the post_save signal and the celery task!
print("Creating critical blood request...")
br = BloodRequest.objects.create(
    requester=seeker,
    patient_name='Emergency Patient',
    blood_group='O',
    rh_factor='-',
    units_required=2,
    hospital_name='City Hospital',
    latitude=19.0760,
    longitude=72.8777,
    urgency_level='critical',
    status='open'
)
print("Blood request created! Check logs above for dispatch output.")
