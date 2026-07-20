# Environment Variables

## What are Environment Variables?

Environment variables are configuration values stored **outside the application code**.

Instead of hardcoding secrets in `settings.py`, Django reads them from the operating system or a `.env` file.

Example:

```python
SECRET_KEY = os.getenv("SECRET_KEY")
```

```
.env

↓

SECRET_KEY=django-insecure-xxxxxxxx
```

---

# Why use Environment Variables?

Advantages

- Prevent secrets from being committed to GitHub.
- Different configuration for Development and Production.
- Easier deployment.
- Better security.
- Industry best practice.

---

# CommerceCore Environment Variables

Current `.env`

```env
DEBUG=True

SECRET_KEY=********

ALLOWED_HOSTS=localhost,127.0.0.1,<EC2-IP>

DB_NAME=commerceCore_db
DB_USER=root
DB_PASSWORD=******
DB_HOST=localhost
DB_PORT=3306
```

---

# How Django Loads Variables

```python
from dotenv import load_dotenv
import os

load_dotenv(BASE_DIR / ".env")
```

Example

```python
SECRET_KEY = os.getenv("SECRET_KEY")

DEBUG = os.getenv("DEBUG", "False").lower() == "true"

ALLOWED_HOSTS = [
    host.strip()
    for host in os.getenv("ALLOWED_HOSTS", "").split(",")
    if host.strip()
]
```

---

# Database Configuration

```python
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": os.getenv("DB_NAME"),
        "USER": os.getenv("DB_USER"),
        "PASSWORD": os.getenv("DB_PASSWORD"),
        "HOST": os.getenv("DB_HOST", "localhost"),
        "PORT": os.getenv("DB_PORT", "3306"),
    }
}
```

---

# Best Practices

✅ Keep secrets in `.env`

✅ Commit `.env.example`

✅ Never commit `.env`

✅ Add default values where appropriate

✅ Validate required variables like `SECRET_KEY`

---

# Files

```
CommerceCore/

│── .env               ❌ Never commit

│── .env.example       ✅ Commit

│── .gitignore

│── core/
      settings.py
```

---

# .gitignore

```gitignore
.env
```

---

# .env.example

```env
DEBUG=True

SECRET_KEY=your-secret-key

ALLOWED_HOSTS=localhost,127.0.0.1

DB_NAME=your_database
DB_USER=your_username
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=3306
```

---

# Why not Hardcode?

❌

```python
SECRET_KEY = "django-insecure-abc123"
```

Anyone who clones the repository can see it.

---

✅

```python
SECRET_KEY = os.getenv("SECRET_KEY")
```

Only the server knows the real value.

---

# Interview Questions

### Why should secrets not be hardcoded?

Because source code is often stored in Git repositories. Hardcoding secrets exposes sensitive credentials and increases security risk.

---

### What should be stored in `.env`?

- SECRET_KEY
- Database credentials
- API keys
- Email credentials
- Allowed hosts
- Debug flag

---

### Why commit `.env.example` but not `.env`?

`.env.example` documents the required variables without exposing sensitive values, while `.env` contains real secrets and should remain private.

---

 
Implemented ✅

- Environment Variables
- `.env`
- `.env.example`
- `.gitignore`
- Secure SECEY loading
- Secure Database Configuration
- ALLOWED_HOSTS from Environment
- DEBUG from Environment