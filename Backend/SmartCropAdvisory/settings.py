"""
Django settings for SmartCropAdvisory project.

🌾 AI-Powered Agricultural Intelligence System
🚀 MongoDB-only configuration with MongoEngine
📊 Production-ready configuration optimized for Render
"""

# Suppress specific warnings from dependencies
import warnings
import logging
import sys
import os

warnings.filterwarnings("ignore", category=UserWarning, module="pkg_resources")
warnings.filterwarnings(
    "ignore", category=UserWarning, module="rest_framework_simplejwt"
)
logger = logging.getLogger(__name__)

# Standard library imports
import json
from pathlib import Path
from decouple import config, Csv
from django.core.management.utils import get_random_secret_key
import mongoengine
from datetime import timedelta

# Build paths inside the project like this: BASE_DIR / 'subdir'
BASE_DIR = Path(__file__).resolve().parent.parent

# ==========================================
# 🚀 RENDER ENVIRONMENT DETECTION
# ==========================================
IS_RENDER = os.getenv("RENDER") == "true"
IS_PRODUCTION = IS_RENDER or os.getenv("DJANGO_ENV") == "production"

if IS_RENDER:
    print("🚀 Running on Render.com - Production optimizations enabled")

# ==========================================
# 🔐 Load Shared Config (with fallback)
# ==========================================
try:
    with open(os.path.join(BASE_DIR, "../shared-config.json")) as f:
        SHARED_CONFIG = json.load(f)
    SITE_NAME = SHARED_CONFIG["app"]["name"]
    API_VERSION = SHARED_CONFIG["development"]["api_version"]
except (FileNotFoundError, KeyError, json.JSONDecodeError):
    SITE_NAME = "SmartCropAdvisory"
    API_VERSION = "v1"

# ==========================================
# 🔐 SECURITY SETTINGS
# ==========================================

# Secret Key from .env file with fallback
SECRET_KEY = config(
    "DJANGO_SECRET_KEY",
    default=get_random_secret_key() if IS_RENDER else "dev-secret-key",
)

# Environment and Debug
DJANGO_ENV = config("DJANGO_ENV", default="production" if IS_RENDER else "development")
DEBUG = config("DEBUG", default=False if IS_PRODUCTION else True, cast=bool)
TESTING = "test" in sys.argv

# Allowed Hosts - Optimized for Render
ALLOWED_HOSTS = config(
    "ALLOWED_HOSTS",
    default="127.0.0.1,localhost,smartcropadvisory.onrender.com,.onrender.com,.railway.app,.herokuapp.com,.vercel.app",
    cast=Csv(),
)

# Force add Render domains if on Render
if IS_RENDER:
    ALLOWED_HOSTS.extend(["smartcropadvisory.onrender.com", ".onrender.com"])
    ALLOWED_HOSTS = list(set(ALLOWED_HOSTS))  # Remove duplicates

# Internal IPs for Debug Toolbar
INTERNAL_IPS = config("INTERNAL_IPS", default="127.0.0.1,localhost,::1", cast=Csv())

# Trusted Origins
CSRF_TRUSTED_ORIGINS = config(
    "CSRF_TRUSTED_ORIGINS",
    default="http://127.0.0.1:8000,http://localhost:8000,https://smartcropadvisory.onrender.com",
    cast=Csv(),
)

# Add Render domain to CSRF trusted origins
if IS_RENDER:
    CSRF_TRUSTED_ORIGINS.extend(["https://smartcropadvisory.onrender.com"])
    CSRF_TRUSTED_ORIGINS = list(set(CSRF_TRUSTED_ORIGINS))

# ==========================================
# 📱 APPLICATION DEFINITION
# ==========================================

DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    "django.contrib.humanize",
]

