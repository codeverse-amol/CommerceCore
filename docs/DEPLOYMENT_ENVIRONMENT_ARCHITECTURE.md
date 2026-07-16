# CommerceCore Deployment Environment Architecture

> Purpose:
> This document explains how CommerceCore manages Development and Production environments, why the project is structured this way, and what security measures are implemented.

---

# 1. Why Separate Development & Production?

Development and Production have different requirements.

| Development | Production |
|-------------|------------|
| Easy debugging | Maximum security |
| Fast development | Stability |
| Detailed error pages | Generic error pages |
| Local database | Production database |
| DEBUG=True | DEBUG=False |

Instead of changing settings manually before deployment, CommerceCore uses separate configuration files.

---

# 2. Settings Architecture

```
core/
│
├── settings/
│   ├── __init__.py
│   ├── base.py
│   ├── development.py
│   └── production.py
│
├── wsgi.py
├── asgi.py
└── urls.py
```

### Responsibilities

```
base.py
    │
    ├── Common settings
    ├── Installed Apps
    ├── Middleware
    ├── Database
    ├── Templates
    ├── Static Files
    ├── Logging
    └── REST Framework
```

```
development.py
        │
        ├── from .base import *
        ├── DEBUG=True
        └── Development-only settings
```

```
production.py
        │
        ├── from .base import *
        ├── DEBUG=False
        └── Production security settings
```

---

# 3. Environment Loading

## Local Development

```
Developer

     │

python manage.py runserver

     │

manage.py

     │

core.settings.development

     │

development.py

     │

base.py

     │

Application Starts
```

Result

```
DEBUG=True
```

---

## Production

```
Browser

     │

Nginx

     │

Gunicorn

     │

wsgi.py

     │

core.settings.production

     │

production.py

     │

base.py

     │

Application Starts
```

Result

```
DEBUG=False
```

---

# 4. Environment Variables

Sensitive values are never hardcoded.

All secrets are loaded from

```
.env
```

Example

```env
SECRET_KEY=****************

DEBUG=False

ALLOWED_HOSTS=98.xx.xx.xx

DB_NAME=commercecore_db

DB_USER=root

DB_PASSWORD=********
```

Loaded using

```python
load_dotenv(BASE_DIR / ".env")
```

Advantages

- Credentials not committed to GitHub
- Different values for Development and Production
- Easy deployment
- More secure

---

# 5. Secret Key Management

Instead of

```python
SECRET_KEY = "django-insecure-xxxxxxxx"
```

CommerceCore uses

```python
SECRET_KEY = os.getenv("SECRET_KEY")
```

Validation

```python
if not SECRET_KEY:
    raise RuntimeError(...)
```

Benefits

- Prevents accidental deployments
- Prevents hardcoded secrets
- Safe Git repository

---

# 6. DEBUG Configuration

Development

```python
DEBUG=True
```

Production

```python
DEBUG=False
```

Why?

When DEBUG=True

✔ Stack trace shown

✔ SQL queries visible

✔ Environment details exposed

When DEBUG=False

✔ Generic 500 page

✔ No sensitive information leaked

✔ Errors written to logs

---

# 7. ALLOWED_HOSTS

Only trusted hosts can access the application.

Configured using

```env
ALLOWED_HOSTS=98.xx.xx.xx,localhost,127.0.0.1
```

Loaded dynamically

```python
ALLOWED_HOSTS = [
    host.strip()
    for host in os.getenv("ALLOWED_HOSTS","").split(",")
]
```

Benefits

- Prevents Host Header attacks
- Blocks fake domains
- Allows multiple environments

---

# 8. Production Security Settings

Enabled only when

```python
if not DEBUG:
```

Current implementation

```python
SESSION_COOKIE_HTTPONLY=True

CSRF_COOKIE_HTTPONLY=True

SECURE_PROXY_SSL_HEADER=(...)
```

Future (after HTTPS)

```python
SESSION_COOKIE_SECURE=True

CSRF_COOKIE_SECURE=True
```

Reason

HTTPS is not configured yet.

---

# 9. Logging

Errors are written into

```
logs/django.log
```

Instead of exposing them to users.

Flow

```
Exception

      │

Logging

      │

django.log

      │

Developer Investigation
```

Users only see

```
500 Internal Server Error
```

---

# 10. Deployment Flow

```
Developer

    │

Git Commit

    │

GitHub

    │

GitHub Actions

    │

EC2

    │

git pull

    │

Gunicorn Restart

    │

Production Live
```

---

# 11. Configuration Flow

```
                .env
                  │
                  ▼
             base.py
                  │
      ┌───────────┴───────────┐
      ▼                       ▼
development.py          production.py
      │                       │
      ▼                       ▼
manage.py                 wsgi.py
      │                       │
      ▼                       ▼
 Local Development      Gunicorn + Nginx
```

---

# 12. Security Measures Implemented

✅ Environment Variables

✅ Secret Key Protection

✅ DEBUG=False in Production

✅ Dynamic ALLOWED_HOSTS

✅ Multiple Settings Files

✅ Environment Switching

✅ HTTPOnly Cookies

✅ Secure Proxy Header

✅ Logging

✅ Security Headers

- X_FRAME_OPTIONS="DENY"
- SECURE_CONTENT_TYPE_NOSNIFF
- SECURE_REFERRER_POLICY

---

# Key Takeaways

✔ Separate Development & Production

✔ Environment Variables

✔ Secure Secret Management

✔ Production-safe Configuration

✔ Logging instead of exposing errors

✔ GitHub Actions deployment

✔ Industry-standard Django configuration