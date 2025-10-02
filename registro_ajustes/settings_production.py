"""
=============================================================================
CONFIGURACIÓN DE DJANGO - SISTEMA DE REGISTRO DE AJUSTES
=============================================================================

Configuraciones para el proyecto Django del Sistema de Registro de Ajustes.
Optimizado para desarrollo y producción con variables de entorno.

Autor: Sistema de Desarrollo
Versión: 1.0.0
Fecha: Octubre 2025
=============================================================================
"""

from pathlib import Path
from decouple import config
from datetime import timedelta
import os
import dj_database_url

# =============================================================================
# CONFIGURACIÓN BASE
# =============================================================================

# Directorio base del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent

# Configuración de entorno
ENVIRONMENT = config('ENVIRONMENT', default='development')
DEBUG = config('DEBUG', default=True, cast=bool)
SECRET_KEY = config('SECRET_KEY', default='django-insecure-change-in-production')

# Hosts permitidos (configurado por entorno)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1').split(',')

# =============================================================================
# APLICACIONES DJANGO
# =============================================================================

# Aplicaciones del sistema Django
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

# Aplicaciones de terceros
THIRD_PARTY_APPS = [
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'django_filters',
]

# Aplicaciones locales del proyecto
LOCAL_APPS = [
    'authentication',
    'adjustments',
    'analytics',
]

# Lista completa de aplicaciones instaladas
INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# =============================================================================
# MIDDLEWARE
# =============================================================================

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# =============================================================================
# CONFIGURACIÓN DE URLs Y WSGI
# =============================================================================

ROOT_URLCONF = 'registro_ajustes.urls'
WSGI_APPLICATION = 'registro_ajustes.wsgi.application'

# =============================================================================
# PLANTILLAS
# =============================================================================

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

# =============================================================================
# CONFIGURACIÓN DE BASE DE DATOS
# =============================================================================

# Base de datos configurada por entorno
if config('DATABASE_URL', default=None):
    # Configuración con DATABASE_URL (recomendado para producción)
    DATABASES = {
        'default': dj_database_url.parse(
            config('DATABASE_URL'),
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
else:
    # Configuración SQLite para desarrollo
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# =============================================================================
# VALIDACIÓN DE CONTRASEÑAS
# =============================================================================

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# =============================================================================
# CONFIGURACIÓN REGIONAL
# =============================================================================

LANGUAGE_CODE = 'es-es'
TIME_ZONE = 'America/Bogota'
USE_I18N = True
USE_TZ = True

# =============================================================================
# ARCHIVOS ESTÁTICOS Y MEDIA
# =============================================================================

# Archivos estáticos (CSS, JavaScript, Images)
STATIC_URL = config('STATIC_URL', default='/static/')
STATIC_ROOT = config('STATIC_ROOT', default=BASE_DIR / 'staticfiles')

# Directorios adicionales para archivos estáticos
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# Archivos media (uploads de usuarios)
MEDIA_URL = config('MEDIA_URL', default='/media/')
MEDIA_ROOT = config('MEDIA_ROOT', default=BASE_DIR / 'media')

# =============================================================================
# CONFIGURACIÓN DE DJANGO REST FRAMEWORK
# =============================================================================

REST_FRAMEWORK = {
    # Autenticación por defecto
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    # Permisos por defecto
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    # Renderizadores
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    # Parsers
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser',
    ],
    # Paginación
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    # Filtros
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    # Throttling (limitación de requests)
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour'
    },
    # Formato de fecha y hora
    'DATETIME_FORMAT': '%Y-%m-%d %H:%M:%S',
    'DATE_FORMAT': '%Y-%m-%d',
}

# =============================================================================
# CONFIGURACIÓN JWT
# =============================================================================

SIMPLE_JWT = {
    # Tiempo de vida del token de acceso
    'ACCESS_TOKEN_LIFETIME': timedelta(
        minutes=config('ACCESS_TOKEN_LIFETIME', default=15, cast=int)
    ),
    # Tiempo de vida del token de refresco
    'REFRESH_TOKEN_LIFETIME': timedelta(
        days=config('REFRESH_TOKEN_LIFETIME', default=7, cast=int)
    ),
    # Rotar token de refresco
    'ROTATE_REFRESH_TOKENS': True,
    # Blacklist token después de rotación
    'BLACKLIST_AFTER_ROTATION': True,
    # Algoritmo de firma
    'ALGORITHM': config('JWT_ALGORITHM', default='HS256'),
    # Clave de firma
    'SIGNING_KEY': SECRET_KEY,
    # Verificar firma
    'VERIFYING_KEY': None,
    # Headers de autenticación
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    # Claim para el ID del usuario
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
}

