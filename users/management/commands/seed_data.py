"""
BloodConnect Demo Data Seeding Management Command
Provides robust, realistic, and idempotent demo data for development and testing.
"""
import random
from datetime import date, timedelta
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from django.contrib.auth import get_user_model

from users.models import CustomUser, EmergencyContact
from donors.models import DonorProfile, BloodDonationHistory
from seekers.models import SeekerProfile
from hospitals.models import HospitalProfile, BloodStock, HospitalEmployee
from blood_requests.models import BloodRequest, DonorResponse, DonorNotification

User = get_user_model()

# Configuration constants
DEMO_PREFIX = "demo_"
DEV_PASSWORD = "demo_password123"

CITIES = {
    'Mumbai': {'lat': 19.0760, 'lon': 72.8777, 'state': 'Maharashtra', 'pincode': '400001'},
    'Pune': {'lat': 18.5204, 'lon': 73.8567, 'state': 'Maharashtra', 'pincode': '411001'},
    'Bangalore': {'lat': 12.9716, 'lon': 77.5946, 'state': 'Karnataka', 'pincode': '560001'},
    'Delhi': {'lat': 28.6139, 'lon': 77.2090, 'state': 'Delhi', 'pincode': '110001'},
}

BLOOD_GROUPS = ['A', 'B', 'AB', 'O']
RH_FACTORS = ['+', '-']

HOSPITAL_DETAILS = [
    {
        'username': 'demo_hospital_mumbai_1',
        'hospital_name': 'Mumbai Lifeline Medical Center',
        'city': 'Mumbai',
        'address': '🏥 405, Marine Drive, Near Nariman Point',
        'contact': '9811112222',
        'type': 'private',
        'reg_num': 'HOSP-MUM-001',
    },
    {
        'username': 'demo_hospital_mumbai_2',
        'hospital_name': 'Mumbai City General Hospital',
        'city': 'Mumbai',
        'address': '🏥 12, Dr. E Moses Rd, Worli',
        'contact': '9811112223',
        'type': 'government',
        'reg_num': 'HOSP-MUM-002',
    },
    {
        'username': 'demo_hospital_pune',
        'hospital_name': 'Pune Care & Trust Hospital',
        'city': 'Pune',
        'address': '🏥 78, F.C. Road, Shivajinagar',
        'contact': '9822223333',
        'type': 'trust',
        'reg_num': 'HOSP-PUN-001',
    },
    {
        'username': 'demo_hospital_bangalore',
        'hospital_name': 'Bangalore Global Health Hospital',
        'city': 'Bangalore',
        'address': '🏥 102, 100 Feet Rd, Indiranagar',
        'contact': '9833334444',
        'type': 'private',
        'reg_num': 'HOSP-BLR-001',
    },
    {
        'username': 'demo_hospital_delhi',
        'hospital_name': 'Delhi Metro Super Specialty Hospital',
        'city': 'Delhi',
        'address': '🏥 25, Ring Road, Lajpat Nagar',
        'contact': '9844445555',
        'type': 'semi-govt',
        'reg_num': 'HOSP-DEL-001',
    },
]

