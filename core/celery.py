import os

from celery import Celery

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "core.settings.development"
)

app = Celery("core")

app.config_from_object(
    "django.conf:settings",
    namespace="CELERY"
)

app.autodiscover_tasks()




# Configure Celery Beat
from celery.schedules import crontab


app.conf.beat_schedule = {
    "run-scheduled-hello-every-minute": {
        "task": "apps.main.tasks.scheduled_hello_task",
        "schedule": 60.0
    },
}