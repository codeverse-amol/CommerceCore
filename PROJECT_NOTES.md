# CommerceCore - Project Notes

Quick reference for key files and components.

## Frontend

### Navbar & Layout
- Base template: `templates/base.html`
- Navbar CSS: `static/css/base.css`
- Toggle sidebar logic: `templates/base.html` (JavaScript)

### Components
- Button component: `templates/components/button.html`
- Modal component: `templates/components/modal.html`
- Stats card: `templates/components/stats_card.html`
- Table component: `templates/components/table.html`

### Styling
- Main styles: `static/css/base.css`
- Cart page: `static/css/cart.css`
- Dashboard: `static/css/dashboard.css`
- Login/Register: `static/css/login.css`
- Orders page: `static/css/orders.css`
- Products page: `static/css/products.css`

## Backend - Apps

### Accounts (Authentication)
- Models: `apps/accounts/models.py`
- Views: `apps/accounts/views.py`
- Forms: `apps/accounts/forms.py`
- URLs: `apps/accounts/urls.py`
- Templates: `templates/accounts/login.html`, `register.html`

### Products
- Models: `apps/products/models.py`
- Views: `apps/products/views.py`
- Forms: `apps/products/forms.py`
- URLs: `apps/products/urls.py`
- Admin: `apps/products/admin.py`
- Template (list): `templates/products/listProducts.html`
- Template (add): `templates/products/addProducts.html`
- Template (categories): `templates/products/addCategory.html`
- Template (tags): `templates/products/addTags.html`

### Cart
- Models: `apps/carts/models.py`
- Views: `apps/carts/views.py`
- URLs: `apps/carts/urls.py`
- Template: `templates/carts/cart.html`
- Styling: `static/css/cart.css`

### Orders
- Models: `apps/orders/models.py`
- Views: `apps/orders/views.py` (Order placement logic)
- URLs: `apps/orders/urls.py`
- Admin: `apps/orders/admin.py`
- Template (success): `templates/orders/order_success.html`
- Styling: `static/css/orders.css`

### Main/Dashboard
- Models: `apps/main/models.py`
- Views: `apps/main/views.py`
- URLs: `apps/main/urls.py`
- Template (dashboard): `templates/main/dashboard.html`
- Template (landing): `templates/main/landing.html`
- Styling: `static/css/dashboard.css`

### Common
- Models: `apps/common/models.py`
- Views: `apps/common/views.py`
- Admin: `apps/common/admin.py`

## Configuration

- Settings: `core/settings.py`
- URL routing: `core/urls.py`
- Management: `manage.py`
- Dependencies: `requirements.txt`

## Media & Static Files

- Product images: `media/products/`
- Profile images: `media/profiles/`
- Static assets: `static/`

## Navigation Structure

- Dashboard: URL name `dashboard`
- Products List: URL name `list_products`
- View Cart: URL name `view_cart`