THIRD_PARTY_APPS = [
    # REST Framework
    "rest_framework",
    "rest_framework.authtoken",
    # CORS handling
    "corsheaders",
    # API documentation
    "drf_spectacular",
    # Filtering and searching
    "django_filters",
    # Health checks
    "health_check",
    "health_check.cache",
    "health_check.storage",
    # MongoDB support with MongoEngine
    "rest_framework_mongoengine",
    # Authentication & JWT
    "rest_framework_simplejwt",
    # Additional utilities
    "django_extensions",
    "robots",
]

# Only add Celery apps if not on Render (to reduce memory usage)
if not IS_RENDER:
    THIRD_PARTY_APPS.extend(
        [
            "django_celery_results",
            "django_celery_beat",
        ]
    )

# SmartCropAdvisory Apps
LOCAL_APPS = [
    "Apps.CropAnalysis",
    "Apps.WeatherIntegration",
    "Apps.IrrigationAdvisor",
    "Apps.MarketAnalysis",
    "Apps.UserManagement",
    "Apps.Advisory",
    "Apps.SystemStatus",
]

# Conditionally add debug toolbar (never on Render)
if DEBUG and not TESTING and not IS_RENDER:
    try:
        import debug_toolbar

        THIRD_PARTY_APPS += ["debug_toolbar"]
    except ImportError:
        pass

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# ==========================================
# 🔧 MIDDLEWARE CONFIGURATION
# ==========================================

MIDDLEWARE = [
    # Security middleware
    "django.middleware.security.SecurityMiddleware",
    # Static files serving (Whitenoise)
    "whitenoise.middleware.WhiteNoiseMiddleware",
    # CORS (should be early)
    "corsheaders.middleware.CorsMiddleware",
]

# Try to add API Cache Control middleware
try:
    if not IS_RENDER:  # Skip on Render to reduce overhead
        MIDDLEWARE.append("Apps.Middleware.api_cache_control.APINoCacheMiddleware")
except:
    pass

# Add debug toolbar middleware if available
if DEBUG and not TESTING and not IS_RENDER and "debug_toolbar" in INSTALLED_APPS:
    MIDDLEWARE += ["debug_toolbar.middleware.DebugToolbarMiddleware"]

# Core Django middleware
MIDDLEWARE += [
    # Session handling
    "django.contrib.sessions.middleware.SessionMiddleware",
    # Common functionality
    "django.middleware.common.CommonMiddleware",
    # CSRF protection
    "django.middleware.csrf.CsrfViewMiddleware",
    # Authentication
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    # Messages framework
    "django.contrib.messages.middleware.MessageMiddleware",
    # Clickjacking protection
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# ==========================================
# 🌐 CORS SETTINGS
# ==========================================

CORS_ALLOW_ALL_ORIGINS = config(
    "CORS_ALLOW_ALL_ORIGINS", default=DEBUG and not IS_RENDER, cast=bool
)

if not CORS_ALLOW_ALL_ORIGINS:
    CORS_ALLOWED_ORIGINS = config(
        "CORS_ALLOWED_ORIGINS",
        default="http://localhost:3000,https://localhost:3000,http://127.0.0.1:3000",
        cast=Csv(),
    )

CORS_ALLOW_CREDENTIALS = config("CORS_ALLOW_CREDENTIALS", default=True, cast=bool)
CORS_ALLOW_HEADERS = [
    "accept",
    "accept-encoding",
    "authorization",
    "content-type",
    "dnt",
    "origin",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
    "x-api-key",
    "cache-control",
    "pragma",
    "if-modified-since",
]

CORS_EXPOSE_HEADERS = [
    "content-type",
    "x-api-version",
    "x-request-id",
    "x-ratelimit-remaining",
    "x-ratelimit-limit",
]

# ==========================================
# 🔗 URL AND TEMPLATE CONFIGURATION
# ==========================================

ROOT_URLCONF = "SmartCropAdvisory.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "Templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "django.template.context_processors.tz",
            ],
        },
    },
]

WSGI_APPLICATION = "SmartCropAdvisory.wsgi.application"

