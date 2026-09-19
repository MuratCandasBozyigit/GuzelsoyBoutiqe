"""
Django settings for Gala Butik e-commerce project.
"""

from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-hj)t#ynp_q2**42f*(o1j0vseu*bmmm13t!sac!pt%lro&%tk_gala_boutique')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG', 'True') == 'True'

ALLOWED_HOSTS = ['*']
CSRF_TRUSTED_ORIGINS = ['https://*.vercel.app', 'https://*.now.sh', 'http://127.0.0.1', 'http://localhost']

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'whitenoise.runserver_nostatic',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    # Gala Butik Store App
    'store.apps.StoreConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'gala_project.urls'

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
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                # Store-wide categories and cart data
                'store.context_processors.store_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'gala_project.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'tr'
TIME_ZONE = 'Europe/Istanbul'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'

# Media files (Product uploads, category banners)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Boutique Business Settings
BOUTIQUE_NAME = "Gala Butik"
BOUTIQUE_SLOGAN = "Zarafet ve Konforun Büyük Beden Buluşması"
BOUTIQUE_PHONE = "+90 (850) 305 42 52"
BOUTIQUE_WHATSAPP = "+90 (532) 000 00 00"
BOUTIQUE_EMAIL = "destek@galabutik.com"
BOUTIQUE_ADDRESS = "Nişantaşı, Teşvikiye Cad. No:42 Şişli / İstanbul"

# E-commerce Rules
FREE_SHIPPING_THRESHOLD = 750.00  # TL
DEFAULT_SHIPPING_FEE = 69.90     # TL
MAX_INSTALLMENTS_ALLOWED = 3     # Turkish textile & clothing regulation constraint (Max 3 Taksit)

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
