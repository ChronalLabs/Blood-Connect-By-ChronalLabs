# Contributing to BloodConnect 🩸

Thank you for your interest in contributing to **BloodConnect**! Your support is vital in making this platform more robust and reliable during medical emergencies.

This document outlines the workflows, standards, and setup instructions to help you make successful contributions.

---

## 🧭 Code of Conduct

We expect all contributors to adhere to a respectful and inclusive code of conduct. Please treat other community members with empathy, kindness, and respect.

---

## 🛠️ Local Development Setup

To run BloodConnect on your local system, follow these steps:

### 1. Prerequisites
Ensure you have the following installed:
- **Python 3.10+**
- **pip** (Python package installer)
- **Virtualenv** (or Python's built-in `venv` module)

### 2. Fork and Clone
1. Fork the BloodConnect repository on GitHub by clicking the **Fork** button.
2. Clone your forked repository locally:
   ```bash
   git clone https://github.com/YOUR-USERNAME/Blood-Connect-By-ChronalLabs.git
   cd Blood-Connect-By-ChronalLabs
   ```

### 3. Create a Virtual Environment
Initialize a local virtual environment:
```bash
python3 -m venv venv
```
Activate the environment:
- **macOS and Linux:**
  ```bash
  source venv/bin/activate
  ```
- **Windows (CMD):**
  ```cmd
  venv\Scripts\activate.bat
  ```
- **Windows (PowerShell):**
  ```powershell
  venv\Scripts\Activate.ps1
  ```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Configure Environment Variables
Create a local `.env` configuration file from the example template:
```bash
cp .env.example .env
```
Open `.env` and configure your settings:
- Update the `SECRET_KEY` with a secure random key.
- Set `DEBUG=True` for local development.

### 6. Run Database Migrations
Initialize the SQLite database and run the Django migrations:
```bash
python manage.py makemigrations users donors seekers hospitals blood_requests
python manage.py migrate
```

### 7. Create a Superuser
Create an admin account to access the Django admin panel (`/admin/`):
```bash
python manage.py createsuperuser
```

### 8. Collect Static Files
Generate static file directories for local testing:
```bash
python manage.py collectstatic
```

### 9. Start the Development Server
```bash
python manage.py runserver
```
Visit **http://127.0.0.1:8000** in your browser to see the live app!

---

## 🧪 Running Tests

Always run tests before pushing code or submitting a Pull Request.

Run the entire Django test suite:
```bash
python manage.py test
```

To run a specific test file (for example, the blood compatibility tests):
```bash
python manage.py test blood_requests.tests.test_compatibility
```

---

## 🌿 Git Branching Workflow

We follow structured conventions for branch names and commit messages.

### Branch Naming Convention
Please create a new branch from `main` using one of the following prefixes:

| Branch Prefix | Purpose | Example |
| :--- | :--- | :--- |
| `feat/` | Adding a new feature | `feat/hospital-dashboard` |
| `fix/` | Fixing a bug | `fix/compatibility-test-city` |
| `docs/` | Documentation improvements | `docs/add-contributing-guide` |
| `refactor/` | Code refactoring (no functional changes) | `refactor/blood-matching-logic` |
| `chore/` | Build scripts, tasks, dependencies, etc. | `chore/update-readme` |

### Commit Message Guidelines
Keep your commit messages atomic, descriptive, and in the imperative mood:
- **Good:** `feat: add donor availability status toggle`
- **Good:** `fix: resolve duplicate keyword error in compatibility tests`
- **Bad:** `fixed bug` or `updates`

---

## 🚀 Submitting a Pull Request (PR)

Once you are ready to submit your changes, follow these steps:

1. **Commit and Push:**
   Commit your changes and push your branch to your GitHub fork:
   ```bash
   git push origin <your-branch-name>
   ```
2. **Open the PR:**
   Go to the original BloodConnect repository on GitHub. You should see a prompt to open a Pull Request. Click **Compare & pull request**.
3. **Fill Out the PR Description:**
   - Clearly describe what changes were made.
   - Reference any relevant issues (e.g. `Closes #37`).
   - Mention what manual or automated testing was performed.
4. **Review Process:**
   Project maintainers will review your code. Please address any comments or requested changes in a timely manner. Once approved, your PR will be merged into the `main` branch!

---

Thank you again for contributing to **BloodConnect**! Let's save lives together! 🩸❤️
