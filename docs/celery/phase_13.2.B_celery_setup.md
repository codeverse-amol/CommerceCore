# Celery Setup — Django + Redis

**Stack:** Django · Redis (broker) · Celery 5.6.x
**Scope:** wire Celery into a Django project and confirm a worker can connect to Redis. No task execution yet — dispatching and running a real task is a separate step once this plumbing is verified.

## Architecture

```
Django (producer)
     │  task.delay()
     ▼
Redis :6379 (broker / message queue)
     │  consume
     ▼
Celery Worker (consumer)
```

Django never talks to the worker directly — both sides only talk to Redis. That's what lets the worker run as an independent, restartable process.

## 1. Prerequisites

Redis must already be running and reachable before Celery is introduced.

```bash
docker ps                                          # confirm the container is up
docker start <container-name>                      # if it's stopped
docker exec -it <container-name> redis-cli PING     # expect: PONG
```

## 2. Install

```bash
pip install -U "celery[redis]"
```

The `[redis]` extra pulls in `redis-py`, which Celery's Redis transport depends on — plain `celery` alone isn't enough.

Verify the install:

```bash
celery --version
python -c "import celery; print(celery.__version__)"
```

## 3. Project Layout

```
project/
├── manage.py
└── core/
    ├── __init__.py     ← imports the Celery app
    ├── celery.py       ← defines the Celery app
    └── settings/
        ├── base.py
        ├── development.py
        └── production.py
```

## 4. `core/celery.py`

```python
import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings.development")

app = Celery("core")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
```

| Line | Purpose |
|---|---|
| `os.environ.setdefault(...)` | Sets the default Django settings module *only if it isn't already set* — a process manager in production can still override it via the real environment variable. |
| `Celery("core")` | Creates the Celery application instance. |
| `config_from_object("django.conf:settings", namespace="CELERY")` | Loads config from Django's active settings object; only uppercase `CELERY_`-prefixed keys are read. |
| `autodiscover_tasks()` | Scans every installed app for a `tasks.py` module. |

> **Import string, not a dotted path.** The first argument to `config_from_object` is parsed as `module:attribute`. `"django.conf:settings"` correctly fetches Django's `LazySettings` object. There's no `"module:attribute.sub-attribute"` form — everything after the colon is treated as a single attribute name Celery will `getattr` directly off that module. `django.conf` has no attribute literally called `settings.base`, so passing that raises `AttributeError` / `ModuleNotFoundError`. Environment-specific settings (dev vs. prod) should be controlled through `DJANGO_SETTINGS_MODULE`, not through this string.

## 5. `core/__init__.py`

```python
from .celery import app as celery_app

__all__ = ("celery_app",)
```

Ensures the Celery app loads the moment Django starts, so `@shared_task` has an app to register against.

## 6. Configure the Broker

`.env`:
```
REDIS_URL=redis://127.0.0.1:6379/0
```

`core/settings/base.py`:
```python
REDIS_URL = os.getenv("REDIS_URL", "redis://127.0.0.1:6379/0")
CELERY_BROKER_URL = REDIS_URL
```

| Segment | Meaning |
|---|---|
| `redis://` | scheme |
| `127.0.0.1` | host |
| `6379` | port |
| `/0` | logical DB index |

A result backend (`CELERY_RESULT_BACKEND`) isn't required just to get a worker running — it's only needed once task return values or state need to be stored, which is a separate decision made later.

## 7. Start the Worker

```bash
celery -A core worker -l INFO --pool=solo
```
Replace 'core' with your actual Django project package if it has a different name.

Healthy output includes:

```
.> transport:   redis://127.0.0.1:6379/0
.> concurrency: 16 (solo)
[...] Connected to redis://127.0.0.1:6379/0
[...] celery@HOST ready.
```

An empty `[tasks]` list at this stage is expected — no `tasks.py` module has been created yet.

## Choosing the Right Worker Pool

| Pool | Concurrency model | Good for | Windows |
|---|---|---|---|
| `prefork` (default) | separate OS processes | CPU-bound work; standard for Linux production | ❌ unreliable — relies on `fork()` |
| `solo` | single thread, no concurrency | local dev / debugging | ✅ |
| `threads` | thread pool | I/O-bound tasks needing some concurrency | ✅ |
| `eventlet` / `gevent` | greenlets (separate package) | very high-concurrency I/O (many simultaneous network calls) | ✅ with package installed |

Use `solo` or `threads` for local Windows development. Production deployments (Linux/EC2) default to `prefork` unless the workload is I/O-heavy enough to justify eventlet or gevent.

## Verification Checklist

| Check | Command |
|---|---|
| Redis running | `docker ps` |
| Redis healthy | `redis-cli PING` → `PONG` |
| Celery installed | `celery --version` |
| App wired up | `core/celery.py` exists, imported in `core/__init__.py` |
| Broker configured | `CELERY_BROKER_URL` set in Django settings |
| Worker connects | `celery -A core worker -l INFO --pool=solo` → `ready.` |

## How This Maps to CommerceCore

| Piece | CommerceCore location |
|---|---|
| Celery app | `core/celery.py` |
| App import | `core/__init__.py` |
| Broker config | `core/settings/base.py` (`CELERY_BROKER_URL`) |
| Env var | `.env` → `REDIS_URL` |
| Broker | `commercecore-redis` Docker container, `localhost:6379` |
| Task modules | not yet created — `apps/*/tasks.py` will hold them once real background tasks are added |

At this point Django, Celery, and Redis are wired together and the worker connects successfully — but no task has been dispatched or executed. That's the next piece of work once this foundation is confirmed stable.