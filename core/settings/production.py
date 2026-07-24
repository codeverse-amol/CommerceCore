from .base import *

DEBUG = False


ALLOWED_HOSTS = [
    host.strip()
    for host in os.getenv("ALLOWED_HOSTS", "").split(",")
    if host.strip()
]


# --------------------------------------------------
# Production Settings
# --------------------------------------------------

# Secure cookies (enable after HTTPS is configured)
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# Prevent JavaScript from accessing cookies
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True

# Tell Django it is behind a reverse proxy (Nginx)
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")


# ==============================
# Amazon S3 Media Storage
# ==============================

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_STORAGE_BUCKET_NAME = os.getenv("AWS_STORAGE_BUCKET_NAME")
AWS_S3_REGION_NAME = os.getenv("AWS_S3_REGION_NAME")


AWS_S3_SIGNATURE_VERSION = "s3v4"

AWS_S3_FILE_OVERWRITE = False

AWS_DEFAULT_ACL = None

AWS_QUERYSTRING_AUTH = False


# | Setting                       | Purpose                                                                                                   |
# | ----------------------------- | --------------------------------------------------------------------------------------------------------- |
# | `AWS_S3_SIGNATURE_VERSION`    | Uses the current AWS request signing method (recommended).                                                |
# | `AWS_S3_FILE_OVERWRITE=False` | Prevents overwriting an existing file with the same name. Django will generate a unique filename instead. |
# | `AWS_DEFAULT_ACL=None`        | Recommended with **Bucket owner enforced** (ACLs disabled).                                               |
# | `AWS_QUERYSTRING_AUTH=False`  | Generates clean public URLs instead of temporary signed URLs. We'll discuss signed URLs later.            |


if AWS_STORAGE_BUCKET_NAME:

    AWS_S3_CUSTOM_DOMAIN = (
        f"{AWS_STORAGE_BUCKET_NAME}.s3.{AWS_S3_REGION_NAME}.amazonaws.com"
    )

    MEDIA_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/"

    STORAGES = {
        "default": {
            "BACKEND": "storages.backends.s3.S3Storage",
        },
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
        },
    }