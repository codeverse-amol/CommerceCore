# Phase 14 – Docker & Containerization (CommerceCore)

Oct 13, 2026 · @Buddy

Phase 14 containerized CommerceCore and validated a production-oriented Docker stack on AWS EC2 using port 8080; the final cutover to port 80 is still pending.

| Item | Detail |
| --- | --- |
| Project | CommerceCore |
| Roadmap status | Completed (as requested) |
| Deployment status | Docker stack validated on EC2 using port `8080`; final cutover to port `80` remains pending |

## 1. Goal

Containerize CommerceCore and validate a production-oriented Docker deployment. Learn to run Django/Gunicorn, Nginx, Redis, and Celery as separate services, configure their networking, and deploy them on AWS EC2.

## 2. Learning Outcomes

- Understand Docker images, containers, Dockerfiles, networks, volumes, and Compose.
- Build a Docker image for the Django application.
- Run multiple services with Docker Compose.
- Serve Django static files through Nginx.
- Configure Redis for Django caching and as the Celery broker.
- Run Celery as a separate worker container.
- Use environment variables without committing production secrets.
- Validate Docker alongside the existing host deployment before cutover.

## 3. Core Concepts

| Component | Purpose |
| --- | --- |
| Docker image | Packaged application and runtime dependencies |
| Container | Running instance of an image |
| Dockerfile | Instructions for building an image |
| Docker Compose | Defines and runs multiple services |
| Docker network | Allows services to communicate by Compose service name |
| Volume | Persists or shares data |
| Nginx | Reverse proxy and static-file server |
| Gunicorn | Runs the Django WSGI application |
| Redis | Cache backend and Celery broker |
| Celery worker | Processes background tasks |
| `.env` | Environment-specific configuration; keep secrets private |
| `.env.example` | Safe template for required variables |

## 4. Architecture

### 4.1 Local development

The local Compose setup can include Django web, Nginx, MySQL, Redis, and Celery. A named volume such as `mysql_data` can persist local MySQL data.

### 4.2 AWS EC2 production validation

```text
Browser
   |
   v
Docker Nginx :8080
   |-- /static/ --> Static files volume
   |-- /media/  --> Mounted media path (S3/CloudFront is used for production media URLs)
   |
   v
Django Web / Gunicorn :8000
   |                         |
   v                         v
AWS RDS MySQL              Redis :6379
                              |
                              v
                         Celery Worker
```

Production-specific decisions:

- Production database stays on AWS RDS; no MySQL container is needed in `docker-compose.prod.yml`.
- Docker Nginx is mapped to host port `8080` during parallel validation because host Nginx owns port `80`.
- Containers communicate through Compose service names such as `web` and `redis`.
- Existing host Nginx/Gunicorn remain available until a planned production cutover.

## 5. Important Files

```text
CommerceCore/
├── Dockerfile
├── docker-compose.prod.yml
├── .dockerignore
├── .env                 # secrets; never commit
├── .env.example
├── nginx/
│   └── production.conf
├── core/
│   └── settings/
│       ├── base.py
│       └── production.py
└── .github/
    └── workflows/
        └── deploy.yml
```

### 5.1 Dockerfile

The application image starts Gunicorn on port `8000` inside the container:

```dockerfile
CMD ["gunicorn", "core.wsgi:application", "--bind", "0.0.0.0:8000"]
```

### 5.2 Production Compose services

- `web`: Django/Gunicorn application
- `redis`: Redis service
- `celery`: Celery worker using the application image
- `nginx`: reverse proxy and static-file server

### 5.3 Production Nginx behavior

- Serves `/static/` from `/app/staticfiles/`.
- Defines a `/media/` alias for the mounted media directory.
- Proxies application requests to `http://web:8000`.
- Forwards host, client IP, forwarded IP, and protocol headers.

## 6. Redis and Celery Configuration

The application reads the Redis URL from an environment variable:

```python
REDIS_URL = os.getenv("REDIS_URL", "redis://127.0.0.1:6379/0")
CELERY_BROKER_URL = REDIS_URL
```

In Docker production, `.env` uses:

```dotenv
REDIS_URL=redis://redis:6379/0
```

Inside a container, `127.0.0.1` points to that same container. The Compose service name `redis` resolves to the Redis container. This configuration is used for Django caching and the Celery broker.

**Security:** Never commit `.env` or paste production secrets into documentation, screenshots, or chat messages.

## 7. Validation Commands

Run these from the CommerceCore repository on EC2.

**Validate Compose configuration** (review output privately if it includes environment values):

```bash
docker compose -f docker-compose.prod.yml config
```

