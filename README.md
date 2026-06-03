# 🩸 BloodConnect

**BloodConnect** is a production-ready web platform connecting Blood Donors, Seekers, and Hospitals during emergencies.

Want to contribute? Check out our [Contributing Guide](CONTRIBUTING.md) to get started!

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

### 5. Load Sample Data (Seeding)

To populate the application with a high-fidelity, realistic, and fully connected sample dataset (including donors, seekers, verified hospitals, blood stock levels, emergency requests, and dynamic responses) for local testing or demo environments, run:

```bash
python manage.py seed_data
```

*   **Secure & Hashed:** All generated accounts are safely hashed and configured with a development password: `demo_password123`.
*   **Idempotency:** The seeder is completely idempotent. You can run it multiple times without creating duplicate records.
*   **Safe Clean/Reset:** To wipe only the demo data and return the database to a clean baseline (without touching non-demo or real data), run:
    ```bash
    python manage.py seed_data --clear
    ```

#### 📊 Populated Application Preview

After seeding, the home dashboard and live hospital locator map will look fully active and functional:

| Seeker & Donor Metrics Dashboard | Verified Hospitals & Proximity Map |
|:---:|:---:|
| ![Seeker & Donor Metrics](public/screenshots/dashboard.png) | ![Verified Hospitals & Map](public/screenshots/map.jpg) |

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

## 👥 Contributing

We love contributions! Please read our [CONTRIBUTING.md](CONTRIBUTING.md) to learn how to fork the repository, set up local development, run tests, and submit a pull request.

---

## 📄 License

MIT License — Free to use and modify.
