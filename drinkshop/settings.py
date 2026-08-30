"""
Django settings for the drinkshop project (drink e-commerce + delivery).
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Load variables from a .env file in the project root, if present.
try:
    from dotenv import load_dotenv
    load_dotenv(BASE_DIR / '.env')
except ImportError:
    pass

# ---------------------------------------------------------------------------
# Core / security
# ---------------------------------------------------------------------------
SECRET_KEY = os.environ.get(
    'DJANGO_SECRET_KEY',
    'dev-only-secret-key-change-me-before-deploying'
)

DEBUG = os.environ.get('DJANGO_DEBUG', 'True') == 'True'

ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', '*').split(',')

CSRF_TRUSTED_ORIGINS = [
    o for o in os.environ.get('DJANGO_CSRF_TRUSTED_ORIGINS', '').split(',') if o
]

# ---------------------------------------------------------------------------
# Applications
# ---------------------------------------------------------------------------
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',

    # Media storage
    'cloudinary_storage',
    'cloudinary',

    # Auth
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',

    'store',
    'orders',
    'payments',
]

SITE_ID = 1

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
]

ROOT_URLCONF = 'drinkshop.urls'

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
                'store.context_processors.cart',
                'store.context_processors.site_settings',
            ],
        },
    },
]

WSGI_APPLICATION = 'drinkshop.wsgi.application'

# ---------------------------------------------------------------------------
# Database
# Defaults to SQLite for easy local dev. Point DATABASE_URL-style env vars
# at Postgres/MySQL in production (see README).
# ---------------------------------------------------------------------------
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# ---------------------------------------------------------------------------
# Password validation
# ---------------------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ---------------------------------------------------------------------------
# Internationalization
# ---------------------------------------------------------------------------
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Africa/Nairobi'
USE_I18N = True
USE_TZ = True

# ---------------------------------------------------------------------------
# Static & media files
# Product images (and any other uploaded media) are stored on Cloudinary
# instead of local disk — required for hosts with an ephemeral filesystem,
# and gives free image CDN/transformations. Get credentials from
# https://cloudinary.com/console.
# ---------------------------------------------------------------------------
STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'

CLOUDINARY_STORAGE = {
    'CLOUD_NAME': os.environ.get('CLOUDINARY_CLOUD_NAME', ''),
    'API_KEY': os.environ.get('CLOUDINARY_API_KEY', ''),
    'API_SECRET': os.environ.get('CLOUDINARY_API_SECRET', ''),
}

if CLOUDINARY_STORAGE['CLOUD_NAME']:
    DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
else:
    # No Cloudinary credentials configured yet — fall back to local disk so
    # `runserver` still works out of the box during initial setup.
    MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ---------------------------------------------------------------------------
# Auth redirects
# ---------------------------------------------------------------------------
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

LOGIN_URL = 'account_login'
LOGIN_REDIRECT_URL = 'store:home'
LOGOUT_REDIRECT_URL = 'store:home'

# ---------------------------------------------------------------------------
# django-allauth
# Email+password signup/login plus "Sign in with Google". Username is kept
# (not just email) since existing accounts/migrations use it; allauth will
# ask for one on signup unless you flip ACCOUNT_USERNAME_REQUIRED off.
# ---------------------------------------------------------------------------
ACCOUNT_EMAIL_VERIFICATION = os.environ.get('ACCOUNT_EMAIL_VERIFICATION', 'optional')
ACCOUNT_LOGIN_METHODS = {'username', 'email'}
ACCOUNT_SIGNUP_FIELDS = ['email*', 'username*', 'password1*', 'password2*']
ACCOUNT_UNIQUE_EMAIL = True
SOCIALACCOUNT_LOGIN_ON_GET = True  # skip the "confirm" page, go straight to Google
SOCIALACCOUNT_AUTO_SIGNUP = True

SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'APP': {
            'client_id': os.environ.get('GOOGLE_OAUTH_CLIENT_ID', ''),
            'secret': os.environ.get('GOOGLE_OAUTH_CLIENT_SECRET', ''),
            'key': '',
        },
        'SCOPE': ['profile', 'email'],
        'AUTH_PARAMS': {'access_type': 'online'},
    }
}

# ---------------------------------------------------------------------------
# Email — used for password reset and (optional) signup verification.
# ---------------------------------------------------------------------------
EMAIL_HOST = os.environ.get('EMAIL_HOST', '')
if EMAIL_HOST:
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_PORT = int(os.environ.get('EMAIL_PORT', '587'))
    EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
    EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '').replace(' ', '')
    EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True') == 'True'
    EMAIL_USE_SSL = os.environ.get('EMAIL_USE_SSL', 'False') == 'True'
else:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'DrinkShop <noreply@drinkshop.local>')

# ---------------------------------------------------------------------------
# Shop settings
# ---------------------------------------------------------------------------
# Delivery fee in KES, charged per order (flat-rate; customize per zone later).
DELIVERY_FEE = int(os.environ.get('DELIVERY_FEE', '150'))

# If True, alcoholic products (Product.is_alcoholic=True) cannot be sold /
# delivered via this site. Kenya's NACADA rules currently restrict online
# sale and home delivery of alcohol — keep this True unless your legal
# situation changes. See README for details.
DISALLOW_ALCOHOL_DELIVERY = os.environ.get('DISALLOW_ALCOHOL_DELIVERY', 'True') == 'True'

# ---------------------------------------------------------------------------
# M-Pesa Daraja API settings (Safaricom)
# Get these from https://developer.safaricom.co.ke after creating an app.
# Leave the sandbox defaults in place for testing.
# ---------------------------------------------------------------------------
MPESA_ENV = os.environ.get('MPESA_ENV', 'sandbox')  # 'sandbox' or 'production'
MPESA_CONSUMER_KEY = os.environ.get('MPESA_CONSUMER_KEY', '')
MPESA_CONSUMER_SECRET = os.environ.get('MPESA_CONSUMER_SECRET', '')
MPESA_SHORTCODE = os.environ.get('MPESA_SHORTCODE', '174379')  # sandbox default
MPESA_PASSKEY = os.environ.get('MPESA_PASSKEY', '')
MPESA_CALLBACK_URL = os.environ.get(
    'MPESA_CALLBACK_URL', 'https://example.com/payments/mpesa/callback/'
)

if MPESA_ENV == 'production':
    MPESA_AUTH_URL = 'https://api.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'
    MPESA_STK_PUSH_URL = 'https://api.safaricom.co.ke/mpesa/stkpush/v1/processrequest'
    MPESA_STK_QUERY_URL = 'https://api.safaricom.co.ke/mpesa/stkpushquery/v1/query'
else:
    MPESA_AUTH_URL = 'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'
    MPESA_STK_PUSH_URL = 'https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest'
    MPESA_STK_QUERY_URL = 'https://sandbox.safaricom.co.ke/mpesa/stkpushquery/v1/query'