# =============================================================================
# CONFIGURACIÓN CORS
# =============================================================================

# Orígenes permitidos para CORS
CORS_ALLOWED_ORIGINS = config(
    'CORS_ALLOWED_ORIGINS', 
    default='http://localhost:3000,http://localhost:5173'
).split(',')

# Permitir credenciales en requests CORS
CORS_ALLOW_CREDENTIALS = True

# Headers permitidos
CORS_ALLOW_ALL_HEADERS = True

# =============================================================================
# CONFIGURACIÓN DE EMAIL
# =============================================================================

EMAIL_BACKEND = config(
    'EMAIL_BACKEND', 
    default='django.core.mail.backends.console.EmailBackend'
)

if not DEBUG:
    # Configuración SMTP para producción
    EMAIL_HOST = config('EMAIL_HOST', default='localhost')
    EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
    EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
    EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
    EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')

DEFAULT_FROM_EMAIL = config(
    'DEFAULT_FROM_EMAIL', 
    default='Sistema de Ajustes <noreply@localhost>'
)

# =============================================================================
# CONFIGURACIÓN DE LOGGING
# =============================================================================

LOG_LEVEL = config('LOG_LEVEL', default='DEBUG' if DEBUG else 'INFO')

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{levelname}] {asctime} {name} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '[{levelname}] {asctime} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': config('LOG_FILE', default=BASE_DIR / 'django.log'),
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': LOG_LEVEL,
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': LOG_LEVEL,
            'propagate': False,
        },
        'adjustments': {
            'handlers': ['console', 'file'],
            'level': LOG_LEVEL,
            'propagate': False,
        },
        'authentication': {
            'handlers': ['console', 'file'],
            'level': LOG_LEVEL,
            'propagate': False,
        },
    },
}

# =============================================================================
# CONFIGURACIÓN DE SEGURIDAD
# =============================================================================

if not DEBUG:
    # Configuraciones de seguridad para producción
    
    # HTTPS
    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    
    # Cookies seguras
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    
    # Headers de seguridad
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
    
    # HSTS
    SECURE_HSTS_SECONDS = 31536000  # 1 año
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

# =============================================================================
# CONFIGURACIÓN DE CACHE
# =============================================================================

if config('REDIS_URL', default=None):
    # Cache con Redis para producción
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.redis.RedisCache',
            'LOCATION': config('REDIS_URL'),
            'TIMEOUT': config('CACHE_TIMEOUT', default=300, cast=int),
        }
    }
else:
    # Cache en memoria para desarrollo
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        }
    }

# =============================================================================
# CONFIGURACIONES ADICIONALES
# =============================================================================

# Clave primaria por defecto
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Configuración de admin
ADMIN_URL = config('ADMIN_URL', default='admin/')

# Configuración de sesiones
SESSION_COOKIE_AGE = 86400  # 24 horas
SESSION_SAVE_EVERY_REQUEST = True

# Configuración de archivos
FILE_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB

# =============================================================================
# CONFIGURACIONES ESPECÍFICAS DEL PROYECTO
# =============================================================================

# Configuraciones específicas para el sistema de ajustes
ADJUSTMENTS_SETTINGS = {
    'MAX_ADJUSTMENT_VALUE': config('MAX_ADJUSTMENT_VALUE', default=10000000, cast=int),
    'REQUIRE_APPROVAL_ABOVE': config('REQUIRE_APPROVAL_ABOVE', default=100000, cast=int),
    'AUTO_APPROVE_BELOW': config('AUTO_APPROVE_BELOW', default=10000, cast=int),
    'NOTIFICATION_EMAILS': config('NOTIFICATION_EMAILS', default='').split(','),
}

# =============================================================================
# MONITOREO Y ANALYTICS (OPCIONAL)
# =============================================================================

# Sentry para tracking de errores en producción
SENTRY_DSN = config('SENTRY_DSN', default=None)
if SENTRY_DSN and not DEBUG:
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration
    
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[DjangoIntegration()],
        traces_sample_rate=0.1,
        send_default_pii=True
    )