# ==========================================
# 💾 DATABASE CONFIGURATION
# ==========================================

# Dummy SQLite database for Django's required tables
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "django_internal.sqlite3",
    }
}

# Add connection optimization for production
if IS_PRODUCTION:
    DATABASES["default"]["CONN_MAX_AGE"] = 600
    DATABASES["default"]["CONN_HEALTH_CHECKS"] = True

# MongoDB Configuration - Optimized for Render
if IS_RENDER:
    # Minimal connections for Render free tier
    MONGODB_SETTINGS = {
        "db": config("MONGODB_DATABASE", default="smartcrop_db"),
        "host": config("MONGODB_HOST", default="localhost"),
        "port": config("MONGODB_PORT", default=27017, cast=int),
        "username": config("MONGODB_USERNAME", default=""),
        "password": config("MONGODB_PASSWORD", default=""),
        "authentication_source": config("MONGODB_AUTH_SOURCE", default="admin"),
        "authentication_mechanism": config(
            "MONGODB_AUTH_MECHANISM", default="SCRAM-SHA-1"
        ),
        "connect": False,  # Lazy connection
        "tz_aware": True,
        "uuidRepresentation": "standard",
        # Reduced pool for Render
        "maxPoolSize": 1,
        "minPoolSize": 1,
        "maxIdleTimeMS": 60000,
        "serverSelectionTimeoutMS": 45000,
        "connectTimeoutMS": 45000,
        "socketTimeoutMS": 45000,
        "heartbeatFrequencyMS": 30000,
    }
else:
    # Development settings with more connections
    MONGODB_SETTINGS = {
        "db": config("MONGODB_DATABASE", default="smartcrop_db"),
        "host": config("MONGODB_HOST", default="localhost"),
        "port": config("MONGODB_PORT", default=27017, cast=int),
        "username": config("MONGODB_USERNAME", default=""),
        "password": config("MONGODB_PASSWORD", default=""),
        "authentication_source": config("MONGODB_AUTH_SOURCE", default="admin"),
        "authentication_mechanism": config(
            "MONGODB_AUTH_MECHANISM", default="SCRAM-SHA-1"
        ),
        "connect": False,
        "tz_aware": True,
        "uuidRepresentation": "standard",
        "maxPoolSize": config("MONGODB_MAX_POOL_SIZE", default=100, cast=int),
        "minPoolSize": config("MONGODB_MIN_POOL_SIZE", default=5, cast=int),
        "maxIdleTimeMS": config("MONGODB_MAX_IDLE_TIME", default=30000, cast=int),
        "serverSelectionTimeoutMS": config(
            "MONGODB_SERVER_TIMEOUT", default=10000, cast=int
        ),
        "connectTimeoutMS": config("MONGODB_CONNECT_TIMEOUT", default=20000, cast=int),
        "socketTimeoutMS": config("MONGODB_SOCKET_TIMEOUT", default=0, cast=int),
        "heartbeatFrequencyMS": config(
            "MONGODB_HEARTBEAT_FREQ", default=10000, cast=int
        ),
    }

# MongoDB URI Connection String Support
MONGODB_URI = config("MONGODB_URI", default="")
if MONGODB_URI:
    mongoengine.connect(host=MONGODB_URI, connect=False, tz_aware=True)
else:
    if MONGODB_SETTINGS["username"] and MONGODB_SETTINGS["password"]:
        mongoengine.connect(**MONGODB_SETTINGS)
    else:
        mongoengine.connect(
            db=MONGODB_SETTINGS["db"],
            host=MONGODB_SETTINGS["host"],
            port=MONGODB_SETTINGS["port"],
            connect=False,
            tz_aware=True,
        )

# ==========================================
# 🔒 AUTHENTICATION & PASSWORD VALIDATION
# ==========================================

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {"min_length": config("PASSWORD_MIN_LENGTH", default=8, cast=int)},
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Authentication backends
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
]

