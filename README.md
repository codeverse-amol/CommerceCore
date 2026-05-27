# CommerceCore
Backend-focused E-Commerce system built with Django (and ready for DRF). The project emphasizes clean architecture, authentication, caching, async processing, and pragmatic developer workflows.

## Project Architecture

CommerceCore/
│
├── apps/
│   ├── accounts/
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   ├── forms.py
│   │
│   ├── products/
│   ├── carts/
│   ├── orders/
│   └── common/
│
├── templates/
├── media/
├── static/
├── core/
├── manage.py

## Key Features
- User authentication & profiles
- Product management (CRUD, images)
- Shopping cart with cart items and totals
- Order processing and status tracking

## Quick start (development)

Prerequisites: Python 3.10+, git

On Windows (PowerShell):

``powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
``

On macOS / Linux:

``bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
``

Visit http://127.0.0.1:8000/ to view the site in development.

## Running tests

``bash
python manage.py test
``

## Contributing

- Open issues for bugs and feature ideas.
- Follow the existing app structure under `apps/` for new features.

## License

This project is licensed under the terms in the `LICENSE` file.

---
Updated: concise overview and developer setup instructions.