# CommerceCore — AWS EC2 Docker Migration Validation

## 1. Purpose

This document records validation performed while migrating CommerceCore from the existing host-based EC2 deployment to Docker.

**Current status:** Docker migration validation is complete. **Production cutover is still pending.**

The Docker deployment was tested in parallel on port `8080`, while the existing production Nginx/Gunicorn deployment on port `80` remained untouched.

## 2. Existing Production Architecture

```text
Internet
   |
   v
AWS EC2
   |
   +--> Host Nginx :80
   |
   +--> Host Gunicorn :127.0.0.1:8000
   |
   +--> Django application
   |
   +--> Amazon RDS MySQL
   |
   +--> Amazon S3 / CloudFront
```

## 3. Target Docker Architecture

```text
EC2 :8080
   |
   v
Docker Nginx :80
   |
   v
Django / Gunicorn container
   |
   +--> Amazon RDS MySQL
   |
   +--> Redis
   |
   +--> Amazon S3 / CloudFront

Celery container
   |
   +--> Redis
   +--> Amazon RDS MySQL
```

Production database remains Amazon RDS and is **not containerized**.

## 4. Docker Services

| Service | Purpose |
|---|---|
| `web` | Django + Gunicorn |
| `nginx` | Reverse proxy + static file server |
| `redis` | Redis service |
| `celery` | Background task worker |

## 5. Validation Evidence

### 5.1 Docker Buildx

Initial EC2 Buildx version:

```text
github.com/docker/buildx 0.12.1
```

Docker Compose required Buildx `0.17.0` or later.

Final verified version:

```text
github.com/docker/buildx v0.37.2
```

**Result: PASS**

---

### 5.2 Production Docker Images

Command:

```bash
docker compose -f docker-compose.prod.yml build
```

Result:

```text
[+] build 2/2
✔ Image commercecore-celery Built
✔ Image commercecore-web Built
```

**Result: PASS**

---

### 5.3 Django Application Check

Command:

```bash
docker compose -f docker-compose.prod.yml run --rm web python manage.py check
```

Result:

```text
System check identified no issues (0 silenced).
```

**Result: PASS**

---

### 5.4 Docker → Amazon RDS

Command:

```bash
docker compose -f docker-compose.prod.yml run --rm web python manage.py shell -c "from django.db import connection; connection.ensure_connection(); print('DB CONNECTION OK'); print('DB HOST:', connection.settings_dict['HOST'])"
```

Result:

```text
DB CONNECTION OK
DB HOST: <production RDS endpoint>
```

**Result: PASS**

The Dockerized Django application successfully connected to the existing Amazon RDS MySQL database.

No database password was exposed in the validation output.

---

### 5.5 Docker Services Running

Commands:

```bash
docker compose -f docker-compose.prod.yml up -d
docker compose -f docker-compose.prod.yml ps
```

Verified:

```text
commercecore-web-prod
commercecore-celery-prod
commercecore-redis-prod
commercecore-nginx-prod
```

Docker Nginx:

```text
0.0.0.0:8080 -> 80
```

**Result: PASS**

---

### 5.6 Application HTTP Test

Command:

```bash
curl -I http://127.0.0.1:8080/
```

Result:

```text
HTTP/1.1 200 OK
Server: nginx/1.31.6
Content-Type: text/html; charset=utf-8
```

**Result: PASS**

This proves the request successfully reaches Docker Nginx and the Django/Gunicorn application.

---

### 5.7 Static Files

Command:

```bash
docker compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput
```

Result:

```text
171 static files copied to '/app/staticfiles'.
```

Test:

```bash
curl -I http://127.0.0.1:8080/static/css/base.css
```

Result:

```text
HTTP/1.1 200 OK
Content-Type: text/css
```

**Result: PASS**

---

### 5.8 S3 / CloudFront Media

Production Django configuration reported:

```text
MEDIA_URL: https://<cloudfront-domain>/
STORAGE: storages.backends.s3.S3Storage
```

An existing media object was tested:

```text
products/alienware.jpg
```

Result:

```text
EXISTS: True
URL: https://<cloudfront-domain>/products/alienware.jpg
```

**Result: PASS**

The Dockerized Django application can access the existing S3-backed media storage and generate the expected CloudFront URL.

---

# 6. Overall Validation

| Area | Status |
|---|---|
| Buildx | PASS |
| Docker image build | PASS |
| Django system check | PASS |
| Docker → RDS | PASS |
| Redis | PASS |
| Celery | PASS |
| Django/Gunicorn | PASS |
| Nginx | PASS |
| Application HTTP response | PASS |
| Static file serving | PASS |
| S3/CloudFront media | PASS |
| Existing production deployment interrupted | NO |

## Conclusion

The Dockerized CommerceCore application has been successfully validated on AWS EC2.

The Docker deployment can:

- start all required services
- load the production Django configuration
- connect to Amazon RDS
- run Django/Gunicorn
- run Redis
- run Celery
- serve the application through Nginx
- serve static files
- use the existing S3/CloudFront media configuration

The validation was performed on port `8080`, so the existing production application on port `80` was not interrupted.

# 7. Migration Status

```text
Phase 1 — Understand existing application        COMPLETE
Phase 2 — Dockerize application                  COMPLETE
Phase 3 — Local Docker validation                COMPLETE
Phase 4 — AWS production Docker configuration    COMPLETE
Phase 5 — EC2 Docker validation                  COMPLETE
Phase 6 — Parallel production validation         COMPLETE
Phase 7 — Production port-80 cutover             PENDING
Phase 8 — HTTPS / final production hardening     PENDING
Phase 9 — Old host deployment cleanup            PENDING
```

# 8. Cutover Plan

The final cutover should happen only after approval and a rollback plan.

1. Confirm Docker services are healthy.
2. Confirm backup/rollback plan.
3. Change Docker Nginx from port `8080` to port `80`.
4. Commit the configuration change locally.
5. Push to GitHub.
6. Pull the change on EC2.
7. Stop/disable the old host Gunicorn service.
8. Stop/disable the old host Nginx service.
9. Start Docker Nginx on port 80.
10. Validate the public application.
11. Validate application, database, static files, media, and background jobs.
12. Monitor logs and application behavior.
13. Keep the old deployment available until Docker production stability is confirmed.

Do not immediately delete the old virtual environment, host Nginx configuration, or other legacy components. Keep a rollback path until stability is confirmed.

# 9. Rollback Strategy

If the Docker deployment has an issue after cutover:

```text
Stop Docker Nginx
       |
       v
Restore host Nginx
       |
       v
Restore host Gunicorn
       |
       v
Verify application
```

The RDS database remains unchanged because both deployments use the same production database.

# 10. Evidence Screenshots

Recommended evidence files:

```text
docs/migration/screenshots/
├── 01-buildx-upgrade.png
├── 02-docker-build-success.png
├── 03-django-check.png
├── 04-rds-connectivity.png
├── 05-docker-services-running.png
├── 06-application-http-200.png
├── 07-static-files-200.png
└── 08-s3-cloudfront-media.png
```

For a public GitHub repository, redact passwords, access keys, secret keys, database credentials, tokens, and unnecessary infrastructure identifiers.

# 11. Git Commit Recommendation

Validation documentation:

```text
docs: add Docker migration validation evidence
```

Future production cutover:

```text
deploy: switch production nginx to Docker
```

Keeping these separate makes the migration history easy to review and clearly distinguishes validation from the actual production cutover.