DONOR_DETAILS = [
    {'username': 'demo_donor_mumbai_1', 'first_name': 'Aarav', 'last_name': 'Mehta', 'city': 'Mumbai', 'blood_group': 'O', 'rh_factor': '-', 'age': 28, 'weight': 72.5},
    {'username': 'demo_donor_mumbai_2', 'first_name': 'Diya', 'last_name': 'Sharma', 'city': 'Mumbai', 'blood_group': 'A', 'rh_factor': '+', 'age': 24, 'weight': 58.0},
    {'username': 'demo_donor_mumbai_3', 'first_name': 'Kabir', 'last_name': 'Patel', 'city': 'Mumbai', 'blood_group': 'B', 'rh_factor': '+', 'age': 35, 'weight': 81.0},
    {'username': 'demo_donor_mumbai_4', 'first_name': 'Ananya', 'last_name': 'Desai', 'city': 'Mumbai', 'blood_group': 'AB', 'rh_factor': '+', 'age': 31, 'weight': 63.5},
    {'username': 'demo_donor_pune_1', 'first_name': 'Rohan', 'last_name': 'Kulkarni', 'city': 'Pune', 'blood_group': 'O', 'rh_factor': '+', 'age': 29, 'weight': 75.0},
    {'username': 'demo_donor_pune_2', 'first_name': 'Neha', 'last_name': 'Joshi', 'city': 'Pune', 'blood_group': 'B', 'rh_factor': '-', 'age': 22, 'weight': 54.5},
    {'username': 'demo_donor_pune_3', 'first_name': 'Aditya', 'last_name': 'Shinde', 'city': 'Pune', 'blood_group': 'A', 'rh_factor': '-', 'age': 42, 'weight': 88.0},
    {'username': 'demo_donor_bangalore_1', 'first_name': 'Vikram', 'last_name': 'Rao', 'city': 'Bangalore', 'blood_group': 'O', 'rh_factor': '-', 'age': 30, 'weight': 70.0},
    {'username': 'demo_donor_bangalore_2', 'first_name': 'Meera', 'last_name': 'Nair', 'city': 'Bangalore', 'blood_group': 'AB', 'rh_factor': '-', 'age': 27, 'weight': 59.0},
    {'username': 'demo_donor_bangalore_3', 'first_name': 'Arjun', 'last_name': 'Gowda', 'city': 'Bangalore', 'blood_group': 'B', 'rh_factor': '+', 'age': 33, 'weight': 79.5},
    {'username': 'demo_donor_delhi_1', 'first_name': 'Rahul', 'last_name': 'Verma', 'city': 'Delhi', 'blood_group': 'O', 'rh_factor': '+', 'age': 26, 'weight': 73.0},
    {'username': 'demo_donor_delhi_2', 'first_name': 'Priyanka', 'last_name': 'Singh', 'city': 'Delhi', 'blood_group': 'A', 'rh_factor': '+', 'age': 28, 'weight': 61.0},
]

SEEKER_DETAILS = [
    {'username': 'demo_seeker_mumbai_1', 'first_name': 'Raj', 'last_name': 'Malhotra', 'city': 'Mumbai', 'blood_group': 'A', 'rh_factor': '+', 'hospital': 'Mumbai Lifeline Medical Center', 'patient': 'Savitri Malhotra'},
    {'username': 'demo_seeker_mumbai_2', 'first_name': 'Pooja', 'last_name': 'Kapoor', 'city': 'Mumbai', 'blood_group': 'O', 'rh_factor': '-', 'hospital': 'Mumbai City General Hospital', 'patient': 'Ramesh Kapoor'},
    {'username': 'demo_seeker_pune', 'first_name': 'Sanjay', 'last_name': 'Patil', 'city': 'Pune', 'blood_group': 'B', 'rh_factor': '-', 'hospital': 'Pune Care & Trust Hospital', 'patient': 'Sanjay Patil'},
    {'username': 'demo_seeker_bangalore', 'first_name': 'Karthik', 'last_name': 'Subramanian', 'city': 'Bangalore', 'blood_group': 'AB', 'rh_factor': '+', 'hospital': 'Bangalore Global Health Hospital', 'patient': 'Lakshmi S.'},
    {'username': 'demo_seeker_delhi_1', 'first_name': 'Amit', 'last_name': 'Gupta', 'city': 'Delhi', 'blood_group': 'O', 'rh_factor': '+', 'hospital': 'Delhi Metro Super Specialty Hospital', 'patient': 'Amit Gupta'},
    {'username': 'demo_seeker_delhi_2', 'first_name': 'Sonia', 'last_name': 'Bhasin', 'city': 'Delhi', 'blood_group': 'A', 'rh_factor': '-', 'hospital': 'Delhi Metro Super Specialty Hospital', 'patient': 'Karan Bhasin'},
]


def jitter(coord, amount=0.015):
    """Slightly adjust coordinates to avoid overlapping markers on the map."""
    return float(coord) + random.uniform(-amount, amount)


