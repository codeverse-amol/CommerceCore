# Phase 13.2.E — Configuring SMTP for Transactional Email

How to move an application's outgoing email from a local/dev backend to a real mail server, and have it actually land in a customer's inbox. CommerceCore (Django) is used as the worked example, but the pattern — credentials in environment variables, one settings block, a real send test, and a recipient pulled from user data — applies to any backend framework.

## Prerequisites

- An SMTP-capable mail account or provider (a Gmail account, a Google Workspace account, or a transactional provider such as Amazon SES / SendGrid / Mailgun / Postmark)
- If using Gmail: **2-Step Verification enabled** on the Google Account, so an **App Password** can be generated — Gmail's SMTP server rejects the regular account password once 2-Step Verification is on
- A way to load environment variables into settings at startup (CommerceCore uses `python-dotenv` + `os.getenv()`; any `.env`-style loader or the framework's native config system works the same way)
- `.env` excluded from version control, with a `.env.example` template committed in its place
- Outbound network access on the SMTP port being used (587 or 465) — some hosting platforms and corporate networks block these by default

## 1. Choosing the Right SMTP Provider

| Provider | Host example | Auth | Best for |
|---|---|---|---|
| Gmail (personal) | `smtp.gmail.com` | App Password | Local dev, demos, personal projects. ~500 emails/day |
| Google Workspace | `smtp.gmail.com` | App Password or OAuth2 | Small teams already on Workspace. ~2000 emails/day |
| Amazon SES | `email-smtp.<region>.amazonaws.com` | SMTP credentials from the SES console | Production at scale, low cost, needs "production access" requested to leave sandbox mode |
| SendGrid / Mailgun / Postmark | `smtp.<provider>.com` | API key as the password | Production transactional email — bounce/complaint webhooks, deliverability dashboards |
| Self-hosted / corporate relay | internal hostname | varies | Full control, but reputation, DNS, and uptime become your responsibility |

For a real product, a transactional provider (SES/SendGrid/Mailgun/Postmark) is the right long-term choice — Gmail is fine for proving the pipeline works, but it isn't built for application traffic and can flag or suspend an account that sends automated mail at volume.

## 2. Common Ports and Encryption

| Port | Encryption | Setting |
|---|---|---|
| 587 | STARTTLS (connect plain, then upgrade) | `EMAIL_USE_TLS = True` |
| 465 | Implicit SSL/TLS | `EMAIL_USE_SSL = True` |
| 25 | Unencrypted | Avoid — frequently blocked by ISPs and cloud providers for outbound mail |

Set only one of `EMAIL_USE_TLS` / `EMAIL_USE_SSL` to `True` at a time — never both.

## 3. Generating a Gmail App Password

1. Turn on **2-Step Verification** at `myaccount.google.com/security`.
2. Open **App Passwords** (under Security), pick "Mail" as the app and give it a name (e.g. "CommerceCore").
3. Google generates a 16-character password, shown once — copy it immediately.
4. Use that string as `EMAIL_HOST_PASSWORD`. Never use the account's normal login password; Gmail's SMTP server won't accept it once 2-Step Verification is on, and even if it did, it would give the app full account access instead of a scoped, revocable credential.

## 4. Environment Variables

`.env.example` — committed, placeholder values only:

```
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-gmail@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=your-gmail@gmail.com
```

`.env` — real credentials, listed in `.gitignore`, never committed:

```
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=<real address>
EMAIL_HOST_PASSWORD=<the 16-character App Password>
DEFAULT_FROM_EMAIL=<real address>
```

```
.env.example  → template, safe to commit
.env          → real secrets, gitignored, loaded at runtime only
```

## 5. Application Settings

```python
# core/settings/development.py
import os

from .base import *

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"

EMAIL_HOST = os.getenv("EMAIL_HOST")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS", "True") == "True"

EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")

DEFAULT_FROM_EMAIL = os.getenv(
    "DEFAULT_FROM_EMAIL",
    EMAIL_HOST_USER,
)
```

This works because `base.py` already runs `load_dotenv(BASE_DIR / ".env")` before any setting is read, so every `os.getenv()` call here sees the values from `.env`.

Two parsing details worth knowing, since they apply to any environment-variable-driven config, not just this one:

- **`EMAIL_PORT`** comes out of `os.getenv()` as a string — `int(...)` is required, or Django's SMTP client will fail to connect.
- **`EMAIL_USE_TLS`** is compared against the literal string `"True"`. That's fine as long as `.env` consistently uses that exact capitalization; a more typo-tolerant version is `os.getenv("EMAIL_USE_TLS", "True").strip().lower() in ("true", "1", "yes")`.

## 6. Where SMTP Fits in the Pipeline

```
Order
  │
  ▼
Redis (broker)
  │
  ▼
Celery Worker
  │
  ▼
Django SMTP Backend  ← this section
  │
  ▼
Mail Provider (Gmail / SES / SendGrid / ...)
  │
  ▼
Customer's Inbox
```

Nothing upstream of the SMTP backend changes. The task still does `Order.objects.get(id=order_id)` and calls `send_mail(...)`; only where Django hands the message off is different from the console backend used in development.

## 7. Verifying the Configuration

```bash
# keep the broker running
docker start commercecore-redis
docker exec -it commercecore-redis redis-cli PING   # expect PONG

# terminal 1 — worker
celery -A core worker -l INFO --pool=solo

# terminal 2 — shell
python manage.py shell
```

```python
from apps.orders.models import Order
from apps.orders.tasks import send_order_confirmation_email

Order.objects.values_list("id", flat=True)   # pick a real, existing order id
send_order_confirmation_email.delay(65)
```

Watch the worker terminal — a `received` line followed by a `succeeded` line confirms Django successfully handed the message to the SMTP server. That's a different guarantee from "the customer received it," which is why the next two sections matter.

## 8. Reading a Bounce

Sending to an address that doesn't exist (a placeholder like `celeryuser@test.com`, for example) produces a bounce from the mail provider, not from the application:

```
Django SMTP Backend
        │
        ▼
   Gmail SMTP
        │
        ▼
  celeryuser@test.com
        │
        │  ❌ mailbox doesn't exist
        ▼
Gmail Mail Delivery Subsystem
        │
        ▼
mailer-daemon@googlemail.com
        │
        ▼
   Bounce notice
```

`mailer-daemon@googlemail.com` is Gmail's automated delivery-failure responder — it isn't a customer and isn't part of the application. Seeing a bounce is actually a useful signal: it means authentication and the SMTP connection worked, and the only remaining problem is the destination address.

## 9. Resolving the Real Recipient

The address used for testing should never be hardcoded into a call like `send_order_confirmation_email.delay(order_id)` with a manually chosen email — production code should resolve the recipient from the same record the order belongs to.

```
Customer places Order #65
        │
        ▼
Order.user  ──────────► Django User
        │                     │
        ▼                     ▼
order.user.email    (already on the User record —
        │             no extra input needed)
        ▼
send_mail(recipient_list=[order.user.email])
```

Because the task only receives `order_id`, everything else — including who to email — is derived from the database at execution time:

```python
@shared_task
def send_order_confirmation_email(order_id):
    order = Order.objects.select_related("user").get(id=order_id)
    send_mail(
        subject=f"Order Confirmation - Order #{order.id}",
        message=...,
        from_email=None,
        recipient_list=[order.user.email],
    )
```

## 10. Verified Output

Worker log for two separate orders processed through the SMTP backend:

```
Task ...send_order_confirmation_email[e56ed84c-...] received
Preparing confirmation email for order #61
Task ...send_order_confirmation_email[e56ed84c-...] succeeded in 3.94s: None

Task ...send_order_confirmation_email[e177d7e0-...] received
Preparing confirmation email for order #65
Task ...send_order_confirmation_email[e177d7e0-...] succeeded in 4.19s: None
```

And the resulting inbox delivery:

```
From:    commercecoredemo@gmail.com
To:      <real customer inbox>
Subject: Order Confirmation - Order #65

Hello <customer name>,

Thank you for your order!

Order ID: #65
Order Status: PENDING
Total Amount: ₹50000.00

Your order has been successfully placed.

Thank you for shopping with CommerceCore!
```

The longer send time compared to the console backend (a few seconds instead of milliseconds) is expected — that time is the worker holding an actual network connection open to Gmail's SMTP server, which is exactly the latency the checkout view avoids by not sending the email synchronously.

## 11. Production Considerations

- **Sending limits** — Gmail's roughly 500-emails/day (personal) or 2000/day (Workspace) ceiling is fine for development and demos, not for a production customer base.
- **Dedicated sender address** — using an address made for the application (e.g. `commercecoredemo@gmail.com`) rather than a personal inbox keeps replies, bounces, and reputation separate from personal email.
- **Move to an API-based provider at scale** — SES/SendGrid/Mailgun/Postmark expose bounce and complaint webhooks that raw SMTP doesn't, which matters once delivery quality needs to be monitored.
- **Domain authentication** — SPF, DKIM, and DMARC records on the sending domain significantly reduce the odds of transactional email landing in spam.
- **Secrets handling** — App Passwords and API keys belong in environment variables or a secrets manager in every environment, not just `.env` locally; rotate them if a key is ever exposed.

## What This Configuration Proves

| Component | Role | Status |
|---|---|---|
| `.env` / `.env.example` | Credentials loaded via `python-dotenv`, kept out of version control | Verified |
| Gmail App Password | Authenticates SMTP without exposing the account password | Verified |
| Django SMTP backend | Hands the message to a real mail server instead of printing it | Verified |
| Recipient resolution | Pulled from `order.user.email`, never hardcoded | Verified |
| Delivery to a real inbox | Confirmed end to end for Order #65 | Verified |