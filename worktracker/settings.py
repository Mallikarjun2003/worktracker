import os
from pathlib import Path
from django.core.exceptions import ImproperlyConfigured

# --------------------
# BASE DIR
# --------------------
BASE_DIR = Path(__file__).resolve().parent.parent

# --------------------
# SECRET KEY
# --------------------
# Use environment variable in production
SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret')
if not SECRET_KEY:
    raise ImproperlyConfigured("SECRET_KEY environment variable is not set!")

# --------------------
# DEBUG
# --------------------
DEBUG = os.environ.get('DEBUG', 'True') == 'True'

# --------------------
# ALLOWED HOSTS
# --------------------
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '*').split(',')

# --------------------
# INSTALLED APPS
# --------------------
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'tracker',
]

# --------------------
# MIDDLEWARE
# --------------------
MIDDLEWARE = [
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Must be first for static files
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# --------------------
# URLS & TEMPLATES
# --------------------
ROOT_URLCONF = 'worktracker.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'worktracker.wsgi.application'

# --------------------
# DATABASE
# --------------------
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# --------------------
# AUTH PASSWORD VALIDATORS
# --------------------
AUTH_PASSWORD_VALIDATORS = []

# --------------------
# INTERNATIONALIZATION
# --------------------
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True

# --------------------
# STATIC FILES
# --------------------
STATIC_URL = '/static/'

# Where Django will look for static files in dev
STATICFILES_DIRS = [BASE_DIR / 'static']

# Where collectstatic will copy all static files for production
STATIC_ROOT = BASE_DIR / 'staticfiles'

# WhiteNoise storage for compression & caching
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# --------------------
# SECURITY SETTINGS (Production)
# --------------------
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    X_FRAME_OPTIONS = 'DENY'