**Build images:**

```bash
docker compose -f docker-compose.prod.yml build
```

**Django system check:**

```bash
docker compose -f docker-compose.prod.yml run --rm web python manage.py check
```

**Collect static files:**

```bash
docker compose -f docker-compose.prod.yml run --rm web python manage.py collectstatic --noinput
```

**Start and inspect services:**

```bash
docker compose -f docker-compose.prod.yml up -d
docker compose -f docker-compose.prod.yml ps
```

**Inspect logs:**

```bash
docker compose -f docker-compose.prod.yml logs --tail=100 web
docker compose -f docker-compose.prod.yml logs --tail=100 nginx
docker compose -f docker-compose.prod.yml logs --tail=100 celery
```

**Test the Docker Nginx endpoint during parallel validation:**

```bash
curl -I http://127.0.0.1:8080/
curl -I http://127.0.0.1:8080/static/css/base.css
```

**Verify Django's Redis settings:**

```bash
docker compose -f docker-compose.prod.yml run --rm web python -c "from django.conf import settings; print(settings.REDIS_URL); print(settings.CELERY_BROKER_URL)"
```

Expected values:

```text
redis://redis:6379/0
redis://redis:6379/0
```

## 8. Validation Results

The following checks were recorded as successful during EC2 validation:

- Production Docker images built successfully.
- `manage.py check` reported no issues.
- Static files were collected into `/app/staticfiles/`.
- Docker Nginx served the tested CSS file with `200 OK`.
- The Docker homepage returned `200 OK` on port `8080` after Nginx was recreated with the restored port mapping.
- Django connected to the production RDS database during validation.
- Production media settings used the S3/CloudFront URL.
- A known product image in S3 was confirmed to exist.
- Django and Celery used `redis://redis:6379/0`.
- Celery logs confirmed it connected to Redis and became ready.
- The `web`, `redis`, `celery`, and `nginx` Compose services were running during the last recorded check.
- The existing host application continued responding on port `80` while Docker was tested on port `8080`.

## 9. GitHub Actions Deployment Workflow

The tracked workflow is `.github/workflows/deploy.yml`. It:

1. Triggers on pushes to `main`, subject to configured path exclusions.
2. Runs on `ubuntu-latest`.
3. Connects to EC2 through SSH using GitHub Secrets.
4. Changes to `/home/ec2-user/CommerceCore`.
5. Executes `./deploy.sh` on EC2.

The workflow alone does not tell us which services `deploy.sh` changes. Inspect the actual EC2 script before relying on it for a Docker cutover. The EC2 copy was previously observed as untracked by Git, so do not assume it is managed by the repository.

## 10. Safety and Rollback Notes

- Keep production `.env` private and out of version control.
- Do not recreate Docker Nginx with a `80:80` mapping while host Nginx owns port `80`; the port binding will fail.
- Keep host Nginx/Gunicorn available until the cutover and rollback procedure are understood.
- Use `8080:80` for Docker Nginx during parallel testing.
- Do not stop host services until the Docker stack, deployment script, cutover steps, and rollback procedure have been checked.
- Avoid destructive database operations during validation.
- HTTPS/cookie security settings and `manage.py check --deploy` warnings remain separate production-hardening work.

## 11. Completion Checklist

- [x] Understand Docker images, containers, networks, volumes, and Compose.
- [x] Build the production Docker images.
- [x] Run Django/Gunicorn in Docker.
- [x] Configure Nginx as reverse proxy and static-file server.
- [x] Keep production database on AWS RDS.
- [x] Configure Redis using the Compose service name.
- [x] Run Celery as a separate service and verify broker connectivity.
- [x] Collect and serve static files.
- [x] Validate the Docker homepage on port `8080`.
- [x] Preserve the existing host application during validation.
- [x] Mark Phase 14 completed in the learning roadmap.
- [ ] Perform the final production cutover from host services to Docker on port `80`.
- [ ] Verify the public endpoint after cutover and confirm rollback readiness.
- [ ] Complete separate HTTPS and production security hardening.

**Roadmap status:** Completed. The final port-80 cutover remains a separate pending production operation.

## 12. Key Takeaways

1. Docker packages the application and its runtime dependencies.
2. Docker Compose defines and operates a multi-service application.
3. Containers should use Compose service names, not `localhost`, to reach other services.
4. Production can use managed AWS RDS instead of running MySQL in a container.
5. Static files, uploaded media, secrets, logs, and persistent data need deliberate storage decisions.
6. A successful test on port `8080` supports migration readiness but is not the same as completing the production cutover on port `80`.
