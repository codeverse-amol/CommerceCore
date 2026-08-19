from .base import *

DEBUG = True

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"


ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
]


EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
DEFAULT_FROM_EMAIL = "noreply@commercecore.local"


