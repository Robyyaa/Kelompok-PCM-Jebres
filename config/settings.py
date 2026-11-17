import os
import secrets
from pathlib import Path

import dj_database_url
from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


def env_bool(name, default=False):
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def env_list(name, default=""):
    return [item.strip() for item in os.getenv(name, default).split(",") if item.strip()]


DEBUG = env_bool("DEBUG", default=True)
SECRET_KEY = os.getenv("SECRET_KEY", "")
if not SECRET_KEY:
    if DEBUG:
        SECRET_KEY = secrets.token_urlsafe(50)
    else:
        raise RuntimeError("SECRET_KEY wajib diatur saat DEBUG=False.")

ALLOWED_HOSTS = env_list(
    "ALLOWED_HOSTS",
    "localhost,127.0.0.1,[::1]" if DEBUG else "",
)
RENDER_EXTERNAL_HOSTNAME = os.getenv("RENDER_EXTERNAL_HOSTNAME", "").strip()
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)
if not DEBUG and not ALLOWED_HOSTS:
    raise RuntimeError("ALLOWED_HOSTS wajib diatur saat DEBUG=False.")

CSRF_TRUSTED_ORIGINS = env_list("CSRF_TRUSTED_ORIGINS")
if RENDER_EXTERNAL_HOSTNAME:
    CSRF_TRUSTED_ORIGINS.append(f"https://{RENDER_EXTERNAL_HOSTNAME}")


INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "pcm.apps.PcmConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]
WHITENOISE_ENABLED = not DEBUG or env_bool("WHITENOISE_ENABLED")
if WHITENOISE_ENABLED:
    MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "pcm.context_processors.pcm_global",
                "pcm.context_processors.pcm_admin_dashboard",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

DATABASE_URL = os.getenv("DATABASE_URL", "").strip()
DATABASE_TRANSACTION_POOLING = env_bool("DATABASE_TRANSACTION_POOLING")
PCM_DB_HOST = os.getenv("PCM_DB_HOST", "").strip()
if DATABASE_URL:
    DATABASES = {
        "default": dj_database_url.parse(
            DATABASE_URL,
            conn_max_age=0 if DATABASE_TRANSACTION_POOLING else (0 if DEBUG else 600),
            conn_health_checks=not DEBUG and not DATABASE_TRANSACTION_POOLING,
            disable_server_side_cursors=DATABASE_TRANSACTION_POOLING,
            ssl_require=not DEBUG,
        )
    }
elif PCM_DB_HOST:
    PCM_DB_PASSWORD = os.getenv("PCM_DB_PASSWORD", "")
    if not PCM_DB_PASSWORD:
        raise RuntimeError("PCM_DB_PASSWORD wajib diatur untuk koneksi PostgreSQL Compose.")
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.getenv("PCM_DB_NAME", "pcm"),
            "USER": os.getenv("PCM_DB_USER", "pcm"),
            "PASSWORD": PCM_DB_PASSWORD,
            "HOST": PCM_DB_HOST,
            "PORT": os.getenv("PCM_DB_PORT", "5432"),
            "CONN_MAX_AGE": 0,
        }
    }
elif DEBUG:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }
else:
    raise RuntimeError("DATABASE_URL wajib diatur di lingkungan produksi.")

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "id"
TIME_ZONE = "Asia/Jakarta"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]
MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage"
    },
}

AWS_STORAGE_BUCKET_NAME = os.getenv("AWS_STORAGE_BUCKET_NAME", "").strip()
AWS_S3_ENDPOINT_URL = os.getenv("AWS_S3_ENDPOINT_URL", "").strip() or None
AWS_S3_REGION_NAME = os.getenv("AWS_S3_REGION_NAME", "").strip() or None
AWS_S3_CUSTOM_DOMAIN = os.getenv("AWS_S3_CUSTOM_DOMAIN", "").strip() or None
AWS_QUERYSTRING_AUTH = env_bool("AWS_QUERYSTRING_AUTH", default=False)
AWS_S3_FILE_OVERWRITE = False
AWS_DEFAULT_ACL = None
AWS_S3_SIGNATURE_VERSION = "s3v4"
if AWS_S3_ENDPOINT_URL:
    AWS_S3_ADDRESSING_STYLE = "path"

if AWS_STORAGE_BUCKET_NAME:
    STORAGES["default"] = {"BACKEND": "storages.backends.s3.S3Storage"}
elif not DEBUG:
    raise RuntimeError(
        "AWS_STORAGE_BUCKET_NAME wajib diatur di produksi agar file media tersimpan permanen."
    )

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31_536_000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = "DENY"
