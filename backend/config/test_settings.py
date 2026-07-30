"""Settings used by the backend test suite."""

from .settings import *  # noqa: F403


SECRET_KEY = "test-only-secret-key-with-at-least-thirty-two-bytes"

DATABASES = {  # noqa: F405
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    },
}
