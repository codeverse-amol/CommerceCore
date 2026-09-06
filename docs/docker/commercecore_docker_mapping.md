# CommerceCore — Containerizing a Django Application with Docker

## Objective

Containerize CommerceCore for consistent development and deployment.

### Topics

- [x] Docker Basics
- [x] Dockerfile
- [x] Docker Compose
- [x] Django Container
- [x] MySQL Container
- [x] Nginx Container
- [x] Environment Variables
- [x] Production Deployment

### Table of Contents

1. [Docker Basics](#1-docker-basics)
2. [Dockerfile](#2-dockerfile)
3. [Docker Compose](#3-docker-compose)
4. [Django Container](#4-django-container)
5. [MySQL Container](#5-mysql-container)
6. [Nginx Container](#6-nginx-container)
7. [Environment Variables](#7-environment-variables)
8. [Production Deployment](#8-production-deployment)
9. [Quick Command Reference](#9-quick-command-reference)
10. [References](#10-references)

---

## 1. Docker Basics

### 1.1 What is Docker?

Docker is a platform that packages an application and its dependencies into containers.

Instead of installing everything directly on the EC2 host:

```text
EC2
├── Python
├── Django
├── Redis
├── MySQL
├── Nginx
└── Celery
```

we run each piece as its own container:

```text
EC2
└── Docker
    ├── Django container
    ├── Redis container
    ├── MySQL container
    ├── Celery container
    └── Nginx container
```

EC2 provides the infrastructure; Docker manages the application services on top of it.

### 1.2 Docker Image

An **image** is a packaged blueprint used to create a container.

```text
CommerceCore source code
        +
requirements.txt
        +
Python
        +
dependencies
        ↓
   Docker Image
```

An image on its own isn't a running application — it's the recipe, not the meal.

### 1.3 Docker Container

A **container** is a running instance of an image.

```text
Docker Image
     ↓
Docker Container
     ↓
CommerceCore Django running
```

| Concept | Meaning |
|---|---|
| Image | Blueprint / package |
| Container | Running instance of an image |

You can start multiple containers from the same image (e.g., two Django workers from one `commercecore` image).

### 1.4 Port Mapping

Django currently listens on `127.0.0.1:8000` on the host. Inside Docker, the app listens *inside* the container, and Docker maps a host port to it:

```text
EC2:8000
     │
     ▼
Django container:8000
```

Once Nginx is added:

```text
Internet
   ↓
EC2 :80
   ↓
Nginx container :80
   ↓
Django container :8000
```

A port mapping is written as:

```text
8000:8000
HOST PORT : CONTAINER PORT
```

### 1.5 Docker Network — the Redis fix

This is the concept that solves our current Redis connection problem.

Docker Compose creates a shared network (e.g., `commercecore-network`) that containers on the same project join automatically. On that network, containers can reach each other **by service name** instead of by IP:

```text
Django container
      │
      │  commercecore-network
      ↓
Redis container
```

The key thing to unlearn: inside a container, `127.0.0.1` always means *this same container* — never another one.

```text
Django container → 127.0.0.1:6379   ❌  (looks for Redis inside the Django container itself)
Django container → redis:6379       ✅  (resolves to the Redis container via the network)
```

So every place in `settings.py` that currently says `127.0.0.1` for Redis or MySQL needs to become the **service name** defined in `docker-compose.yml` (`redis`, `mysql`).

### 1.6 Docker Volume

Containers are meant to be disposable. If the MySQL container is removed, the database must survive.

```text
MySQL container
      │
      ▼
Docker Volume
      │
      ▼
Persistent database data
```

- **Container** → temporary application environment
- **Volume** → persistent data, independent of the container's lifecycle

```text
Delete MySQL container
        ↓
Create new MySQL container
        ↓
Attach existing volume
        ↓
✅ Data remains
```

### 1.7 Container Lifecycle

```text
Created → Running → Stopped → Started again → Removed
```

| Command | Purpose |
|---|---|
| `docker ps` | List running containers |
| `docker ps -a` | List all containers (including stopped) |
| `docker start <container>` | Start a stopped container |
| `docker stop <container>` | Stop a running container |
| `docker restart <container>` | Restart a container |
| `docker rm <container>` | Remove a container |

### 1.8 Why Docker Solves the EC2 Problem

Current EC2 deployment:

```text
EC2
 │
 ├── Gunicorn
 ├── Nginx
 └── Django virtual environment

Django → 127.0.0.1:6379 → ❌ Connection refused (Redis isn't installed on the host)
```

Target architecture with Docker Compose:

```text
                    EC2
                     │
                   Docker
                     │
       ┌─────────────┼──────────────┐
       │             │              │
       ▼             ▼              ▼
    Nginx          Django          Redis
  container       container       container
                     │
                     ▼
                   MySQL
                  container
                     │
                     ▼
                  Volume

                    Redis
                   /     \
                  ▼       ▼
             Django      Celery
```

This gives every environment (laptop, staging, EC2) the same set of services, wired together the same way.

### 1.9 Concept Summary

| Docker concept | CommerceCore mapping |
|---|---|
| Image | The CommerceCore application image |
| Container | Django/Gunicorn running environment |
| Dockerfile | Instructions to build the CommerceCore image |
| Network | Django ↔ Redis ↔ MySQL ↔ Celery |
| Volume | Persistent MySQL data |
| Port | Nginx/Django exposed ports |
| Lifecycle | Start / stop / restart / remove services |

---

## 2. Dockerfile

A `Dockerfile` is the set of instructions Docker follows to build an image.

```text
Dockerfile → docker build → Docker Image → docker run → Container
```

For CommerceCore, the project will eventually look like:

```text
CommerceCore/
│
├── Dockerfile
├── .dockerignore
├── docker-compose.yml
├── entrypoint.sh
├── requirements.txt
├── manage.py
├── apps/
└── core/
```

### 2.1 Key instructions

| Instruction | Purpose |
|---|---|
| `FROM` | Base image to build on top of |
| `WORKDIR` | Sets the working directory inside the container |
| `COPY` | Copies files from the host into the image (prefer over `ADD`) |
| `RUN` | Executes a command at build time (installing packages, etc.) |
| `ENV` | Sets environment variables baked into the image |
| `EXPOSE` | Documents which port the container listens on |
| `USER` | Switches to a non-root user for the remaining instructions |
| `ENTRYPOINT` / `CMD` | Defines what runs when the container starts |

### 2.2 CommerceCore Dockerfile

This follows current Docker guidance for Python images: a slim base, a multi-stage build so build tools don't ship in the final image, and a non-root user.

```dockerfile
# syntax=docker/dockerfile:1
ARG PYTHON_VERSION=3.12-slim

########################################
# Stage 1: build wheels for dependencies
########################################
FROM python:${PYTHON_VERSION} AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        default-libmysqlclient-dev \
        pkg-config \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt

########################################
# Stage 2: runtime image
########################################
FROM python:${PYTHON_VERSION}

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Runtime-only system dependency for MySQL client libraries
RUN apt-get update && apt-get install -y --no-install-recommends \
        default-libmysqlclient-dev \
        default-mysql-client \
    && rm -rf /var/lib/apt/lists/*

# Non-root user
RUN addgroup --system django && adduser --system --ingroup django django

COPY --from=builder /app/wheels /wheels
COPY requirements.txt .
RUN pip install --no-cache-dir /wheels/* && rm -rf /wheels

COPY . .
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh && chown -R django:django /app

USER django

EXPOSE 8000

ENTRYPOINT ["/entrypoint.sh"]
CMD ["gunicorn", "core.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
```

### 2.3 `.dockerignore`

Keep build context small and secrets out of the image:

```text
.git
.gitignore
__pycache__/
*.pyc
*.pyo
.env
.env.*
.venv/
venv/
db.sqlite3
media/
staticfiles/
*.log
node_modules/
```

### 2.4 Build it

```bash
docker build -t commercecore:latest .
```

---

## 3. Docker Compose

Docker Compose describes all CommerceCore services — Django, MySQL, Redis, Celery, Nginx — as one file, so the whole stack starts with one command.

> Modern Compose (the `docker compose` v2 CLI) no longer needs a top-level `version:` key — it's obsolete and safely omitted.

### 3.1 `docker-compose.yml`

```yaml
services:
  django:
    build: .
    container_name: commercecore-django
    command: gunicorn core.wsgi:application --bind 0.0.0.0:8000 --workers 3
    volumes:
      - static_volume:/app/staticfiles
      - media_volume:/app/media
    expose:
      - "8000"
    env_file:
      - .env
    depends_on:
      mysql:
        condition: service_healthy
      redis:
        condition: service_started
    networks:
      - commercecore-network
    restart: unless-stopped

  mysql:
    image: mysql:8.0
    container_name: commercecore-mysql
    restart: unless-stopped
    environment:
      MYSQL_ROOT_PASSWORD: ${MYSQL_ROOT_PASSWORD}
      MYSQL_DATABASE: ${MYSQL_DATABASE}
      MYSQL_USER: ${MYSQL_USER}
      MYSQL_PASSWORD: ${MYSQL_PASSWORD}
    volumes:
      - mysql_data:/var/lib/mysql
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - commercecore-network

  redis:
    image: redis:7-alpine
    container_name: commercecore-redis
    restart: unless-stopped
    networks:
      - commercecore-network

  celery:
    build: .
    container_name: commercecore-celery
    command: celery -A core worker -l info
    env_file:
      - .env
    depends_on:
      - django
      - redis
    networks:
      - commercecore-network
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    container_name: commercecore-nginx
    ports:
      - "80:80"
    volumes:
      - ./nginx/default.conf:/etc/nginx/conf.d/default.conf:ro
      - static_volume:/app/staticfiles:ro
      - media_volume:/app/media:ro
    depends_on:
      - django
    networks:
      - commercecore-network
    restart: unless-stopped

volumes:
  mysql_data:
  static_volume:
  media_volume:

networks:
  commercecore-network:
    driver: bridge
```

Notice `django` and `celery` expose no host port at all — only `nginx` does. Nothing outside Docker needs to reach Gunicorn directly.

### 3.2 Everyday commands

```bash
docker compose up -d --build     # build images and start everything, detached
docker compose ps                # see what's running
docker compose logs -f django    # tail logs for one service
docker compose exec django sh    # shell into the running Django container
docker compose down              # stop and remove containers (volumes kept)
docker compose down -v           # also remove volumes — wipes MySQL data, use with care
```

---

## 4. Django Container

### 4.1 `entrypoint.sh`

Django's container needs to wait for MySQL to be ready, then run migrations and collect static files, before Gunicorn starts:

```bash
#!/bin/sh
set -e

echo "Waiting for MySQL at ${DB_HOST}:${DB_PORT}..."
until mysqladmin ping -h"${DB_HOST}" -P"${DB_PORT}" --silent; do
    sleep 1
done
echo "MySQL is ready."

python manage.py migrate --noinput
python manage.py collectstatic --noinput

exec "$@"
```

The `exec "$@"` at the end hands off to whatever `CMD` was set in the Dockerfile (Gunicorn), so signals like `SIGTERM` reach the actual process correctly.

### 4.2 `settings.py` changes for containers

```python
import os

ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "").split(",")

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": os.environ["DB_NAME"],
        "USER": os.environ["DB_USER"],
        "PASSWORD": os.environ["DB_PASSWORD"],
        "HOST": os.environ.get("DB_HOST", "mysql"),   # service name, not 127.0.0.1
        "PORT": os.environ.get("DB_PORT", "3306"),
    }
}

CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL", "redis://redis:6379/0")

STATIC_URL = "/static/"
STATIC_ROOT = "/app/staticfiles"

MEDIA_URL = "/media/"
MEDIA_ROOT = "/app/media"
```

The important habit carried over from [Section 1.5](#15-docker-network--the-redis-fix): `HOST` and broker URLs use the **service name** (`mysql`, `redis`), never `127.0.0.1` or `localhost`.

---

## 5. MySQL Container

CommerceCore uses the official `mysql` image from Docker Hub rather than installing MySQL on the host.

### 5.1 Environment variables

| Variable | Purpose |
|---|---|
| `MYSQL_ROOT_PASSWORD` | Required unless you explicitly allow an empty password. Sets the root user's password. |
| `MYSQL_DATABASE` | Creates this database automatically on first startup. |
| `MYSQL_USER` / `MYSQL_PASSWORD` | Creates an application user with full access to `MYSQL_DATABASE`. Both must be set together. |
| `MYSQL_ALLOW_EMPTY_PASSWORD` | Optional, dev-only — never use in production. |

These only take effect the **first time** the container initializes an empty data directory; if a volume already has data, they're ignored on subsequent restarts.

### 5.2 Persistence

The image stores its data at `/var/lib/mysql` inside the container, which is why `docker-compose.yml` mounts a named volume there:

```yaml
volumes:
  - mysql_data:/var/lib/mysql
```

Removing the `mysql` container never touches this volume — a new container just reattaches to it.

### 5.3 Backups

```bash
docker compose exec mysql sh -c \
  'mysqldump -u root -p"$MYSQL_ROOT_PASSWORD" $MYSQL_DATABASE' > backup.sql
```

Store backups off the instance (e.g., S3), not just on the same EC2 volume.

---

## 6. Nginx Container

Nginx terminates the incoming request, serves static/media files directly, and proxies everything else to Django/Gunicorn.

### 6.1 `nginx/default.conf`

```nginx
upstream django {
    server django:8000;
}

server {
    listen 80;
    server_name _;

    client_max_body_size 20M;

    location /static/ {
        alias /app/staticfiles/;
    }

    location /media/ {
        alias /app/media/;
    }

    location / {
        proxy_pass http://django;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

`upstream django { server django:8000; }` again relies on Compose's network — `django` here is the service name, resolved automatically to the Django container's internal IP.

### 6.2 Why this matters

- Gunicorn is good at running Python, not at serving static files efficiently or handling slow clients — Nginx does both better.
- Only Nginx publishes a host port (`80:80`); Django and Celery stay internal to the Docker network.

---

## 7. Environment Variables

### 7.1 `.env` (never committed — add to `.gitignore` and `.dockerignore`)

```env
DEBUG=False
SECRET_KEY=change-me-to-a-real-secret
ALLOWED_HOSTS=commercecore.example.com,localhost

DB_HOST=mysql
DB_PORT=3306
DB_NAME=commercecore
DB_USER=commercecore_user
DB_PASSWORD=supersecret

MYSQL_ROOT_PASSWORD=rootsecret
MYSQL_DATABASE=commercecore
MYSQL_USER=commercecore_user
MYSQL_PASSWORD=supersecret

CELERY_BROKER_URL=redis://redis:6379/0
```

Commit a `.env.example` instead, with the same keys and placeholder values, so teammates know what to fill in.

### 7.2 How Compose reads it

- `env_file: .env` in `docker-compose.yml` loads every key into the container's environment.
- `environment:` (as used for `mysql` above) can reference those same values with `${VARIABLE_NAME}` syntax, letting one `.env` file drive multiple services consistently.

### 7.3 Reading it in Django

`os.environ["DB_NAME"]` works, but a small library removes boilerplate and adds type casting:

```bash
pip install django-environ
```

```python
import environ
env = environ.Env()
environ.Env.read_env()

DEBUG = env.bool("DEBUG", default=False)
SECRET_KEY = env("SECRET_KEY")
```

### 7.4 Dev vs. prod

Keep separate files — `.env.dev` and `.env.prod` — and point Compose at the right one:

```bash
docker compose --env-file .env.prod up -d
```

---

## 8. Production Deployment

### 8.1 What changes from development

| Dev | Prod |
|---|---|
| Code often bind-mounted for live reload | Code baked into the image at build time |
| `DEBUG=True` | `DEBUG=False`, real `ALLOWED_HOSTS` |
| `restart: unless-stopped` | `restart: always` |
| Gunicorn with a couple of workers | Worker count tuned to CPU (`2 × cores + 1`) |
| Ports open for local testing | Only Nginx publishes a port |

### 8.2 `docker-compose.prod.yml` (used as an override)

```yaml
services:
  django:
    image: your-registry/commercecore:latest   # pre-built, not `build:` on the server
    restart: always
    env_file:
      - .env.prod

  celery:
    image: your-registry/commercecore:latest
    restart: always
    env_file:
      - .env.prod

  nginx:
    restart: always
```

```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### 8.3 Build → ship → run

```text
CI pipeline:
  docker build -t your-registry/commercecore:$GIT_SHA .
  docker push your-registry/commercecore:$GIT_SHA

EC2:
  docker pull your-registry/commercecore:$GIT_SHA
  docker compose up -d
```

Building on the server itself works for a single small EC2 instance, but building once in CI and pulling a tagged image keeps every environment on an identical, reproducible artifact.

### 8.4 Static files, HTTPS, logging

- **Static files**: run `collectstatic` at image-build time (or in the entrypoint on deploy) so Nginx always has the latest assets in the shared volume.
- **HTTPS**: terminate TLS either in the Nginx container (with Certbot) or one layer up at a load balancer in front of EC2; Nginx then forwards plain HTTP to Django internally.
- **Logging**: let containers log to stdout/stderr (Gunicorn and Nginx do this by default) and ship those logs off-box with the Docker logging driver or a sidecar, rather than writing to files inside the container.
- **Monitoring**: `docker stats` for a quick look; Compose `healthcheck:` blocks plus `restart: always` give basic self-healing before reaching for anything heavier like ECS or Kubernetes.

### 8.5 Backups & rollbacks

- Automate `mysqldump` off the `mysql_data` volume on a schedule; store the dump somewhere off the instance (S3, etc.).
- Because images are tagged by commit SHA, a bad deploy is a rollback: `docker pull ...:<previous-sha> && docker compose up -d`.

---

## 9. Quick Command Reference

```bash
# Images / containers
docker build -t commercecore:latest .
docker ps
docker ps -a
docker start <container>
docker stop <container>
docker restart <container>
docker rm <container>

# Compose
docker compose up -d --build
docker compose ps
docker compose logs -f <service>
docker compose exec <service> sh
docker compose down
docker compose down -v      # ⚠️ also deletes volumes

# MySQL
docker compose exec mysql mysql -u root -p
docker compose exec mysql sh -c 'mysqldump -u root -p"$MYSQL_ROOT_PASSWORD" $MYSQL_DATABASE' > backup.sql
```

---

## 10. References

- Docker Dockerfile best practices — docs.docker.com/develop/develop-images/dockerfile_best-practices/
- Docker Compose file reference — docs.docker.com/reference/compose-file/
- Official `mysql` image — hub.docker.com/_/mysql
- Official `nginx` image — hub.docker.com/_/nginx
- Official `redis` image — hub.docker.com/_/redis
- Official `python` image — hub.docker.com/_/python

Treat these as the source of truth if any command or option above ever looks out of date — image tags and CLI flags do shift over time.