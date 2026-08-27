from celery import shared_task
from django.core.management import call_command
from django.utils import timezone
from datetime import timedelta
from django.db.models import Sum, Count

from apps.carts.models import CartItem
from apps.orders.models import Order


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



@shared_task
def daily_reports():
    print("Daily report task started")

    today = timezone.localdate()

    # All orders created today
    todays_orders = Order.objects.filter(
        created_at__date=today,
    )

    # Total number of orders
    total_orders = todays_orders.count()

    # Cancelled orders
    cancelled_orders = todays_orders.filter(
        status="CANCELLED"
    ).count()

    # Pending orders
    pending_orders = todays_orders.filter(
        status="PENDING"
    ).count()

    # Delivered orders
    delivered_orders = todays_orders.filter(
        status="DELIVERED"
    ).count()

    # Sales = only delivered orders
    sales = todays_orders.filter(status="DELIVERED").aggregate(
        total=Sum("total_amount")
    )["total"] or 0

    # Status-wise order counts
    status_counts = todays_orders.values(
        "status"
    ).annotate(
        count=Count("id")
    )

    print("================================")
    print(f"Daily CommerceCore Report - {today}")
    print("================================")
    print(f"Total orders: {total_orders}")
    print(f"Cancelled orders: {cancelled_orders}")
    print(f"Pending orders: {pending_orders}")
    print(f"Delivered orders: {delivered_orders}")
    print(f"Today's sales: ₹{sales}")


    print("Order status:")
    for item in status_counts:
        print(
            f"{item['status']}: {item['count']}"
        )

    print("Daily report task completed.")
