# Contributing to BloodConnect 🩸

Thank you for contributing to BloodConnect!

We welcome bug fixes, documentation improvements, UI enhancements, and new features that improve the platform for blood donors, seekers, and hospitals.

---

## 📌 Before You Start

- Check existing issues before creating a new one.
- Create an issue first for major changes.
- Keep pull requests focused and small.

---

## 🚀 Getting Started

### 1) Fork the Repository

Click the **Fork** button on GitHub and clone your fork locally.

```bash
git clone https://github.com/YOUR_USERNAME/Blood-Connect-By-ChronalLabs.git
cd Blood-Connect-By-ChronalLabs
```

### 2) Create a Virtual Environment

**Linux / macOS**

```bash
python -m venv venv
source venv/bin/activate
```

**Windows**

```bat
python -m venv venv
venv\Scripts\activate
```

### 3) Install Dependencies

```bash
pip install -r requirements.txt
```

---

## ⚙️ Environment Setup

Create a `.env` file from the example file:

```bash
cp .env.example .env
```

Then update:

```env
SECRET_KEY=your-secret-key
DEBUG=True
```

---

## 🗄️ Database Setup

Run migrations:

```bash
python manage.py makemigrations users donors seekers hospitals blood_requests
python manage.py migrate
```

Create an admin account:

```bash
python manage.py createsuperuser
```

---

## ▶️ Running the Development Server

Start the server:

```bash
python manage.py runserver
```

Visit:

http://127.0.0.1:8000

---

## 🧪 Running Tests

Run tests:

```bash
python manage.py test
```

---

## 🌱 Branch Naming Convention

Use meaningful branch names.

- **Feature branches**: `feat/add-hospital-search`
- **Bug fixes**: `fix/navbar-active-state`
- **Documentation**: `docs/update-readme`

---

## 📝 Code Style Guidelines

- Follow **PEP 8** for Python code.
- Use meaningful variable and function names.
- Keep views and services modular.
- Avoid unnecessary comments.
- Use **Bootstrap 5** classes consistently for UI updates.

---

## 📂 Project Structure

Main Django apps:

- `users/` — User authentication & profiles
- `donors/` — Donor functionality
- `seekers/` — Blood seekers
- `hospitals/` — Hospital management
- `blood_requests/` — Emergency blood requests
- `requests_app/` — Request handling

Static files:

- `static/css/`
- `static/js/`
- `templates/`

---

## 🔀 Pull Request Process

1. Fork the repository.
2. Create a new branch.
3. Commit your changes.
4. Push to your fork.
5. Open a Pull Request.

Example:

```bash
git checkout -b docs/add-contributing-guide
git add .
git commit -m "docs: add CONTRIBUTING.md"
git push origin docs/add-contributing-guide
```

---

## ✅ Pull Request Checklist

Before submitting your PR:

- Code runs without errors.
- No sensitive information added.
- Documentation updated if needed.
- PR title clearly explains the change.
- Branch is up to date with `main`.

---

## 💡 Good First Contributions

You can contribute by:

- Improving UI/UX
- Fixing bugs
- Adding tests
- Improving documentation
- Optimizing queries
- Improving accessibility

---

## ❤️ Thank You

Your contributions help make BloodConnect better and more accessible during emergencies.

---

*Tip: Add this section in your `README.md` near the bottom:*

```md
## 🤝 Contributing

We welcome contributions from the community.

Please read the [CONTRIBUTING.md](CONTRIBUTING.md) guide before submitting a pull request.
```

