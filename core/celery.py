import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings.development")

app = Celery("core")

app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks()


# Configure Celery Beat
from celery.schedules import crontab

app.conf.beat_schedule = {
    "run-daily-session-cleanup": {
        "task": "apps.main.tasks.daily_session_cleanup",
        "schedule": crontab(hour=2, minute=0),
    },
    "run-expired-cart-cleanup": {
        "task": "apps.main.tasks.expired_cart_cleanup",
        "schedule": crontab(hour=2, minute=0),
    },
    "run-daily-reports": {
        "task": "apps.main.tasks.daily_reports",
        "schedule": crontab(hour=2, minute=0),
    },
    "run-low_stock-notification": {
        "task": "apps.products.tasks.low_stock_notification",
        "schedule": crontab(hour=8, minute=0),
    },
}
