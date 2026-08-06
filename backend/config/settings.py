"""Django settings for the BrainOn REST API."""

import os
from datetime import timedelta
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR.parent / ".env")

SECRET_KEY = os.getenv(
    "DJANGO_SECRET_KEY",
    "unsafe-local-development-key",
)
DEBUG = os.getenv("DJANGO_DEBUG", "false").lower() == "true"
ALLOWED_HOSTS = [
    host.strip()
    for host in os.getenv(
        "DJANGO_ALLOWED_HOSTS",
        "localhost,127.0.0.1",
    ).split(",")
    if host.strip()
]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "corsheaders",
    "rest_framework",
    "rest_framework_simplejwt.token_blacklist",
    "apps.accounts.apps.AccountsConfig",
    "apps.hospitals.apps.HospitalsConfig",
    "apps.patients.apps.PatientsConfig",
    "apps.clinicians.apps.CliniciansConfig",
    "apps.appointments.apps.AppointmentsConfig",
    "apps.clinical_records.apps.ClinicalRecordsConfig",
    "apps.prescriptions.apps.PrescriptionsConfig",
    "apps.medications.apps.MedicationsConfig",
    "apps.assets.apps.AssetsConfig",
    "apps.diagnostics.apps.DiagnosticsConfig",
    "apps.imaging.apps.ImagingConfig",
    "apps.ct_analysis.apps.CtAnalysisConfig",
    "apps.test_results.apps.TestResultsConfig",
    "apps.consultations.apps.ConsultationsConfig",
    "apps.notifications.apps.NotificationsConfig",
    "apps.chatbot.apps.ChatbotConfig",
    "apps.audit_logs.apps.AuditLogsConfig",
    "apps.documentation.apps.DocumentationConfig",
    "apps.reports.apps.ReportsConfig",
    "apps.core.apps.CoreConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("POSTGRES_DB", "medical_cdss"),
        "USER": os.getenv("POSTGRES_USER", "cdssadmin"),
        "PASSWORD": os.getenv("POSTGRES_PASSWORD", ""),
        "HOST": os.getenv("POSTGRES_HOST", ""),
        "PORT": os.getenv("POSTGRES_PORT", "5432"),
        "CONN_MAX_AGE": int(
            os.getenv("POSTGRES_CONN_MAX_AGE", "0")
        ),
        "OPTIONS": {
            "sslmode": os.getenv(
                "POSTGRES_SSLMODE",
                "require",
            ),
        },
    },
}

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "UserAttributeSimilarityValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "MinimumLengthValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "CommonPasswordValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "NumericPasswordValidator"
        ),
    },
]

LANGUAGE_CODE = "ko-kr"
TIME_ZONE = "Asia/Seoul"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
AUTH_USER_MODEL = "accounts.User"

CORS_ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.getenv(
        "CORS_ALLOWED_ORIGINS",
        "http://localhost:5173",
    ).split(",")
    if origin.strip()
]
CORS_ALLOW_CREDENTIALS = True
CSRF_TRUSTED_ORIGINS = [
    origin.strip()
    for origin in os.getenv(
        "CSRF_TRUSTED_ORIGINS",
        "http://localhost:5173",
    ).split(",")
    if origin.strip()
]

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
    ],
    "DEFAULT_PAGINATION_CLASS": "apps.core.pagination.CommonPageNumberPagination",
    "EXCEPTION_HANDLER": "apps.core.exceptions.api_exception_handler",
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(
        minutes=int(os.getenv("JWT_ACCESS_MINUTES", "15"))
    ),
    "REFRESH_TOKEN_LIFETIME": timedelta(
        days=int(os.getenv("JWT_REFRESH_DAYS", "7"))
    ),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": False,
    "AUTH_HEADER_TYPES": ("Bearer",),
}

JWT_COOKIE_SECURE = os.getenv("JWT_COOKIE_SECURE", "false").lower() == "true"
JWT_COOKIE_SAMESITE = os.getenv("JWT_COOKIE_SAMESITE", "Lax")
JWT_REFRESH_COOKIE_NAME = os.getenv(
    "JWT_REFRESH_COOKIE_NAME",
    "brainon_refresh",
)

AI_SERVICE_URL = os.getenv(
    "AI_SERVICE_URL",
    "http://localhost:18200",
).rstrip("/")
AI_SERVICE_TIMEOUT_SECONDS = int(
    os.getenv("AI_SERVICE_TIMEOUT_SECONDS", "120")
)

FCM_ENABLED = os.getenv(
    "FCM_ENABLED",
    "false",
).lower() == "true"
FIREBASE_PROJECT_ID = os.getenv(
    "FIREBASE_PROJECT_ID",
    "",
).strip()
FIREBASE_CREDENTIALS_PATH = os.getenv(
    "FIREBASE_CREDENTIALS_PATH",
    "",
).strip()
FCM_HTTP_TIMEOUT_SECONDS = int(
    os.getenv("FCM_HTTP_TIMEOUT_SECONDS", "10")
)

# CT analysis / Cloud Run inference
CT_INPUT_BUCKET = os.getenv(
    "CT_INPUT_BUCKET",
    "brainon_ct-input_patient",
).strip()
CT_INPUT_PREFIX = os.getenv(
    "CT_INPUT_PREFIX",
    "uploads",
).strip().strip("/")
CT_DATASET_MANIFEST_URI = os.getenv(
    "CT_DATASET_MANIFEST_URI",
    (
        "gs://brainon_ct-input_patient/manifests/"
        "brainon_ct_verified_manifest_20260805.csv"
    ),
).strip()
CT_INFERENCE_GATEWAY_URL = os.getenv(
    "CT_INFERENCE_GATEWAY_URL",
    "http://localhost:8100",
).strip().rstrip("/")
CT_INFERENCE_GATEWAY_AUDIENCE = os.getenv(
    "CT_INFERENCE_GATEWAY_AUDIENCE",
    "",
).strip().rstrip("/")
CT_GATEWAY_USE_GCLOUD_AUTH = os.getenv(
    "CT_GATEWAY_USE_GCLOUD_AUTH",
    "false",
).lower() == "true"
CT_MODEL_VERSION = os.getenv(
    "CT_MODEL_VERSION",
    "1.0.0",
).strip()
CT_GATEWAY_TIMEOUT_SECONDS = int(
    os.getenv("CT_GATEWAY_TIMEOUT_SECONDS", "920")
)
CT_MAX_UPLOAD_BYTES = int(
    os.getenv("CT_MAX_UPLOAD_BYTES", str(512 * 1024 * 1024))
)
