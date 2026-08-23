from celery import shared_task
from django.core.management import call_command
from django.utils import timezone
from datetime import timedelta


from apps.carts.models import CartItem

# @shared_task
# def hello_task():
#     print("Hello from Celery!")


@shared_task
def scheduled_hello_task():
    print("Celery Beat triggered the scheduled task!")


@shared_task
def daily_cleanup():
    print("Daily cleaup task started.")

    # 1. Clean expired Django sessions
    call_command("clearsessions")
    print("Expired Django sessions cleaned up.")

    # 2. Delete cart items older than 30 days
    cutoff = timezone.now() - timedelta(days=30)

    deleted_count, _ = CartItem.objects.filter(added_at__lt=cutoff).delete()

    print(f"Expired cart items deleted: {deleted_count}")

    print("Daily cleanup task completed.")




@shared_task
def expired_cart_cleanup():
    print("Expired cart cleanup started.")

    expiration_date = timezone.now() - timedelta(days=30)

    expired_items = CartItem.objects.filter(added_at__lt=expiration_date)

    deleted_count = expired_items.count()

    expired_items.delete()

    print(f"Deleted {deleted_count} expired cart items.")
    print("Expired cart cleanup completed.")
