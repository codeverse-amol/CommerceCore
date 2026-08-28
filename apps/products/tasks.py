from celery import shared_task
from django.conf import settings
from django.core.mail import EmailMessage

from apps.products.models import Product


LOW_STOCK_THRESHOLD = 5


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 5},
)
def low_stock_notification(self):
    print("Low stock notification task started.")

    low_stock_products = Product.objects.filter(
        stock__lte=LOW_STOCK_THRESHOLD
    ).order_by("stock", "name")

    if not low_stock_products.exists():
        print("No low-stock products available.")
        return

    subject = "CommerceCore - Low Stock Alert"

    body_lines = [
        "CommerceCore Low Stock Alert",
        "",
        f"The following products have stock at or below "
        f"{LOW_STOCK_THRESHOLD}:",
        "",
    ]

    for product in low_stock_products:
        body_lines.append(
            f"- {product.name} | Stock: {product.stock}"
        )

    body_lines.extend(
        [
            "",
            "Please review and replenish the inventory.",
            "",
            "CommerceCore",
        ]
    )

    email = EmailMessage(
        subject=subject,
        body="\n".join(body_lines),
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[settings.LOW_STOCK_NOTIFICATION_EMAIL],
    )

    email.send(fail_silently=False)

    print("Low stock notification email sent successfully.")