# Session configuration
SESSION_ENGINE = (
    "django.contrib.sessions.backends.cache"
    if not IS_RENDER
    else "django.contrib.sessions.backends.db"
)
SESSION_CACHE_ALIAS = "default"
SESSION_COOKIE_AGE = config("SESSION_COOKIE_AGE", default=86400, cast=int)  # 24 hours
SESSION_COOKIE_SECURE = config(
    "SESSION_COOKIE_SECURE", default=IS_PRODUCTION, cast=bool
)
SESSION_COOKIE_HTTPONLY = config("SESSION_COOKIE_HTTPONLY", default=True, cast=bool)
SESSION_COOKIE_SAMESITE = config("SESSION_COOKIE_SAMESITE", default="Lax")

# ==========================================
# 🌍 INTERNATIONALIZATION
# ==========================================

LANGUAGE_CODE = config("LANGUAGE_CODE", default="en-us")
TIME_ZONE = config("TIME_ZONE", default="Asia/Kolkata")
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Supported languages for multi-language support
LANGUAGES = [
    ("en", "English"),
    ("hi", "Hindi (हिन्दी)"),
    ("bn", "Bengali (বাংলা)"),
    ("ta", "Tamil (தமிழ்)"),
    ("te", "Telugu (తెలుగు)"),
    ("mr", "Marathi (मराठी)"),
    ("gu", "Gujarati (ગુજરાતી)"),
    ("pa", "Punjabi (ਪੰਜਾਬੀ)"),
]

LOCALE_PATHS = [BASE_DIR / "locale"]

# ==========================================
# 📁 STATIC & MEDIA FILES
# ==========================================

# Static files configuration
STATIC_URL = config("STATIC_URL", default="/static/")
STATIC_ROOT = BASE_DIR / config("STATIC_ROOT", default="staticfiles")
STATICFILES_DIRS = [BASE_DIR / config("STATICFILES_DIR", default="Static")]

# Whitenoise configuration for static files
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
WHITENOISE_USE_FINDERS = True
WHITENOISE_AUTOREFRESH = DEBUG

# Additional static files finders
STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]

# Media files configuration
MEDIA_URL = config("MEDIA_URL", default="/media/")
MEDIA_ROOT = BASE_DIR / config("MEDIA_ROOT", default="Media")

# File upload settings - Optimized for Render
if IS_RENDER:
    # Reduced for Render's memory constraints
    FILE_UPLOAD_MAX_MEMORY_SIZE = 5 * 1024 * 1024  # 5MB
    DATA_UPLOAD_MAX_MEMORY_SIZE = 5 * 1024 * 1024  # 5MB
    DATA_UPLOAD_MAX_NUMBER_FIELDS = 1000
else:
    FILE_UPLOAD_MAX_MEMORY_SIZE = config(
        "FILE_UPLOAD_MAX_MEMORY_SIZE", default=50 * 1024 * 1024, cast=int
    )
    DATA_UPLOAD_MAX_MEMORY_SIZE = config(
        "DATA_UPLOAD_MAX_MEMORY_SIZE", default=50 * 1024 * 1024, cast=int
    )
    DATA_UPLOAD_MAX_NUMBER_FIELDS = config(
        "DATA_UPLOAD_MAX_NUMBER_FIELDS", default=5000, cast=int
    )

# Image processing settings
IMAGE_UPLOAD_EXTENSIONS = config(
    "IMAGE_UPLOAD_EXTENSIONS", default="jpg,jpeg,png,webp,bmp", cast=Csv()
)
MAX_IMAGE_SIZE = config("MAX_IMAGE_SIZE", default=10 * 1024 * 1024, cast=int)  # 10MB

# ==========================================
# 🔥 REDIS & CACHING CONFIGURATION
# ==========================================

