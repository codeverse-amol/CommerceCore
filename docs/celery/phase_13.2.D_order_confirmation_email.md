# Phase 13.2.D — Order Confirmation Email

Asynchronous order confirmation emails triggered from the checkout flow, using Celery + Redis as the broker and Django's mail framework for delivery.

## Overview

When a customer places an order, the view creates the `Order` and `OrderItem` rows, adjusts stock, and clears the cart inside a single database transaction. Sending the confirmation email is delegated to a Celery task so the HTTP response doesn't block on SMTP/API latency.

```
Customer → Django View → DB Transaction (Order, Items, Stock, Cart)
                              │ commit
                              ▼
                        Celery (Redis broker)
                              │
                              ▼
                Worker: fetch Order → send_mail()
                              │
                              ▼
                        Customer inbox
```

## 1. The Task

Celery messages should carry the smallest payload possible — an ID, not a serialized object. The worker re-fetches the row itself at execution time.

```python
# apps/orders/tasks.py
import logging
from celery import shared_task
from django.core.mail import send_mail
from apps.orders.models import Order

logger = logging.getLogger(__name__)

@shared_task
def send_order_confirmation_email(order_id):
    order = Order.objects.select_related("user").get(id=order_id)

    subject = f"Order Confirmation - Order #{order.id}"
    message = f"""Hello {order.user.username},

Thank you for your order!

Order ID: #{order.id}
Order Status: {order.status}
Total Amount: ₹{order.total_amount}

Your order has been successfully placed.

Thank you for shopping with CommerceCore!
"""

    send_mail(
        subject=subject,
        message=message,
        from_email=None,          # falls back to DEFAULT_FROM_EMAIL
        recipient_list=[order.user.email],
    )
    logger.info("Order confirmation email sent for order #%s", order.id)
```

`@shared_task` is used instead of `@app.task` so the task isn't bound to one specific Celery app instance — the standard choice for tasks living inside a reusable Django app. `logging` is used instead of `print()`: worker output is normally captured by whatever sits around Celery in production (systemd, Docker log driver, Sentry), and `print()` bypasses log levels and formatting entirely.

## 2. Why Pass `order_id`, Not an `Order` Object

| | Payload sent through Redis | Coupling |
|---|---|---|
| ❌ Serialize the object | `Order`, `User`, `Address`, `OrderItem[]`, `Product[]` | Breaks if any related model's shape changes |
| ✅ Pass the ID | `order_id = 64` | Worker reads current data at execution time |

A single integer keeps the broker payload tiny and sidesteps serialization issues with model instances, `Decimal` fields, and FK relations.

## 3. Choosing the Right Email Backend

`EMAIL_BACKEND` should change per environment — the task code never needs to know which one is active.

| Backend | Setting | Use when |
|---|---|---|
| Console | `django.core.mail.backends.console.EmailBackend` | Local dev — prints the email to the terminal |
| File-based | `django.core.mail.backends.filebased.EmailBackend` | Local dev without a visible console, or inspecting output later |
| In-memory | `django.core.mail.backends.locmem.EmailBackend` | Automated tests (`django.core.mail.outbox`) |
| SMTP | `django.core.mail.backends.smtp.EmailBackend` | Staging/production with a mail server (Gmail SMTP, Postfix, etc.) |
| API-based (e.g. Anymail) | `anymail.backends.*` | Production — SES, SendGrid, Mailgun, Postmark. HTTP API instead of SMTP: faster, with delivery/bounce webhooks |

```python
# core/settings/development.py
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
DEFAULT_FROM_EMAIL = "noreply@commercecore.local"
```

Only this setting changes between environments — no task or view code changes.

## 4. Triggering the Task from the Checkout View

The task must fire only after the order is durably committed, never while the transaction is still open.

```python
# apps/orders/views.py
from django.db import transaction
from apps.orders.tasks import send_order_confirmation_email

@login_required
def placed_orders(request):
    ...
    with transaction.atomic():
        order = Order.objects.create(
            user=request.user,
            total_amount=subtotal,
            delivery_address=delivery_address,
        )
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price_at_purchase=item.product.price,
                total_price=item.total_price,
            )
            item.product.stock -= item.quantity
            item.product.save()

        cart_items.delete()

        transaction.on_commit(
            lambda: send_order_confirmation_email.delay(order.id)
        )

    return render(request, "orders/order_success.html", {"order": order})
```

### Trigger point comparison

| Approach | Risk |
|---|---|
| `.delay()` right after `Order.objects.create()`, no atomic block | Fine only if no other write needs to succeed atomically with the order |
| `.delay()` called inside `transaction.atomic()`, no `on_commit` | Race condition — the worker can start before the transaction commits, and `Order.objects.get()` raises `DoesNotExist` |
| `.delay()` wrapped in `transaction.on_commit()`, inside `transaction.atomic()` | Task enqueues only after a successful commit; a rolled-back transaction never queues an email |

## 5. Manual Testing

```bash
# terminal 1 — worker
celery -A core worker -l INFO --pool=solo   # --pool=solo required on Windows

# terminal 2 — shell
python manage.py shell
```

```python
from apps.orders.tasks import send_order_confirmation_email
from apps.orders.models import Order

Order.objects.values_list("id", "user__username", "status")
send_order_confirmation_email.delay(<real_order_id>)
```

> `--pool=solo` is a Windows-only requirement. Celery's default prefork pool relies on `os.fork()`, which Windows doesn't support.

## 6. Verified Output

```
Task apps.orders.tasks.send_order_confirmation_email[1b0342c5-...] received

Subject: Order Confirmation - Order #64
From: noreply@commercecore.local
To: celeryuser@test.com

    Hello celeryuser,
    Order ID: #64
    Order Status: PENDING
    Total Amount: ₹50000.00

Task ...[1b0342c5-...] succeeded in 0.0072s: None
```

End-to-end path confirmed: checkout → commit → Redis → worker → `Order.objects.get()` → `send_mail()`.

## 7. Production Hardening Checklist

- [ ] Replace any `print()` calls with `logging` inside tasks
- [ ] Add retries for transient failures — `@shared_task(bind=True, max_retries=3, default_retry_delay=30)` with `self.retry(exc=exc)`
- [ ] Route email tasks to a dedicated queue so a slow SMTP/API provider can't block other background jobs
- [ ] Only enable a result backend if something needs to check task status (`.get()`, `AsyncResult`) — a fire-and-forget email task doesn't need one
- [ ] Switch `EMAIL_BACKEND` to an SMTP/API backend outside local development
- [ ] Make the task idempotent — Celery's at-least-once delivery plus retries means it can run more than once for the same `order_id`

## Status

| Item | State |
|---|---|
| Celery task | ✅ |
| Redis broker | ✅ |
| Worker | ✅ |
| Console email backend | ✅ |
| Manual `.delay()` test | ✅ |
| `transaction.on_commit()` integration | ✅ |
| Real checkout end-to-end test | ✅ |