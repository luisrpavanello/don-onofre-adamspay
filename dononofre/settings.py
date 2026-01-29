"""
Configuración de Django para el proyecto dononofre.

Generado por 'django-admin startproject' usando Django 6.0.1.

Para más información sobre este archivo, consulta:
https://docs.djangoproject.com/en/6.0/topics/settings/

Para la lista completa de configuraciones y sus valores, consulta:
https://docs.djangoproject.com/en/6.0/ref/settings/
"""
import os
import dj_database_url
from pathlib import Path

# Construye rutas dentro del proyecto así: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Configuraciones de inicio rápido para desarrollo - no adecuadas para producción
# Ver: https://docs.djangoproject.com/en/6.0/howto/deployment/checklist/

# ADVERTENCIA DE SEGURIDAD: ¡mantén secreta la clave secreta utilizada en producción!
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'clave-secreta-de-desarrollo')

# ADVERTENCIA DE SEGURIDAD:
DEBUG = os.getenv('DEBUG', 'False') == 'True'  

# Configuración de CORS
CORS_ALLOW_ALL_ORIGINS = True 

# Configuración de CSRF
CSRF_TRUSTED_ORIGINS = [
    'https://don-onofre-adamspay.onrender.com',
    'http://localhost:8000',
]

ALLOWED_HOSTS = ['don-onofre-adamspay.onrender.com', 'localhost', '127.0.0.1']

# Definición de aplicaciones
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'orders',
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

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

ROOT_URLCONF = 'dononofre.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'orders/templates'],
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

WSGI_APPLICATION = 'dononofre.wsgi.application'

# Configuración de la base de datos
print("=== CONFIGURACIÓN DE LA BASE DE DATOS ===")
print(f"Variable de entorno RENDER: {os.getenv('RENDER')}")
print(f"Variable de entorno DATABASE_URL: {os.getenv('DATABASE_URL')}")

# Usar PostgreSQL cuando DATABASE_URL esté definida
if os.getenv('DATABASE_URL'):
    print("=== USANDO POSTGRESQL (DATABASE_URL detectada) ===")
    DATABASES = {
        'default': dj_database_url.config(
            default=os.getenv('DATABASE_URL'),
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
    # Forzar motor PostgreSQL
    DATABASES['default']['ENGINE'] = 'django.db.backends.postgresql'
    print(f"Motor de base de datos: {DATABASES['default']['ENGINE']}")
    print(f"Host de base de datos: {DATABASES['default'].get('HOST', 'N/A')}")
else:
    # Localmente - usar SQLite
    print("=== USANDO SQLITE (entorno local) ===")
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Validación de contraseñas
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

# Internacionalización
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

# Logs en Render
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}

# Configuración de AdamsPay
ADAMSPAY_BASE_URL = os.getenv('ADAMSPAY_BASE_URL', 'https://app.adamspay.com')
ADAMSPAY_API_KEY = os.getenv('ADAMSPAY_API_KEY', '')
ADAMSPAY_CALLBACK_URL = os.getenv('ADAMSPAY_CALLBACK_URL', '')