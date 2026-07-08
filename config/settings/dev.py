from .base import *

DEBUG = True

ALLOWED_HOSTS = ['*']

# SQLite for local dev
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Console email for development
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# CORS - allow all in dev
CORS_ALLOW_ALL_ORIGINS = True

# Django debug toolbar (optional)
INTERNAL_IPS = ['127.0.0.1']

# Allauth - skip email verification in dev
ACCOUNT_EMAIL_VERIFICATION = 'none'


# ─── CSRF ────────────────────────────────────────────────────
CSRF_TRUSTED_ORIGINS = [
    'http://localhost:8000',
    'http://127.0.0.1:8000',
    'http://localhost',
    'http://127.0.0.1',
]

# Ensure session and CSRF cookies work correctly in dev
CSRF_COOKIE_SAMESITE  = 'Lax'
SESSION_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_HTTPONLY  = False  # must be False so JS can read it if needed