# First Background Task

> Creating and executing the first asynchronous Celery task in CommerceCore, verifying the Django → Celery → Redis → Worker pipeline end-to-end.

## Overview

A Celery task is a Python function registered with Celery so it can run outside the request/response cycle, executed by a separate worker process rather than the process that submits it. Before implementing business-critical background work — such as order confirmation emails — it's necessary to confirm the full asynchronous pipeline (Django, Celery, Redis, and the worker) operates correctly, using a minimal, side-effect-free task.

This document covers defining a task, registering it for automatic discovery, submitting it asynchronously, and verifying its execution in a separate worker process.

## Prerequisites

- Django, Celery, and Redis already configured and connected
- `core/celery.py` containing `app.autodiscover_tasks()`
- Redis broker reachable at `redis://127.0.0.1:6379/0`
- A Django app (`main`) present in `INSTALLED_APPS`
- Virtual environment activated

## Core Concepts

| Concept | Description |
|---|---|
| `@shared_task` | Decorator that registers a function as a Celery task without binding it to a specific app instance, so it can be imported from any Django app |
| `autodiscover_tasks()` | Scans installed Django apps for a `tasks.py` module and registers any tasks found |
| `.delay()` | Shortcut for submitting a task for asynchronous execution; equivalent to `apply_async()` with no extra options |
| `AsyncResult` | Handle returned by `.delay()`, identified by a unique task ID, used to reference the submitted task |

## Architecture

```text
Django (task defined in apps/main/tasks.py)
     │
     ▼
Celery App (registers task via autodiscover_tasks)
     │
     ▼
Redis Broker (redis://127.0.0.1:6379/0)
     │
     ▼
Celery Worker (consumes and executes task)
     │
     ▼
Console Output
```

## Implementation

### Task Definition — `apps/main/tasks.py`

```python
from celery import shared_task


@shared_task
def hello_task():
    print("Hello from Celery!")
```

### Explanation

`@shared_task` registers `hello_task` as a Celery task independent of any specific Celery app instance, letting it be imported anywhere while still being discoverable through `autodiscover_tasks()`. Placing it inside `apps/main/`, an installed Django app, ensures Celery finds it automatically at worker startup — no manual registration is required.

## Execution Flow

```text
Django Shell
     │  hello_task.delay()
     ▼
Celery — creates task message
     │
     ▼
Redis Broker — stores the message
     │
     ▼
Celery Worker — consumes the message
     │
     ▼
Worker executes hello_task()
     │
     ▼
"Hello from Celery!" printed in the worker process
```

`hello_task.delay()` does not execute the function in the calling process. It publishes a task message to Redis; the worker, running as a separate process, consumes and executes it. This is what distinguishes it from a direct call, `hello_task()`, which runs synchronously in the current process.

## Configuration

Worker startup (Windows):

```powershell
celery -A core worker -l INFO --pool=solo
```
`core' is project name.

`--pool=solo` runs the worker in a single-threaded pool within the same process. It is required on Windows because Celery's default prefork pool depends on `os.fork()`, which is not available on that platform.

Relevant broker configuration confirmed at worker startup:

```text
.> transport:   redis://127.0.0.1:6379/0
.> results:     disabled://
.> concurrency: 16 (solo)
.> queues:      celery exchange=celery(direct) key=celery
```

No result backend is configured (`results: disabled://`). Submitted tasks return an `AsyncResult` with a task ID, but their state and return value cannot be queried afterward — a result backend (e.g. Redis) must be configured for that.

## Verification

### Task Registration

```text
[tasks]
  . apps.main.tasks.hello_task
```

### Task Submission — Django Shell

```python
>>> from apps.main.tasks import hello_task
>>> hello_task.delay()
<AsyncResult: 2e4d2c72-4adb-41c4-b5bb-803d02341f93>
>>> hello_task.delay()
<AsyncResult: 14c0f817-d9bc-4c77-8eb5-382f06b559de>
```

### Verified Output — Worker Terminal

```text
[2026-08-16 19:24:36,883: INFO/MainProcess] Connected to redis://127.0.0.1:6379/0
[2026-08-16 19:24:38,131: INFO/MainProcess] celery@AMOL-DEV ready.
[2026-08-16 19:25:17,538: INFO/MainProcess] Task apps.main.tasks.hello_task[2e4d2c72-4adb-41c4-b5bb-803d02341f93] received
[2026-08-16 19:25:17,539: WARNING/MainProcess] Hello from Celery!
[2026-08-16 19:25:17,539: INFO/MainProcess] Task apps.main.tasks.hello_task[2e4d2c72-4adb-41c4-b5bb-803d02341f93] succeeded in 0.00034s: None
[2026-08-16 19:25:29,268: INFO/MainProcess] Task apps.main.tasks.hello_task[14c0f817-d9bc-4c77-8eb5-382f06b559de] received
[2026-08-16 19:25:29,268: WARNING/MainProcess] Hello from Celery!
[2026-08-16 19:25:29,269: INFO/MainProcess] Task apps.main.tasks.hello_task[14c0f817-d9bc-4c77-8eb5-382f06b559de] succeeded in 0.00035s: None
```

Both submissions were received, executed, and completed successfully, each producing the expected console output and a `succeeded` status. `print()` output from within a task is captured by Celery's stdout redirection and logged at `WARNING` level by default — this is expected behavior, not an error.

## Direct Call vs `.delay()`

| Call | Executes In | Behavior |
|---|---|---|
| `hello_task()` | Current process (e.g. Django shell) | Synchronous — blocks until complete |
| `hello_task.delay()` | Celery worker process | Asynchronous — returns immediately with an `AsyncResult` |

## Troubleshooting

### Task doesn't appear under `[tasks]`

**Cause:** `tasks.py` is missing, or the app isn't in `INSTALLED_APPS`.

**Solution:**
```powershell
# Verify apps/main/tasks.py exists and 'main' is in INSTALLED_APPS, then:
celery -A core worker -l INFO --pool=solo
```

### `ModuleNotFoundError`

**Cause:** Worker or shell started from the wrong directory, or the virtual environment isn't active.

**Solution:**
```powershell
# Run from the CommerceCore root (where manage.py lives)
.\venv\Scripts\activate
```

### Worker can't connect to Redis

**Cause:** Redis container isn't running, or the broker URL is misconfigured.

**Solution:**
```powershell
docker ps
docker exec -it commercecore-redis redis-cli PING
# Expect: PONG
```

## Best Practices

- Keep initial infrastructure tasks free of side effects beyond logging, to isolate transport issues from business logic
- Never call a task directly (`hello_task()`) when asynchronous execution is intended — this defeats the purpose of offloading work
- Restart the worker after adding or changing a task module so `autodiscover_tasks()` picks up the change
- Configure a result backend before relying on task state or return values
- Keep the worker terminal visible during development to observe task lifecycle events in real time

## Key Takeaways

- A Celery task is a Python function registered with Celery via `@shared_task`
- `autodiscover_tasks()` finds `tasks.py` modules in installed Django apps automatically
- `.delay()` submits a task for asynchronous execution and is equivalent to `apply_async()` with default options
- The Django process and the Celery worker are separate processes connected through the Redis broker
- Successful execution is confirmed by matching `received` → `succeeded` log entries in the worker terminal

## How This Maps to CommerceCore

`apps/main/tasks.py` establishes the pattern used for all subsequent CommerceCore background work. The Django → Celery → Redis → Worker pipeline validated here will carry the order confirmation email task, replacing `hello_task()` with real business logic (order processing → email dispatch) without any change to the underlying infrastructure.