# 🩸 BloodConnect

**BloodConnect** is a production-ready web platform connecting Blood Donors, Seekers, and Hospitals during emergencies.

---

## 📋 Tech Stack

| Layer       | Technology                    |
|-------------|-------------------------------|
| Backend     | Python Django 4.2             |
| Database    | SQLite (dev) / PostgreSQL (prod) |
| Frontend    | HTML5, CSS3, Bootstrap 5      |
| Maps        | Leaflet.js (OpenStreetMap)    |
| Auth        | Django Authentication         |
| Admin       | Django Admin                  |

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- pip

### 1. Clone & Setup

```bash
cd bloodconnect
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env and set your SECRET_KEY
```

### 3. Run Migrations

```bash
python manage.py makemigrations users donors seekers hospitals blood_requests
python manage.py migrate
```

### 4. Create Superuser (Admin)

```bash
python manage.py createsuperuser
```

### 5. Load Sample Data (Optional)

```bash
python manage.py shell
```

Then paste:
```python
from users.models import CustomUser
from hospitals.models import HospitalProfile, BloodStock
from donors.models import DonorProfile

# Create a sample hospital
u = CustomUser.objects.create_user('hospital1', password='pass123', role='hospital', first_name='City', last_name='Hospital')
h = HospitalProfile.objects.create(user=u, hospital_name='City General Hospital', address='123 Main St', city='Mumbai', state='Maharashtra', pincode='400001', contact_number='9999888777', verified=True, blood_bank_available=True, latitude=19.0760, longitude=72.8777)
BloodStock.objects.create(hospital=h, a_positive=15, b_positive=8, o_positive=20, ab_positive=5, a_negative=3)
```

### 6. Collect Static Files

```bash
python manage.py collectstatic
```

### 7. Start Development Server

```bash
python manage.py runserver
```

Visit: **http://127.0.0.1:8000**

---

## 🌐 URLs

| URL | Description |
|-----|-------------|
| `/` | Home page |
| `/users/login/` | Login |
| `/users/register/` | Register |
| `/users/dashboard/` | Dashboard (role-based) |
| `/donors/dashboard/` | Donor dashboard |
| `/seekers/dashboard/` | Seeker dashboard |
| `/hospitals/dashboard/` | Hospital dashboard |
| `/hospitals/list/` | All hospitals with map |
| `/requests/list/` | All blood requests |
| `/about/` | About page |
| `/contact/` | Contact form |
| `/admin/` | Django Admin panel |

---

## 👥 User Roles

### Donor
- Register with medical info (blood group, RH factor, health conditions)
- See matching blood requests
- Record donation history
- Update availability status

### Seeker
- Create emergency blood requests
- Search donors by blood type and city
- View nearby hospitals

### Hospital
- Manage blood stock inventory (A+, A-, B+, B-, O+, O-, AB+, AB-)
- View emergency requests
- Add/manage staff members
- Get verified by admin

### Admin
- Full Django Admin access at `/admin/`
- Verify hospitals
- Manage all users, requests, and donations

---

## 🗺️ Map Features

Uses **Leaflet.js** with OpenStreetMap tiles:
- Hospital locations
- Emergency request markers
- User's current location
- Interactive popups with contact info

---

## 📊 Database Models

```
CustomUser          - Extended user with role
EmergencyContact    - Emergency contact per user
DonorProfile        - Medical info for donors
SeekerProfile       - Profile for seekers
HospitalProfile     - Hospital details
HospitalEmployee    - Staff members
BloodStock          - Blood inventory per hospital
BloodRequest        - Emergency blood requests
DonorResponse       - Donor responses to requests
BloodDonationHistory - Donation records
```

---

## 🔧 Production Deployment

### PostgreSQL Setup

```env
DATABASE_URL=postgres://user:password@host:5432/bloodconnect
```

### Environment Variables

```env
SECRET_KEY=<strong-random-key>
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
```

### Static Files

```bash
python manage.py collectstatic
```

Use **WhiteNoise** (already configured) or serve via Nginx.

---

## 📞 Google Sheets Contact Form

1. Create a Google Apps Script Web App
2. Set up a POST handler to write to a spreadsheet
3. Add the Web App URL to `.env`:

```env
GOOGLE_SHEETS_CREDENTIALS=https://script.google.com/macros/s/YOUR_ID/exec
```

---

## 🎨 Design

- **Primary Color**: `#d62828` (Blood Red)
- **Secondary Color**: `#34c1c6` (Teal)
- **Theme**: Dark health-tech
- **Fonts**: Syne (headings) + Plus Jakarta Sans (body)
- **Components**: Bootstrap 5 + Custom CSS

---

## 📄 License

MIT License — Free to use and modify.
