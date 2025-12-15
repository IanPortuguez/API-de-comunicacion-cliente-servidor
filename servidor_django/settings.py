"""
Configuración principal del proyecto Django.

Este archivo define la configuración global del sistema, incluyendo:
- Aplicaciones instaladas
- Middleware
- Base de datos
- Seguridad
- Archivos estáticos y multimedia
- Configuración de CORS
- Django Rest Framework
- Almacenamiento local o en S3 según entorno

Main Django project configuration.

This file defines the global system configuration, including:
- Installed applications
- Middleware
- Database
- Security
- Static and media files
- CORS configuration
- Django Rest Framework
- Local or S3 storage depending on environment
"""

import dj_database_url
import os
from pathlib import Path
from corsheaders.defaults import default_headers


# === BASE CONFIGURATION / CONFIGURACIÓN BASE ===
BASE_DIR = Path(__file__).resolve().parent.parent

# Clave secreta del proyecto.
# Debe definirse como variable de entorno en producción.
# Project secret key.
# Must be defined as an environment variable in production.
SECRET_KEY = os.environ.get(
    'SECRET_KEY',
    default='django-insecure-+p21kue6u#+c!lprrfofn91tmg!ge%tc!4cms9e%zm1m!jayc%'
)

# Activación del modo desarrollo.
# Debug mode activation.
DEBUG = True

# Hosts permitidos para servir la aplicación.
# Allowed hosts for serving the application.
ALLOWED_HOSTS = ['*']

# Configuración dinámica para despliegue en Render.
# Dynamic configuration for Render deployment.
RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)


# === INSTALLED APPS / APLICACIONES INSTALADAS ===
INSTALLED_APPS = [
    # Django core apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-party apps
    'rest_framework',
    'corsheaders',

    # Local apps
    'miapp',
]


# === MIDDLEWARE / MIDDLEWARE ===
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Static files in production
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',       # CORS handling
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


# === URL & WSGI CONFIGURATION / CONFIGURACIÓN URL & WSGI ===
ROOT_URLCONF = 'servidor_django.urls'
WSGI_APPLICATION = 'servidor_django.wsgi.application'


# === TEMPLATES / PLANTILLAS ===
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]


# === DATABASE CONFIGURATION / CONFIGURACIÓN DE BASE DE DATOS ===
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / "db.sqlite3",
    }
}


# === AUTHENTICATION / AUTENTICACIÓN ===
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# === INTERNATIONALIZATION / INTERNACIONALIZACIÓN ===
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True


# === MEDIA & STATIC FILES / ARCHIVOS MEDIA Y ESTÁTICOS ===
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

STATIC_URL = 'static/'

# Configuración específica para producción
# Production-specific configuration
if not DEBUG:
    # Directorio donde Django recopila los archivos estáticos
    # Directory where Django collects static files
    STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

    # WhiteNoise permite compresión y cacheo eficiente
    # WhiteNoise enables compression and efficient caching
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'


# === CORS CONFIGURATION / CONFIGURACIÓN CORS ===
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_HEADERS = list(default_headers) + [
    'content-type',
]


# === REST FRAMEWORK CONFIGURATION / CONFIGURACIÓN REST FRAMEWORK ===
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser',
    ],
}


# === DEFAULT FIELD TYPE / TIPO DE CAMPO POR DEFECTO ===
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# === STORAGE CONFIGURATION (LOCAL OR S3) / CONFIGURACIÓN DE ALMACENAMIENTO ===
USE_S3 = os.environ.get("USE_S3", "false").lower() in ("1", "true", "yes")

if USE_S3:
    # Almacenamiento en Amazon S3 usando django-storages
    # Amazon S3 storage using django-storages
    INSTALLED_APPS += ["storages"]

    DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"

    # Credenciales y configuración obtenidas desde variables de entorno
    # Credentials and configuration loaded from environment variables
    AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
    AWS_STORAGE_BUCKET_NAME = os.environ.get("AWS_STORAGE_BUCKET_NAME")
    AWS_S3_REGION_NAME = os.environ.get("AWS_S3_REGION_NAME", None)
    AWS_S3_CUSTOM_DOMAIN = os.environ.get("AWS_S3_CUSTOM_DOMAIN", None)

    AWS_DEFAULT_ACL = None
    AWS_S3_OBJECT_PARAMETERS = {
        'CacheControl': 'max-age=86400',
    }

    # URL pública de archivos multimedia
    # Public media files URL
    if AWS_S3_CUSTOM_DOMAIN:
        MEDIA_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/"
    else:
        MEDIA_URL = f"https://{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/"
else:
    # Almacenamiento local por defecto
    # Default local file system storage
    DEFAULT_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"
    MEDIA_URL = "/media/"
    MEDIA_ROOT = BASE_DIR / "media"


# === SECURITY SETTINGS / CONFIGURACIÓN DE SEGURIDAD ===
SECURE_SSL_REDIRECT = False
