from celery import shared_task
from django.conf import settings
from django.core.mail import EmailMessage
from django.utils import timezone
from apps.products.models import Product, LowStockAlert
from datetime import datetime, timedelta


@shared_task
def low_stock_notification():

    low_stock_products = Product.objects.filter(stock__lte=5)

    products_to_notify = []

    for product in low_stock_products:

        alert, created = LowStockAlert.objects.get_or_create(
            product=product,
            defaults={
                "status": LowStockAlert.Status.ACTIVE,
            },
        )

        if created:
            products_to_notify.append(product)

        elif alert.status == LowStockAlert.Status.RESOLVED:

            alert.status = LowStockAlert.Status.ACTIVE
            alert.notified_at = None

            alert.save(
                update_fields=[
                    "status",
                    "notified_at",
                ]
            )

            products_to_notify.append(product)

    # Resolve products that are no longer low-stock
    LowStockAlert.objects.filter(
        status=LowStockAlert.Status.ACTIVE,
        product__stock__gt=5,
    ).update(
        status=LowStockAlert.Status.RESOLVED,
    )

    # Nothing new to notify
    if not products_to_notify:
        print("No new low-stock products to notify.")
        return

    # --------------------------------------------------
    # Build email
    # --------------------------------------------------

    subject = "CommerceCore - Low Stock Alert"

    body = "The following products are low in stock:\n\n"

    for product in products_to_notify:
        body += (
            f"Product: {product.name}\n"
            f"Product ID: {product.id}\n"
            f"Current Stock: {product.stock}\n"
            f"--------------------------\n"
        )

    body += "\nPlease check the inventory."

    # --------------------------------------------------
    # Send email
    # --------------------------------------------------

    email = EmailMessage(
        subject=subject,
        body=body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[settings.LOW_STOCK_ALERT_RECIPIENT],
    )

    email.send()

    # --------------------------------------------------
    # Mark alerts as notified
    # --------------------------------------------------

    for product in products_to_notify:

        LowStockAlert.objects.filter(
            product=product,
            status=LowStockAlert.Status.ACTIVE,
        ).update(
            notified_at=timezone.now(),
        )

    print(
        f"Low-stock notification email sent for "
        f"{len(products_to_notify)} product(s)."
    )


@shared_task(bind=True, max_retries=3)
def retry_demo(self):
    print("Executing retry_demo")

    try:
        raise Exception("Demo failure")

    except Exception as exc:
        raise self.retry(exc=exc, countdown=5)



@shared_task
def countdown_demo():
    print("Countdown task executed!")    


@shared_task
def eta_demo():
    print("ETA task executed!")    