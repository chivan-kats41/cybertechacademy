# CyberTech Academy 🚀
> *"Empowering the Next Generation of Tech Innovators"*

A professional online Learning Management System (LMS) built with Django 6 + Django REST Framework.

---

## 📞 Contact
| | |
|---|---|
| Phone 1 | +256 705 221 604 |
| Phone 2 | +256 762 899 641 |
| Email   | chivankats@gmail.com |

---

## ⚡ Quick Setup (Windows PowerShell)

### 1. Clone / navigate to project
```powershell
cd C:\path\to\your\projects
```

### 2. Create project folder & virtual environment
```powershell
mkdir cybertech_academy
cd cybertech_academy
python -m venv venv
```

### 3. Activate the virtual environment
```powershell
.\venv\Scripts\Activate.ps1
```
> If you get an execution policy error, run this first (as Administrator):
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```

### 4. Install all dependencies
```powershell
pip install -r requirements.txt
```

### 5. Set up environment variables
```powershell
Copy-Item .env.example .env
notepad .env   # Fill in your SECRET_KEY, DB credentials, email, Flutterwave keys
```

### 6. Run migrations
```powershell
python manage.py makemigrations
python manage.py migrate
```

### 7. Create a superadmin
```powershell
python manage.py createsuperuser
```

### 8. Collect static files (production only)
```powershell
python manage.py collectstatic
```

### 9. Run the development server
```powershell
python manage.py runserver
```
Open: http://127.0.0.1:8000
Admin: http://127.0.0.1:8000/admin

---

## 🗂️ Project Structure

```
cybertech_academy/
├── config/                     # Core Django config
│   ├── settings/
│   │   ├── base.py             # Shared settings
│   │   ├── dev.py              # Development (SQLite)
│   │   └── prod.py             # Production (PostgreSQL)
│   ├── urls.py                 # Root URL routing
│   ├── wsgi.py
│   └── asgi.py
│
├── apps/
│   ├── accounts/               # Custom User model + Auth
│   ├── courses/                # Course → Module → Lesson
│   ├── students/               # Registration, Enrollment, Progress
│   ├── zoom_sessions/          # Live sessions + Payments
│   ├── payments/               # Flutterwave integration
│   └── core/                   # Homepage, contact, shared
│
├── templates/                  # Django HTML templates
│   ├── core/
│   ├── courses/
│   ├── students/
│   ├── zoom_sessions/
│   └── accounts/
│
├── static/                     # CSS, JS, Images
│   ├── css/
│   ├── js/
│   └── images/
│
├── media/                      # User-uploaded files
├── venv/                       # Virtual environment (git-ignored)
├── manage.py
├── requirements.txt
├── .env                        # Secret config (git-ignored)
└── .env.example                # Template for .env
```

---

## 🛢️ Database Models Summary

| App | Models |
|---|---|
| `accounts` | `User` (UUID PK, roles: superadmin/instructor/student) |
| `courses` | `Category`, `Course`, `Module`, `Lesson` |
| `students` | `StudentProfile`, `Enrollment`, `LessonProgress` |
| `zoom_sessions` | `ZoomSession`, `ZoomPayment` |
| `payments` | `CoursePayment`, `FlutterwaveTransaction` |

---

## 🔑 Environment Variables (.env)

```env
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# PostgreSQL (prod only)
DB_NAME=cybertech_db
DB_USER=cybertech_user
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432

# Email (Gmail SMTP)
EMAIL_HOST_USER=chivankats@gmail.com
EMAIL_HOST_PASSWORD=your_app_password

# Flutterwave
FLUTTERWAVE_PUBLIC_KEY=FLWPUBK-xxxx
FLUTTERWAVE_SECRET_KEY=FLWSECK-xxxx
FLUTTERWAVE_ENCRYPTION_KEY=xxxxxxxxxx
```

---

## 🚀 Switching Between Dev and Production

```powershell
# Development (SQLite, console email)
$env:DJANGO_SETTINGS_MODULE = "config.settings.dev"
python manage.py runserver

# Production (PostgreSQL, real email)
$env:DJANGO_SETTINGS_MODULE = "config.settings.prod"
python manage.py runserver
```

---

## 🎨 Design System

| Token | Value |
|---|---|
| Primary BG | `#0A0E1A` (deep navy black) |
| Accent Cyan | `#00F5FF` (electric cyan) |
| Accent Green | `#39FF14` (neon green) |
| Text Primary | `#FFFFFF` |
| Text Muted | `#8892A4` |
| Font Display | Orbitron / Exo 2 |
| Font Body | Inter / DM Sans |