REDIS_URL = config("REDIS_URL", default="redis://localhost:6379/0")
REDIS_HOST = config("REDIS_HOST", default="localhost")
REDIS_PORT = config("REDIS_PORT", default=6379, cast=int)
REDIS_DB = config("REDIS_DB", default=0, cast=int)
REDIS_PASSWORD = config("REDIS_PASSWORD", default=None)

# Force local memory cache on Render to avoid Redis issues
if IS_RENDER:
    REDIS_AVAILABLE = False
    print("🔧 Using local memory cache for Render deployment")

    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "smartcrop-cache-default",
            "TIMEOUT": 3600,
            "OPTIONS": {
                "MAX_ENTRIES": 1000,  # Reduced for memory
                "CULL_FREQUENCY": 3,
            },
        },
        "tokens": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "smartcrop-cache-tokens",
            "TIMEOUT": 604800,  # 7 days
            "OPTIONS": {
                "MAX_ENTRIES": 500,  # Reduced for memory
                "CULL_FREQUENCY": 4,
            },
        },
        "rate_limit": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "smartcrop-cache-ratelimit",
            "TIMEOUT": 3600,
            "OPTIONS": {
                "MAX_ENTRIES": 100,  # Reduced for memory
                "CULL_FREQUENCY": 5,
            },
        },
    }

    # Use database sessions on Render
    SESSION_ENGINE = "django.contrib.sessions.backends.db"
else:
    # Development/Non-Render cache configuration
    try:
        import redis

        # Test Redis connection
        redis_client = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            db=REDIS_DB,
            password=REDIS_PASSWORD,
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5,
            retry_on_timeout=True,
        )
        redis_client.ping()
        REDIS_AVAILABLE = True

        print(f"✅ Redis connected successfully at {REDIS_HOST}:{REDIS_PORT}")

        CACHES = {
            "default": {
                "BACKEND": "django_redis.cache.RedisCache",
                "LOCATION": REDIS_URL,
                "OPTIONS": {
                    "CLIENT_CLASS": "django_redis.client.DefaultClient",
                    "CONNECTION_POOL_KWARGS": {
                        "max_connections": 100,
                        "retry_on_timeout": True,
                        "socket_connect_timeout": 5,
                        "socket_timeout": 5,
                    },
                    "SERIALIZER": "django_redis.serializers.pickle.PickleSerializer",
                    "COMPRESSOR": "django_redis.compressors.zlib.ZlibCompressor",
                    "IGNORE_EXCEPTIONS": True,
                },
                "KEY_PREFIX": "smartcrop",
                "TIMEOUT": 3600,
            },
            "tokens": {
                "BACKEND": "django_redis.cache.RedisCache",
                "LOCATION": f"redis://{REDIS_HOST}:{REDIS_PORT}/2",
                "OPTIONS": {
                    "CLIENT_CLASS": "django_redis.client.DefaultClient",
                    "CONNECTION_POOL_KWARGS": {
                        "max_connections": 50,
                        "retry_on_timeout": True,
                    },
                    "IGNORE_EXCEPTIONS": False,
                },
                "KEY_PREFIX": "auth_token",
                "TIMEOUT": 604800,
            },
            "rate_limit": {
                "BACKEND": "django_redis.cache.RedisCache",
                "LOCATION": f"redis://{REDIS_HOST}:{REDIS_PORT}/4",
                "OPTIONS": {
                    "CLIENT_CLASS": "django_redis.client.DefaultClient",
                    "CONNECTION_POOL_KWARGS": {
                        "max_connections": 20,
                        "retry_on_timeout": True,
                    },
                    "IGNORE_EXCEPTIONS": True,
                },
                "KEY_PREFIX": "rate_limit",
                "TIMEOUT": 3600,
            },
        }

        SESSION_ENGINE = "django.contrib.sessions.backends.cache"
        SESSION_CACHE_ALIAS = "default"

    except (ImportError, Exception) as e:
        REDIS_AVAILABLE = False
        print(f"⚠️ Redis not available, falling back to local memory cache: {e}")

        CACHES = {
            "default": {
                "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
                "LOCATION": "smartcrop-cache-default",
                "TIMEOUT": 3600,
                "OPTIONS": {
                    "MAX_ENTRIES": 10000,
                    "CULL_FREQUENCY": 3,
                },
            },
            "tokens": {
                "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
                "LOCATION": "smartcrop-cache-tokens",
                "TIMEOUT": 604800,
                "OPTIONS": {
                    "MAX_ENTRIES": 5000,
                    "CULL_FREQUENCY": 4,
                },
            },
            "rate_limit": {
                "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
                "LOCATION": "smartcrop-cache-ratelimit",
                "TIMEOUT": 3600,
                "OPTIONS": {
                    "MAX_ENTRIES": 1000,
                    "CULL_FREQUENCY": 5,
                },
            },
        }

        SESSION_ENGINE = "django.contrib.sessions.backends.db"

