from celery import shared_task
from django.core.management import call_command


# @shared_task
# def hello_task():
#     print("Hello from Celery!")


@shared_task
def scheduled_hello_task():
    print("Celery Beat triggered the scheduled task!")


@shared_task
def daily_cleanup():
    print("Daily cleaup task started.")

    call_command("clearsessions")

    print("Expired Django sessions cleaned up.")
    print("Daily cleanup task completed.")