class Command(BaseCommand):
    help = "Seeds the database with realistic demo/sample data or clears previous demo data."

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Safely remove all demo-prefixed data instead of seeding.',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.clear_demo_data()
        else:
            self.seed_demo_data()

    def clear_demo_data(self):
        self.stdout.write(self.style.WARNING("Starting to clear demo data..."))
        
        # We query for users with username starting with DEMO_PREFIX.
        # Thanks to CASCADE delete constraints in the models, deleting these CustomUser entries
        # will cleanly cascade to delete:
        # EmergencyContact, DonorProfile, SeekerProfile, HospitalProfile, BloodStock,
        # HospitalEmployee, BloodRequest, DonorResponse, DonorNotification, and BloodDonationHistory
        demo_users = CustomUser.objects.filter(username__startswith=DEMO_PREFIX)
        count = demo_users.count()
        
        if count == 0:
            self.stdout.write(self.style.SUCCESS("No demo data found to clear."))
            return
            
        with transaction.atomic():
            demo_users.delete()
            
        self.stdout.write(self.style.SUCCESS(f"Successfully cleared {count} demo user accounts and all their associated profile and operational records."))

    def seed_demo_data(self):
        self.stdout.write(self.style.MIGRATE_HEADING("Populating database with premium demo data..."))
        
        # 12-digit mock Aadhaar tracker to keep them unique
        aadhaar_base = 100020003000

        with transaction.atomic():
            # 1. Seed Demo Administrator
            admin_username = f"{DEMO_PREFIX}admin"
            admin_user, created = CustomUser.objects.get_or_create(
                username=admin_username,
                defaults={
                    'first_name': 'System',
                    'last_name': 'Administrator',
                    'email': 'admin@demo-bloodconnect.org',
                    'role': 'admin',
                    'is_staff': True,
                    'is_superuser': True,
                    'is_verified': True,
                }
            )
            if created:
                admin_user.set_password(DEV_PASSWORD)
                admin_user.save()
                self.stdout.write(self.style.SUCCESS(f"Seeded Admin User: {admin_username}"))
            else:
                self.stdout.write(f"Admin User {admin_username} already exists.")

            # 2. Seed Hospitals
            hospitals_seeded = []
            for h_det in HOSPITAL_DETAILS:
                username = h_det['username']
                city_info = CITIES[h_det['city']]
                
                # Jitter coordinates slightly around city center
                lat = jitter(city_info['lat'])
                lon = jitter(city_info['lon'])
                
                aadhaar_base += 1
                
                user, created = CustomUser.objects.get_or_create(
                    username=username,
                    defaults={
                        'first_name': 'Hospital',
                        'last_name': h_det['hospital_name'].split()[-1],
                        'email': f"{username}@demo-bloodconnect.org",
                        'role': 'hospital',
                        'phone_number': h_det['contact'],
                        'address': h_det['address'],
                        'city': h_det['city'],
                        'state': city_info['state'],
                        'pincode': city_info['pincode'],
                        'latitude': lat,
                        'longitude': lon,
                        'aadhar_card_number': str(aadhaar_base),
                        'is_verified': True,
                    }
                )
                if created:
                    user.set_password(DEV_PASSWORD)
                    user.save()
                    
                # Create HospitalProfile
                profile, p_created = HospitalProfile.objects.get_or_create(
                    user=user,
                    defaults={
                        'hospital_name': h_det['hospital_name'],
                        'registration_number': h_det['reg_num'],
                        'address': h_det['address'],
                        'city': h_det['city'],
                        'state': city_info['state'],
                        'pincode': city_info['pincode'],
                        'contact_number': h_det['contact'],
                        'emergency_contact': h_det['contact'],
                        'hospital_type': h_det['type'],
                        'blood_bank_available': True,
                        'has_24hr_service': random.choice([True, False]),
                        'verified': True,
                        'verified_at': timezone.now(),
                        'latitude': lat,
                        'longitude': lon,
                        'description': f"Premium {h_det['type']} healthcare institution in {h_det['city']} fully equipped with direct testing and storage systems.",
                    }
                )
                
                # Create BloodStock (Initialize with premium, realistic volumes of bags)
                BloodStock.objects.get_or_create(
                    hospital=profile,
                    defaults={
                        'a_positive': random.randint(15, 45),
                        'a_negative': random.randint(2, 10),
                        'b_positive': random.randint(20, 50),
                        'b_negative': random.randint(3, 12),
                        'o_positive': random.randint(25, 60),
                        'o_negative': random.randint(4, 15),
                        'ab_positive': random.randint(5, 18),
                        'ab_negative': random.randint(1, 5),
                    }
                )
                
                # Create HospitalEmployee profiles
                first_names = ["Ramesh", "Priya", "Sunita", "Deepak", "Vikram"]
                last_names = ["Gupta", "Nair", "Iyer", "Choudhury", "Pande"]
                roles = ['doctor', 'nurse', 'technician', 'blood_bank_officer']
                
                for idx in range(3):
                    emp_name = f"Dr. {random.choice(first_names)} {random.choice(last_names)}" if idx == 0 else f"{random.choice(first_names)} {random.choice(last_names)}"
                    HospitalEmployee.objects.get_or_create(
                        hospital=profile,
                        name=emp_name,
                        contact_number=f"97111222{idx}{random.randint(0, 9)}",
                        defaults={
                            'role': roles[idx % len(roles)],
                            'employee_id': f"EMP-{h_det['reg_num'].split('-')[-1]}-{100 + idx}",
                            'verified': True,
                        }
                    )
                
                hospitals_seeded.append(profile)
                if created:
                    self.stdout.write(self.style.SUCCESS(f"Seeded Hospital: {h_det['hospital_name']} ({username})"))

            # 3. Seed Donors
            donors_seeded = []
            for d_det in DONOR_DETAILS:
                username = d_det['username']
                city_info = CITIES[d_det['city']]
                lat = jitter(city_info['lat'])
                lon = jitter(city_info['lon'])
                aadhaar_base += 1
                
                user, created = CustomUser.objects.get_or_create(
                    username=username,
                    defaults={
                        'first_name': d_det['first_name'],
                        'last_name': d_det['last_name'],
                        'email': f"{username}@demo-bloodconnect.org",
                        'role': 'donor',
                        'phone_number': f"99112233{random.randint(10, 99)}",
                        'address': f"🏠 Building {random.randint(10, 200)}, Street {random.randint(1, 10)}, {d_det['city']}",
                        'city': d_det['city'],
                        'state': city_info['state'],
                        'pincode': city_info['pincode'],
                        'latitude': lat,
                        'longitude': lon,
                        'aadhar_card_number': str(aadhaar_base),
                        'is_verified': True,
                    }
                )
                if created:
                    user.set_password(DEV_PASSWORD)
                    user.save()
                
                # Emergency Contact
                EmergencyContact.objects.get_or_create(
                    user=user,
                    defaults={
                        'name': f"{random.choice(['Suresh', 'Anita', 'Sunil'])} {d_det['last_name']}",
                        'phone_number': f"98223344{random.randint(10, 99)}",
                        'relationship': random.choice(['Father', 'Mother', 'Spouse', 'Sibling']),
                        'address': user.address,
                        'email': f"contact_{username}@demo-bloodconnect.org",
                    }
                )
                
                # Donor Profile
                avail = 'available'
                if username in ['demo_donor_mumbai_3', 'demo_donor_bangalore_1']:
                    avail = 'cooldown'
                elif username == 'demo_donor_pune_2':
                    avail = 'unavailable'
                    
                profile, p_created = DonorProfile.objects.get_or_create(
                    user=user,
                    defaults={
                        'blood_group': d_det['blood_group'],
                        'rh_factor': d_det['rh_factor'],
                        'age': d_det['age'],
                        'weight': d_det['weight'],
                        'any_disease': 'None',
                        'previous_injury': 'None',
                        'current_health_condition': 'Perfectly Healthy',
                        'medications': 'None',
                        'availability_status': avail,
                        'willing_to_travel': True,
                        'max_travel_distance': random.choice([5, 10, 15, 20]),
                        'last_blood_donation_date': date.today() - timedelta(days=random.randint(95, 200)) if avail == 'available' else date.today() - timedelta(days=random.randint(10, 45)),
                        'last_donation_hospital': 'City Red Cross Bank' if avail == 'cooldown' else '',
                        'total_donations': random.randint(2, 8),
                    }
                )
                
                # Pre-fill some donation history for donors who have already donated
                for i in range(profile.total_donations):
                    BloodDonationHistory.objects.get_or_create(
                        donor=profile,
                        donation_date=date.today() - timedelta(days=120 * (i + 1)),
                        defaults={
                            'hospital_name': random.choice(['Apollo Clinic', 'Fortis Care Center', 'Metro Red Cross']),
                            'units_donated': 1.0,
                            'verified_by_hospital': True,
                            'notes': 'Routine donation.',
                        }
                    )
                
                donors_seeded.append(profile)
                if created:
                    self.stdout.write(self.style.SUCCESS(f"Seeded Donor: {user.get_full_name()} ({d_det['blood_group']}{d_det['rh_factor']})"))

            # 4. Seed Seekers
            seekers_seeded = []
            for s_det in SEEKER_DETAILS:
                username = s_det['username']
                city_info = CITIES[s_det['city']]
                lat = jitter(city_info['lat'])
                lon = jitter(city_info['lon'])
                aadhaar_base += 1
                
                user, created = CustomUser.objects.get_or_create(
                    username=username,
                    defaults={
                        'first_name': s_det['first_name'],
                        'last_name': s_det['last_name'],
                        'email': f"{username}@demo-bloodconnect.org",
                        'role': 'seeker',
                        'phone_number': f"96112233{random.randint(10, 99)}",
                        'address': f"🏠 Flat {random.randint(1, 40)}, Tower {random.randint(1, 5)}, {s_det['city']}",
                        'city': s_det['city'],
                        'state': city_info['state'],
                        'pincode': city_info['pincode'],
                        'latitude': lat,
                        'longitude': lon,
                        'aadhar_card_number': str(aadhaar_base),
                        'is_verified': True,
                    }
                )
                if created:
                    user.set_password(DEV_PASSWORD)
                    user.save()
                
                # Emergency Contact
                EmergencyContact.objects.get_or_create(
                    user=user,
                    defaults={
                        'name': f"Guardian of {user.get_full_name()}",
                        'phone_number': f"95112233{random.randint(10, 99)}",
                        'relationship': 'Guardian',
                        'address': user.address,
                    }
                )
                
                # Seeker Profile
                profile, p_created = SeekerProfile.objects.get_or_create(
                    user=user,
                    defaults={
                        'blood_group': s_det['blood_group'],
                        'rh_factor': s_det['rh_factor'],
                        'hospital_name': s_det['hospital'],
                        'patient_name': s_det['patient'],
                    }
                )
                
                seekers_seeded.append(profile)
                if created:
                    self.stdout.write(self.style.SUCCESS(f"Seeded Seeker: {user.get_full_name()} ({username})"))

            # 5. Seed Blood Requests & Interactions
            # Let's create about 6 highly realistic blood requests
            requests_data = [
                {
                    'requester_username': 'demo_seeker_mumbai_1',
                    'patient_name': 'Savitri Malhotra',
                    'age': 67,
                    'blood_group': 'A',
                    'rh_factor': '+',
                    'units': 3,
                    'hospital_name': 'Mumbai Lifeline Medical Center',
                    'city': 'Mumbai',
                    'urgency': 'critical',
                    'status': 'in_progress',
                    'notes': 'Patient undergoing major heart bypass surgery tomorrow morning. Urgently need matching donors.',
                },
                {
                    'requester_username': 'demo_seeker_mumbai_2',
                    'patient_name': 'Ramesh Kapoor',
                    'age': 45,
                    'blood_group': 'O',
                    'rh_factor': '-',
                    'units': 2,
                    'hospital_name': 'Mumbai City General Hospital',
                    'city': 'Mumbai',
                    'urgency': 'critical',
                    'status': 'open',
                    'notes': 'Accident victim lost blood. Universal donor O- is critically required.',
                },
                {
                    'requester_username': 'demo_seeker_pune',
                    'patient_name': 'Sanjay Patil',
                    'age': 38,
                    'blood_group': 'B',
                    'rh_factor': '-',
                    'units': 2,
                    'hospital_name': 'Pune Care & Trust Hospital',
                    'city': 'Pune',
                    'urgency': 'urgent',
                    'status': 'fulfilled',
                    'notes': 'Required for severe anemia treatment.',
                },
                {
                    'requester_username': 'demo_hospital_bangalore',
                    'patient_name': 'Rohit Kumar (Emergency Ward)',
                    'age': 19,
                    'blood_group': 'B',
                    'rh_factor': '+',
                    'units': 4,
                    'hospital_name': 'Bangalore Global Health Hospital',
                    'city': 'Bangalore',
                    'urgency': 'critical',
                    'status': 'open',
                    'notes': 'Severe dengue case with plummeting platelet count.',
                },
                {
                    'requester_username': 'demo_seeker_delhi_1',
                    'patient_name': 'Amit Gupta',
                    'age': 52,
                    'blood_group': 'O',
                    'rh_factor': '+',
                    'units': 2,
                    'hospital_name': 'Delhi Metro Super Specialty Hospital',
                    'city': 'Delhi',
                    'urgency': 'moderate',
                    'status': 'open',
                    'notes': 'Scheduled hip replacement surgery later this week.',
                },
                {
                    'requester_username': 'demo_seeker_delhi_2',
                    'patient_name': 'Karan Bhasin',
                    'age': 12,
                    'blood_group': 'A',
                    'rh_factor': '-',
                    'units': 1,
                    'hospital_name': 'Delhi Metro Super Specialty Hospital',
                    'city': 'Delhi',
                    'urgency': 'normal',
                    'status': 'cancelled',
                    'notes': 'Patient discharged; blood was arranged locally.',
                },
            ]

            for req_det in requests_data:
                requester = CustomUser.objects.get(username=req_det['requester_username'])
                city_info = CITIES[req_det['city']]
                lat = jitter(city_info['lat'], amount=0.008)
                lon = jitter(city_info['lon'], amount=0.008)
                
                # Check for existing request
                blood_request, created = BloodRequest.objects.get_or_create(
                    requester=requester,
                    patient_name=req_det['patient_name'],
                    blood_group=req_det['blood_group'],
                    rh_factor=req_det['rh_factor'],
                    hospital_name=req_det['hospital_name'],
                    defaults={
                        'patient_age': req_det['age'],
                        'units_required': req_det['units'],
                        'units_fulfilled': req_det['units'] if req_det['status'] == 'fulfilled' else 0,
                        'hospital_address': f"{req_det['hospital_name']}, {req_det['city']}",
                        'hospital_contact': '9800088000',
                        'latitude': lat,
                        'longitude': lon,
                        'city': req_det['city'],
                        'urgency_level': req_det['urgency'],
                        'status': req_det['status'],
                        'additional_notes': req_det['notes'],
                        'required_by': timezone.now() + timedelta(days=1) if req_det['urgency'] in ['critical', 'urgent'] else timezone.now() + timedelta(days=4),
                        'fulfilled_at': timezone.now() - timedelta(hours=6) if req_det['status'] == 'fulfilled' else None,
                    }
                )
                
                if created:
                    self.stdout.write(self.style.SUCCESS(f"Seeded Blood Request: {req_det['patient_name']} - {req_det['blood_group']}{req_det['rh_factor']} ({req_det['status']})"))
                
                # Now set up realistic responses, notifications, and fulfillment linkages
                compatible_donors = DonorProfile.objects.filter(
                    blood_group=blood_request.blood_group,
                    rh_factor=blood_request.rh_factor
                )
                
                # 1. Populate notifications for open/in_progress requests
                for d_prof in compatible_donors:
                    DonorNotification.objects.get_or_create(
                        blood_request=blood_request,
                        donor=d_prof.user,
                        defaults={
                            'channel': 'email',
                            'status': 'sent',
                            'sent_at': timezone.now() - timedelta(minutes=30),
                        }
                    )
                
                # 2. Populate donor responses and complete cycles
                if req_det['status'] == 'in_progress' and compatible_donors.exists():
                    # Pick a donor and set them to "confirmed"
                    donor_profile = compatible_donors.first()
                    DonorResponse.objects.get_or_create(
                        blood_request=blood_request,
                        donor=donor_profile.user,
                        defaults={
                            'status': 'confirmed',
                            'message': "I am close by and can reach the hospital in 30 minutes! Please confirm.",
                        }
                    )
                
                elif req_det['status'] == 'fulfilled' and compatible_donors.exists():
                    # Pick a donor and mark donation history
                    donor_profile = compatible_donors.first()
                    
                    DonorResponse.objects.get_or_create(
                        blood_request=blood_request,
                        donor=donor_profile.user,
                        defaults={
                            'status': 'donated',
                            'message': "Donation successfully completed! Extremely happy to help.",
                        }
                    )
                    
                    # Log to their official history
                    BloodDonationHistory.objects.get_or_create(
                        donor=donor_profile,
                        blood_request=blood_request,
                        defaults={
                            'donation_date': date.today(),
                            'hospital_name': req_det['hospital_name'],
                            'units_donated': 1.0,
                            'verified_by_hospital': True,
                            'notes': f"Fulfilled emergency request for {req_det['patient_name']}.",
                        }
                    )
                    
                    # Update donor profile metrics
                    donor_profile.total_donations += 1
                    donor_profile.last_blood_donation_date = date.today()
                    donor_profile.availability_status = 'cooldown'
                    donor_profile.save()
                    
                elif req_det['status'] == 'open' and compatible_donors.count() >= 2:
                    # Let one donor express interest and one donor cancel to simulate normal activity
                    d1, d2 = list(compatible_donors)[:2]
                    DonorResponse.objects.get_or_create(
                        blood_request=blood_request,
                        donor=d1.user,
                        defaults={
                            'status': 'interested',
                            'message': "Ready to donate! Please coordinate the timing.",
                        }
                    )
                    
                    DonorResponse.objects.get_or_create(
                        blood_request=blood_request,
                        donor=d2.user,
                        defaults={
                            'status': 'cancelled',
                            'message': "Sorry, something came up at work. I won't be able to make it today.",
                        }
                    )

        self.stdout.write(self.style.SUCCESS("Database seeding completed perfectly!"))
        self.stdout.write(self.style.SUCCESS(f"All generated accounts are secured with password: '{DEV_PASSWORD}'"))