# Redis status for app usage
REDIS_STATUS = {
    "available": REDIS_AVAILABLE if "REDIS_AVAILABLE" in locals() else False,
    "host": REDIS_HOST,
    "port": REDIS_PORT,
}

# ==========================================
# 🚀 REST FRAMEWORK CONFIGURATION
# ==========================================

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "Apps.UserManagement.authentication.MongoTokenAuthentication",
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "rest_framework.authentication.TokenAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": config("API_PAGE_SIZE", default=20 if IS_RENDER else 50, cast=int),
    "MAX_PAGE_SIZE": config(
        "API_MAX_PAGE_SIZE", default=100 if IS_RENDER else 1000, cast=int
    ),
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ],
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
    ]
    + (
        ["rest_framework.renderers.BrowsableAPIRenderer"]
        if DEBUG and not IS_RENDER
        else []
    ),
    "DEFAULT_PARSER_CLASSES": [
        "rest_framework.parsers.JSONParser",
        "rest_framework.parsers.MultiPartParser",
        "rest_framework.parsers.FormParser",
    ],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_VERSIONING_CLASS": "rest_framework.versioning.URLPathVersioning",
    "DEFAULT_VERSION": "v1",
    "ALLOWED_VERSIONS": ["v1", "v2"],
    # Rate limiting - Reduced for Render
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
        "rest_framework.throttling.ScopedRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": config("API_ANON_RATE", default="50/hour" if IS_RENDER else "100/hour"),
        "user": config(
            "API_USER_RATE", default="500/hour" if IS_RENDER else "1000/hour"
        ),
        "ml_predictions": config(
            "API_ML_RATE", default="25/hour" if IS_RENDER else "50/hour"
        ),
        "file_upload": config(
            "API_UPLOAD_RATE", default="10/hour" if IS_RENDER else "20/hour"
        ),
    },
    # Response formatting
    "DATETIME_FORMAT": "%Y-%m-%dT%H:%M:%S.%fZ",
    "DATE_FORMAT": "%Y-%m-%d",
    "TIME_FORMAT": "%H:%M:%S",
    # Exception handling
    "EXCEPTION_HANDLER": "rest_framework.views.exception_handler",
    # Metadata
    "DEFAULT_METADATA_CLASS": "rest_framework.metadata.SimpleMetadata",
}

# ==========================================
# 🔐 JWT AUTHENTICATION SETTINGS
# ==========================================

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(
        minutes=config("JWT_ACCESS_TOKEN_LIFETIME", default=60, cast=int)
    ),
    "REFRESH_TOKEN_LIFETIME": timedelta(
        days=config("JWT_REFRESH_TOKEN_LIFETIME", default=7, cast=int)
    ),
    "ROTATE_REFRESH_TOKENS": config(
        "JWT_ROTATE_REFRESH_TOKENS", default=True, cast=bool
    ),
    "BLACKLIST_AFTER_ROTATION": config(
        "JWT_BLACKLIST_AFTER_ROTATION", default=True, cast=bool
    ),
    "ALGORITHM": config("JWT_ALGORITHM", default="HS256"),
    "SIGNING_KEY": SECRET_KEY,
    "VERIFYING_KEY": None,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION",
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
    "TOKEN_TYPE_CLAIM": "token_type",
    "JTI_CLAIM": "jti",
}

