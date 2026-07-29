# CommerceCore

CommerceCore is a backend-focused e-commerce platform built with Django and Django REST Framework. The project currently includes core storefront features, authentication, product management, cart and order flows, and deployment-ready configuration for both development and production environments.

## Current project status

CommerceCore is now in a mature implementation stage with:

- Django-based user authentication and profile management
- Product catalog, search, and CRUD workflows
- Shopping cart and order processing flow
- Separate development and production settings
- Production deployment setup with Nginx, Gunicorn, AWS EC2, and GitHub Actions
- Environment-based configuration for secrets and server settings
- API app structure for upcoming DRF expansion

## Tech stack

- Python 3.10+
- Django
- Django REST Framework
- MySQL/PostgreSQL-compatible database support
- HTML/CSS templates with static/media handling
- AWS S3-compatible media storage support
- Nginx + Gunicorn for production deployment

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

- Nginx as a reverse proxy
- Gunicorn as the application server
- AWS EC2 hosting
- GitHub Actions-based deployment automation

Additional deployment documentation is available in the `docs/` and `docs-o/` folders.

## Next steps

Planned improvements include:

- Expanding the REST API endpoints
- Improving checkout and payment integration
- Performance tuning and caching
- Further UI and admin enhancements

## License

This project is licensed under the terms described in the `LICENSE` file.