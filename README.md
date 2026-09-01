# CommerceCore

CommerceCore is a production-ready e-commerce platform built with Django and Django REST Framework. The system provides complete storefront functionality, user authentication, product management, shopping cart, order processing, and cloud-based deployment infrastructure.

## Features & Capabilities

- **User Management:** Registration, login, profile management, session handling
- **Product Catalog:** Full CRUD operations, image uploads, search functionality, category filtering
- **Shopping Cart:** Item management, quantity tracking, persistent cart storage
- **Order Processing:** Order placement, status tracking, order history and details
- **REST API:** DRF endpoints with serializers and permission classes
- **Cloud Storage:** AWS S3 integration for media files with secure IAM access
- **Production Deployment:** Nginx reverse proxy, Gunicorn application server, GitHub Actions CI/CD

## Tech stack

- **Backend:** Python 3.10+, Django 6.0+, Django REST Framework
- **Database:** MySQL/MariaDB (RDS-compatible)
- **Frontend:** HTML5, CSS3, Django templates
- **Task Queue:** Celery + Redis
- **Storage:** AWS S3 with django-storages and boto3
- **Deployment:** Nginx (reverse proxy), Gunicorn (app server)
- **Infrastructure:** AWS EC2
- **CI/CD:** GitHub Actions
## Project structure

```text
CommerceCore/
├── apps/
│   ├── accounts/
│   ├── api/
│   ├── carts/
│   ├── common/
│   ├── main/
│   ├── orders/
│   └── products/
├── core/
├── templates/
├── static/
├── media/
├── docs/
└── manage.py
```

## Quick start (development)

### Prerequisites

- Python 3.10+
- Git
- Virtual environment tool

### Windows (PowerShell)

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

### macOS / Linux

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Open http://127.0.0.1:8000/ to view the site locally.

## Environment configuration

Create a `.env` file with values such as:

```env
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
DB_NAME=commercecore_db
DB_USER=root
DB_PASSWORD=your-password
```

## Running tests

```bash
python manage.py test
```

## Deployment notes

The project is configured for production deployment using:

- **Reverse Proxy:** Nginx on port 80/443, routing `/static/`, `/media/`, and Django requests
- **Application Server:** Gunicorn with systemd service management
- **Hosting:** AWS EC2 instance
- **Deployment Automation:** GitHub Actions with SSH deployment to EC2
- **Media Storage:** AWS S3 for scalable file storage
- **Error Handling:** Custom 404 & 500 pages, production logging

**Production Architecture:**
```
Internet → Nginx → Gunicorn → Django → MariaDB
                 ↓
              S3 Bucket (media)
```

## Cloud Storage & Media Handling

CommerceCore uses AWS S3 for secure, scalable media storage. The system is configured with:

- S3 bucket with secure IAM user access (least-privilege policy)
- django-storages and boto3 for seamless Django integration
- Automatic media upload and retrieval from S3
- CloudFront CDN for optimized media delivery

Environment configuration for S3 is handled through `.env` variables:

```env
AWS_ACCESS_KEY_ID=your-iam-access-key
AWS_SECRET_ACCESS_KEY=your-iam-secret-key
AWS_STORAGE_BUCKET_NAME=your-bucket-name
AWS_S3_REGION_NAME=us-east-1
```

## Future Enhancements

- Payment gateway integration
- Advanced analytics and reporting
- Performance optimization and caching improvements

## License

This project is licensed under the terms described in the `LICENSE` file.