# ==========================================
# 📊 DRF SPECTACULAR SETTINGS (API DOCS)
# ==========================================


# Simplified preprocessing hook for production
def spectacular_preprocessing_hook(endpoints):
    return endpoints


def spectacular_postprocessing_hook(result, generator, request, public):
    return result


SPECTACULAR_SETTINGS = {
    "TITLE": "SmartCropAdvisory API",
    "DESCRIPTION": "AI-Powered Agricultural Intelligence System API",
    "VERSION": "2.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "COMPONENT_SPLIT_REQUEST": False,
    "COMPONENT_SPLIT_PATCH": False,
    "COMPONENT_NO_READ_ONLY_REQUIRED": True,
    "SCHEMA_PATH_PREFIX": "/api/v1/",
    "SCHEMA_PATH_PREFIX_TRIM": True,
    "PREPROCESSING_HOOKS": [
        "SmartCropAdvisory.settings.spectacular_preprocessing_hook"
    ],
    "POSTPROCESSING_HOOKS": [
        "SmartCropAdvisory.settings.spectacular_postprocessing_hook"
    ],
    "DISABLE_ERRORS_AND_WARNINGS": True,
}

# ==========================================
# 🧠 MACHINE LEARNING CONFIGURATION
# ==========================================

# Model paths
ML_MODELS_DIR = BASE_DIR / config("ML_MODELS_DIR", default="Scripts/Models")
ML_MODELS_DIR.mkdir(exist_ok=True, parents=True)

# ML Settings - Optimized for Render
ML_SETTINGS = {
    "image_size": (224, 224),
    "batch_size": config("ML_BATCH_SIZE", default=16 if IS_RENDER else 32, cast=int),
    "confidence_threshold": 0.7,
    "max_image_size": 10 * 1024 * 1024,
    "allowed_image_formats": ["JPEG", "PNG", "JPG", "WEBP"],
    "preprocessing_threads": 1 if IS_RENDER else 2,
    "prediction_timeout": 30,
    "model_cache_timeout": 3600,
}

# GPU Settings
USE_GPU = config("USE_GPU", default=False, cast=bool) and not IS_RENDER
GPU_MEMORY_LIMIT = config("GPU_MEMORY_LIMIT", default=1024, cast=int)

# ==========================================
# 📧 EMAIL CONFIGURATION
# ==========================================

if IS_RENDER:
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
else:
    EMAIL_BACKEND = config(
        "EMAIL_BACKEND",
        default=(
            "django.core.mail.backends.smtp.EmailBackend"
            if not DEBUG
            else "django.core.mail.backends.console.EmailBackend"
        ),
    )

EMAIL_HOST = config("EMAIL_HOST", default="smtp.gmail.com")
EMAIL_PORT = config("EMAIL_PORT", default=587, cast=int)
EMAIL_USE_TLS = config("EMAIL_USE_TLS", default=True, cast=bool)
EMAIL_HOST_USER = config("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD", default="")
DEFAULT_FROM_EMAIL = config(
    "DEFAULT_FROM_EMAIL", default="noreply@smartcropadvisory.com"
)

# ==========================================
# 🔧 CELERY CONFIGURATION (Disabled on Render)
# ==========================================

if not IS_RENDER:
    CELERY_BROKER_URL = config("CELERY_BROKER_URL", default=REDIS_URL)
    CELERY_RESULT_BACKEND = config("CELERY_RESULT_BACKEND", default=REDIS_URL)
    CELERY_TASK_ALWAYS_EAGER = True if DEBUG else False
else:
    # Disable Celery on Render
    CELERY_TASK_ALWAYS_EAGER = True
    CELERY_TASK_EAGER_PROPAGATES = True

# ==========================================
# 📝 LOGGING CONFIGURATION - Simplified for Render
# ==========================================

# Create logs directory
LOGS_DIR = BASE_DIR / config("LOGS_DIR", default="Logs")
LOGS_DIR.mkdir(exist_ok=True)

# Simplified logging for Render
if IS_RENDER:
    LOGGING = {
        "version": 1,
        "disable_existing_loggers": False,
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
            },
        },
        "root": {
            "handlers": ["console"],
            "level": "WARNING",  # Only warnings and errors on Render
        },
        "loggers": {
            "django": {
                "handlers": ["console"],
                "level": "WARNING",
                "propagate": False,
            },
        },
    }
else:
    # Full logging for development
    LOGGING = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "verbose": {
                "format": "{levelname} {asctime} [{module}:{funcName}:{lineno}] {message}",
                "style": "{",
            },
            "simple": {
                "format": "{levelname} {asctime} {message}",
                "style": "{",
            },
        },
        "handlers": {
            "console": {
                "level": "DEBUG" if DEBUG else "INFO",
                "class": "logging.StreamHandler",
                "formatter": "simple",
            },
            "file": {
                "level": "INFO",
                "class": "logging.handlers.RotatingFileHandler",
                "filename": LOGS_DIR / "django.log",
                "maxBytes": 10 * 1024 * 1024,
                "backupCount": 5,
                "formatter": "verbose",
            },
        },
        "loggers": {
            "django": {
                "handlers": ["console", "file"],
                "level": "INFO",
                "propagate": False,
            },
            "Apps": {
                "handlers": ["console", "file"],
                "level": "DEBUG" if DEBUG else "INFO",
                "propagate": False,
            },
        },
    }

# ==========================================
# 🏥 HEALTH CHECK CONFIGURATION
# ==========================================

HEALTH_CHECK = {
    "DISK_USAGE_MAX": 90,  # %
    "MEMORY_MIN": 100,  # MB
    "CACHE_TIMEOUT": 30,  # seconds
}

# ==========================================
# 🌾 AGRICULTURAL SETTINGS
# ==========================================

AGRICULTURAL_SETTINGS = {
    "supported_crops": [
        "wheat",
        "rice",
        "corn",
        "soybean",
        "cotton",
        "sugarcane",
        "potato",
    ],
    "supported_diseases": ["bacterial_blight", "brown_spot", "leaf_blast", "rust"],
    "crop_seasons": {
        "kharif": ["june", "july", "august", "september", "october"],
        "rabi": ["november", "december", "january", "february", "march"],
        "zaid": ["april", "may", "june"],
    },
}

# ==========================================
# 🚫 SECURITY SETTINGS
# ==========================================

# Security headers
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = "DENY"
SECURE_REFERRER_POLICY = "same-origin"

# HTTPS settings - Enable on Render
if IS_PRODUCTION:
    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

# ==========================================
# 🎯 MISCELLANEOUS SETTINGS
# ==========================================

# Site configuration
SITE_ID = 1
SITE_NAME = "SmartCropAdvisory"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Data retention (reduced for Render)
if IS_RENDER:
    DATA_RETENTION = {
        "weather_data_days": 30,  # 1 month
        "ml_predictions_days": 7,  # 1 week
        "user_activity_days": 30,  # 1 month
        "error_logs_days": 7,  # 1 week
    }
else:
    DATA_RETENTION = {
        "weather_data_days": 365,
        "ml_predictions_days": 90,
        "user_activity_days": 180,
        "error_logs_days": 30,
    }

# ==========================================
# 🎉 STARTUP SUMMARY
# ==========================================

print(f"🌾 SmartCropAdvisory loaded - {DJANGO_ENV.title()} mode")
if IS_RENDER:
    print(
        "📊 Render optimizations active: Reduced memory usage, local cache, minimal connections"
    )
