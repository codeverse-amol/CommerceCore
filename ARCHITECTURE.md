# CommerceCore - Project Architecture

## Table of Contents
1. [Overview](#overview)
2. [System Architecture](#system-architecture)
3. [Data Model](#data-model)
4. [App Layer Architecture](#app-layer-architecture)
5. [Request Flow](#request-flow)
6. [Frontend Architecture](#frontend-architecture)
7. [API Endpoints](#api-endpoints)
8. [Data Flow Diagrams](#data-flow-diagrams)
9. [Technology Stack](#technology-stack)
10. [Design Patterns](#design-patterns)
11. [Key Relationships](#key-relationships)

---

## Overview

**CommerceCore** is a Django-based e-commerce platform designed with a modular architecture. It handles user authentication, product catalog management, shopping cart functionality, and order processing.

**Key Features:**
- User registration & authentication
- Product browsing with categories and tags
- Shopping cart management
- Order placement and tracking
- Admin dashboard for product management

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                    CommerceCore - E-Commerce Platform               │
└─────────────────────────────────────────────────────────────────────┘

                         ┌──────────────┐
                         │   Frontend   │
                         │  (Templates) │
                         └──────────────┘
                               │
                ┌──────────────┼──────────────┐
                │              │              │
         ┌──────┴─────┐  ┌────┴────┐  ┌─────┴──────┐
         │  Dashboard │  │ Products │  │Cart/Orders │
         └──────┬─────┘  └────┬────┘  └─────┬──────┘
                │              │             │
                └──────────────┼─────────────┘
                               │
                    ┌──────────▼────────────┐
                    │  URL Router           │
                    │  (core/urls.py)       │
                    └──────────┬────────────┘
                               │
        ┌──────────┬───────────┼───────────┬──────────┐
        │          │           │           │          │
   ┌────▼──┐  ┌────▼──┐  ┌────▼──┐  ┌────▼──┐  ┌────▼──┐
   │Account│  │Products│  │ Carts │  │Orders │  │ Main  │
   │ Views │  │ Views  │  │ Views │  │ Views │  │ Views │
   └────┬──┘  └────┬───┘  └────┬──┘  └────┬──┘  └────┬──┘
        │          │           │          │          │
        └──────────┼───────────┼──────────┼──────────┘
                   │
        ┌──────────▼────────────────────┐
        │   Django ORM / Models Layer    │
        │   (core/settings.py)           │
        └──────────┬────────────────────┘
                   │
        ┌──────────▼────────────────────┐
        │     PostgreSQL/SQLite DB       │
        └────────────────────────────────┘
```

---

## Data Model

### Entity Relationship Diagram (ERD)

```
┌──────────────────┐
│      User        │ (Django Built-in)
│  (auth)          │
└────────┬─────────┘
         │
    ┌────┼────┬────────┬─────────┐
    │    │    │        │         │
1:1 │1:1 │1:1 │  1:N   │  1:N    │
    │    │    │        │         │
    ▼    ▼    ▼        ▼         ▼
┌────────┐ ┌─────────────┐ ┌───────────┐ ┌───────────┐
│ Profile│ │    Cart     │ │   Order   │ │ OrderItem │
│        │ │             │ │           │ │           │
└────────┘ └─────┬───────┘ └─────┬─────┘ └─────┬─────┘
                 │               │             │
              N:M │               │ Related to  │
              thru│               │ Product    │
            CartItem             │
                 │               │
                 └───────┬───────┘
                         │
                    ┌────▼────┐
                    │ Product  │
                    └────┬─────┘
                         │
              ┌──────────┼──────────┐
              │          │          │
            N:1        M:M        M:M
              │          │          │
              ▼          ▼          ▼
        ┌──────────┐ ┌──────┐ ┌─────────────┐
        │ Category │ │ Tags │ │  CartItems  │
        │          │ │      │ │  & OrderItem│
        └──────────┘ └──────┘ └─────────────┘
```

### Model Details

#### User (Django Built-in)
```python
- id (Primary Key)
- username (unique)
- email
- password (hashed)
- first_name
- last_name
- is_active
- is_staff
- date_joined
```

#### Profile (1:1 → User)
```python
- id (Primary Key)
- user (OneToOneField → User)
- fullName (CharField)
- phone (IntegerField)
- address (CharField)
- profileImage (ImageField)
- gender (Choice: M, F, O)
```

#### Product
```python
- id (Primary Key)
- name (CharField)
- price (DecimalField)
- category (ForeignKey → Category)
- tags (ManyToManyField → Tag)
- image (ImageField)
- stock (PositiveIntegerField)
- description (TextField)
```

#### Category (1:N → Product)
```python
- id (Primary Key)
- name (CharField)
```

#### Tag (M:M → Product)
```python
- id (Primary Key)
- name (CharField)
```

#### Cart (1:1 → User)
```python
- id (Primary Key)
- user (OneToOneField → User)
```

#### CartItem (M:N through Cart & Product)
```python
- id (Primary Key)
- cart (ForeignKey → Cart)
- product (ForeignKey → Product)
- quantity (IntegerField)
- added_at (DateTimeField)
- total_price (DecimalField)
```

#### Order (N:1 → User)
```python
- id (Primary Key)
- user (ForeignKey → User)
- created_at (DateTimeField)
- total_amount (DecimalField)
- status (Choice: PENDING, PAID, SHIPPED, DELIVERED, CANCELLED)
```

#### OrderItem (N:1 → Order, N:1 → Product)
```python
- id (Primary Key)
- order (ForeignKey → Order)
- product (ForeignKey → Product)
- quantity (PositiveIntegerField)
- unit_price (DecimalField)
```

---

## App Layer Architecture

| App | Purpose | Responsibility |
|-----|---------|-----------------|
| **accounts** | User authentication & profile management | User registration, login, logout, profile creation & updates |
| **products** | Product catalog management | CRUD operations for products, categories, tags, filtering |
| **carts** | Shopping cart functionality | Add/remove items, cart display, quantity management |
| **orders** | Order management & checkout | Order creation, order history, status tracking |
| **main** | Landing page & dashboard | Homepage, user dashboard, analytics |
| **common** | Shared utilities | Common models and views used across apps |
| **core** | Project configuration | Settings, URL routing, WSGI/ASGI, middleware |

### App File Structure

```
apps/
├── accounts/
│   ├── models.py      (Profile model)
│   ├── views.py       (Auth views)
│   ├── forms.py       (Registration/Login forms)
│   ├── urls.py        (URL patterns)
│   ├── admin.py       (Admin panel config)
│   └── templates/     (Login, Register pages)
│
├── products/
│   ├── models.py      (Product, Category, Tag)
│   ├── views.py       (List, detail, CRUD)
│   ├── forms.py       (Product forms)
│   ├── urls.py        (URL patterns)
│   ├── admin.py       (Admin panel config)
│   └── templates/     (Product list, add, etc.)
│
├── carts/
│   ├── models.py      (Cart, CartItem)
│   ├── views.py       (Cart operations)
│   ├── urls.py        (URL patterns)
│   ├── admin.py       (Admin panel config)
│   └── templates/     (Cart display)
│
├── orders/
│   ├── models.py      (Order, OrderItem)
│   ├── views.py       (Checkout, order history)
│   ├── urls.py        (URL patterns)
│   ├── admin.py       (Admin panel config)
│   └── templates/     (Order success, history)
│
├── main/
│   ├── models.py
│   ├── views.py       (Dashboard, landing)
│   ├── urls.py        (URL patterns)
│   └── templates/     (Dashboard, landing)
│
└── common/
    ├── models.py      (Shared models)
    └── views.py       (Shared utilities)
```

---

## Request Flow

### 1. User Registration & Login
```
GET /accounts/register/ → Show registration form
    ↓
POST /accounts/register/ → Create User + Profile (1:1)
    ↓
Redirect to /accounts/login/

GET /accounts/login/ → Show login form
    ↓
POST /accounts/login/ → Authenticate user
    ↓
Create session → Redirect to /main/dashboard/
```

### 2. Product Browsing
```
GET /products/list/ → Query all products
    ├─ Filter by Category
    ├─ Filter by Tags
    └─ Join with Category & Tags tables
    ↓
Render: templates/products/listProducts.html
    └─ Display product list with filters
```

### 3. Add to Cart
```
POST /carts/add/ (AJAX or Form)
    ├─ Get or Create Cart (1:1 with User)
    ├─ Get Product
    ├─ Create/Update CartItem
    │   ├─ cart_id
    │   ├─ product_id
    │   ├─ quantity
    │   └─ total_price = product.price * quantity
    └─ Response: Success or error
```

### 4. View Cart
```
GET /carts/view/
    ├─ Query Cart → CartItems
    ├─ Join with Product table
    ├─ Calculate subtotal
    ├─ Calculate taxes (if applicable)
    ├─ Calculate shipping (if applicable)
    └─ Calculate total = sum(CartItem.total_price)
    ↓
Render: templates/carts/cart.html
    └─ Display items + checkout button
```

### 5. Checkout → Place Order
```
POST /orders/create/ (From cart checkout)
    ├─ Get Cart + CartItems for user
    ├─ Create Order
    │   ├─ user_id
    │   ├─ total_amount = cart.total
    │   └─ status = 'PENDING'
    ├─ Create OrderItem(s) from CartItem(s)
    │   ├─ order_id
    │   ├─ product_id
    │   ├─ quantity
    │   └─ unit_price
    ├─ Clear CartItems (empty cart)
    └─ Redirect to /orders/success/
```

### 6. Order Tracking
```
GET /orders/history/
    ├─ Query Order objects where user = current_user
    ├─ Join with OrderItem
    └─ Display list of orders with status

GET /orders/detail/<order_id>/
    ├─ Query Order + OrderItems
    ├─ Show order details
    └─ Allow status tracking & cancellation
```

---

## Frontend Architecture

### Template Hierarchy

```
templates/
│
├── base.html (Master template)
│   ├── Navbar with logo
│   ├── Sidebar with navigation
│   └── Main content block
│
├── main/
│   ├── landing.html (Public homepage)
│   └── dashboard.html (User dashboard)
│
├── accounts/
│   ├── login.html (Login form)
│   └── register.html (Registration form)
│
├── products/
│   ├── listProducts.html (Product catalog)
│   ├── addProducts.html (Admin: Add product)
│   ├── addCategory.html (Admin: Add category)
│   └── addTags.html (Admin: Add tags)
│
├── carts/
│   └── cart.html (Shopping cart display)
│
├── orders/
│   └── order_success.html (Order confirmation)
│
└── components/
    ├── button.html (Reusable button)
    ├── modal.html (Reusable modal)
    ├── stats_card.html (Dashboard stats)
    └── table.html (Reusable table)
```

### CSS Organization

```
static/css/
├── base.css           (Main styles, navbar, sidebar)
├── cart.css           (Cart-specific styles)
├── dashboard.css      (Dashboard styles)
├── login.css          (Login/register forms)
├── orders.css         (Order-related styles)
└── products.css       (Product listing styles)
```

### Navigation Structure

```
Navbar (Global)
├── Logo: "CommerceCore"
└── Menu button (☰) → Toggle Sidebar

Sidebar Navigation
├── Dashboard ({% url 'dashboard' %})
├── Products ({% url 'list_products' %})
└── Cart ({% url 'view_cart' %})
```

---

## API Endpoints

### Authentication Routes
```
GET    /accounts/login/          → Show login form
POST   /accounts/login/          → Process login
GET    /accounts/register/       → Show registration form
POST   /accounts/register/       → Create new user
GET    /accounts/logout/         → Logout user
```

### Product Routes
```
GET    /products/list/           → Display all products
GET    /products/detail/<id>/    → Product details
GET    /products/add/            → Product form (admin)
POST   /products/add/            → Create product (admin)
GET    /products/edit/<id>/      → Edit form (admin)
POST   /products/edit/<id>/      → Update product (admin)
POST   /products/delete/<id>/    → Delete product (admin)
GET    /products/category/       → Filter by category
GET    /products/tags/           → Filter by tags
```

### Cart Routes
```
GET    /carts/view/              → Display cart
POST   /carts/add/               → Add item to cart
POST   /carts/remove/<item_id>/  → Remove item from cart
POST   /carts/update/<item_id>/  → Update quantity
POST   /carts/clear/             → Empty cart
```

### Order Routes
```
POST   /orders/create/           → Place order (checkout)
GET    /orders/history/          → View user's orders
GET    /orders/detail/<id>/      → Order details
POST   /orders/cancel/<id>/      → Cancel order
GET    /orders/success/          → Order confirmation
```

### Main/Dashboard Routes
```
GET    /                         → Landing page
GET    /main/dashboard/          → User dashboard
GET    /main/                    → Main landing
```

---

## Data Flow Diagrams

### Complete E-Commerce Journey

```
┌─────────────────────────────────────────────────────────────────┐
│                    USER E-COMMERCE FLOW                         │
└─────────────────────────────────────────────────────────────────┘

START
  │
  ├─► [REGISTRATION] ────► Create User + Profile (1:1)
  │
  ├─► [LOGIN] ────────────► Authenticate + Create Session
  │
  ├─► [BROWSE PRODUCTS] ──► SELECT: Category/Tags/Search
  │        │
  │        └─► Load Product + Category + Tags (Joins)
  │
  ├─► [ADD TO CART] ──────► Create/Update CartItem
  │        │                  (Cart ← User 1:1)
  │        │
  │        └─► Store: cart_id, product_id, qty, total_price
  │
  ├─► [VIEW CART] ────────► Query CartItems + Products
  │        │
  │        ├─► Calculate Subtotal
  │        ├─► Calculate Tax (if any)
  │        ├─► Calculate Shipping (if any)
  │        └─► Display Total
  │
  ├─► [CHECKOUT] ─────────► POST /orders/create/
  │        │
  │        ├─► Create Order (user, total_amount, status='PENDING')
  │        ├─► Create OrderItems from CartItems
  │        ├─► Update Product.stock
  │        └─► Clear CartItems
  │
  ├─► [CONFIRMATION] ─────► Render order_success.html
  │        │
  │        └─► Display Order Details + Receipt
  │
  └─► [ORDER TRACKING] ───► Monitor Order Status
          └─► Status: PENDING → PAID → SHIPPED → DELIVERED
```

### Cart → Order Conversion

```
┌──────────────────────────────────────┐
│        Shopping Cart State           │
├──────────────────────────────────────┤
│ Cart (1:1 User)                      │
│  └─ CartItem[]                       │
│      ├─ product_id = 5               │
│      ├─ quantity = 2                 │
│      └─ total_price = $59.98         │
│                                      │
│      ├─ product_id = 8               │
│      ├─ quantity = 1                 │
│      └─ total_price = $29.99         │
└──────────────────────────────────────┘
           │
           │ CHECKOUT
           │ /orders/create/
           ▼
┌──────────────────────────────────────┐
│       Order Created State            │
├──────────────────────────────────────┤
│ Order                                │
│  ├─ user_id = 3                      │
│  ├─ total_amount = $89.97            │
│  └─ status = 'PENDING'               │
│                                      │
│  └─ OrderItem[]                      │
│      ├─ product_id = 5               │
│      ├─ quantity = 2                 │
│      └─ unit_price = $29.99          │
│                                      │
│      ├─ product_id = 8               │
│      ├─ quantity = 1                 │
│      └─ unit_price = $29.99          │
└──────────────────────────────────────┘
           │
           │ CartItems CLEARED
           ▼
┌──────────────────────────────────────┐
│        Empty Cart State              │
├──────────────────────────────────────┤
│ Cart (1:1 User)                      │
│  └─ CartItem[] = EMPTY               │
└──────────────────────────────────────┘
```

---

## Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Backend Framework** | Django 3.2+ | Web framework & ORM |
| **Database** | SQLite (dev) / PostgreSQL (prod) | Data persistence |
| **Frontend** | Django Templates | Server-side rendering |
| **Styling** | CSS3 | Visual presentation |
| **Scripting** | JavaScript (Vanilla) | Client-side interactivity |
| **Authentication** | Django Auth | User management & sessions |
| **Image Handling** | Pillow | Image processing & upload |
| **Python Version** | 3.8+ | Language runtime |

### Dependencies (from requirements.txt)
- Django
- Pillow (Image support)
- python-decouple (Environment variables)
- Additional packages as needed

---

## Design Patterns

### 1. Model-Template-View (MTV)
Django's architectural pattern separating concerns:
- **Models**: Data layer (`apps/*/models.py`)
- **Views**: Business logic layer (`apps/*/views.py`)
- **Templates**: Presentation layer (`templates/*/`)

### 2. One-to-One Relationships
```python
# Example: User ↔ Profile, User ↔ Cart
user_instance.profile  # Access profile directly
user_instance.cart     # Access cart directly
```

### 3. One-to-Many Relationships
```python
# Example: Category → Products
category.products.all()  # Get all products in category
product.category         # Access parent category
```

### 4. Many-to-Many Relationships
```python
# Example: Product ↔ Tags
product.tags.all()      # Get all tags for product
tag.products.all()      # Get all products with tag
```

### 5. User Isolation Pattern
Each user has their own:
- Profile (1:1)
- Cart (1:1)
- Orders (1:N)
- Session (implicit in Django)

### 6. Order Snapshot Pattern
OrderItem stores product data at time of order (not just product_id):
- Preserves product data if product is deleted
- Records price at purchase time (unit_price)
- Maintains order immutability

### 7. Middleware & Signals (Optional Future)
- Auto-create Profile on User creation
- Auto-create Cart on User creation
- Update product stock on order placement

### 8. View-based Logic
Clean separation in views:
- `accounts/views.py` → Authentication
- `products/views.py` → Product CRUD
- `carts/views.py` → Cart logic
- `orders/views.py` → Checkout logic

---

## Key Relationships

### User-centric View
```
User (1)
  ├─ (1:1) Profile
  ├─ (1:1) Cart
  │        └─ (1:N) CartItem
  │                 └─ (N:1) Product
  └─ (1:N) Order
           └─ (1:N) OrderItem
                    └─ (N:1) Product
```

### Product-centric View
```
Product (1)
  ├─ (N:1) Category
  ├─ (M:M) Tag
  ├─ (M:N) CartItem (via Cart)
  └─ (N:1) OrderItem (via Order)
```

### Admin Responsibilities
```
Admin User (is_staff=True)
  ├─ CRUD Products
  ├─ CRUD Categories
  ├─ CRUD Tags
  ├─ View all Orders
  ├─ View all Users
  └─ Manage staff users
```

---

## Future Enhancements

1. **Payment Integration** - Stripe/PayPal for real transactions
2. **Email Notifications** - Order confirmation, shipment tracking
3. **Search & Filters** - Full-text search on products
4. **Reviews & Ratings** - User feedback system
5. **Wishlist** - Save favorite products
6. **Inventory Management** - Stock tracking & notifications
7. **Analytics** - Sales dashboard, reports
8. **Multi-vendor** - Seller accounts & commissions
9. **API Layer** - REST/GraphQL for mobile apps
10. **Caching** - Redis for performance

---

## Summary

CommerceCore follows Django MVT architecture with:
- **Modular apps** for clean separation of concerns
- **Relational database** with proper normalization
- **User-isolation** for multi-tenant safety
- **Scalable structure** ready for future features
- **Clean code practices** following Django conventions

The project is production-ready for a small to medium e-commerce platform!


# Full Project Folder Structure

```
CommerceCore/
│
├── LICENSE
├── README.md
├── manage.py                          # Django management script
├── requirements.txt                   # Project dependencies
├── PROJECT_NOTES.md                   # Quick reference file
│
├── apps/                              # Django applications
│   │
│   ├── accounts/                      # User authentication & profiles
│   │   ├── __init__.py
│   │   ├── admin.py                   # Admin panel configuration
│   │   ├── apps.py                    # App configuration
│   │   ├── forms.py                   # Registration/Login forms
│   │   ├── models.py                  # Profile model
│   │   ├── tests.py                   # Unit tests
│   │   ├── urls.py                    # URL patterns
│   │   ├── views.py                   # Authentication views
│   │   └── migrations/
│   │       ├── __init__.py
│   │       └── 0001_initial.py        # Initial migration
│   │
│   ├── carts/                         # Shopping cart management
│   │   ├── __init__.py
│   │   ├── admin.py                   # Admin panel configuration
│   │   ├── apps.py                    # App configuration
│   │   ├── models.py                  # Cart & CartItem models
│   │   ├── tests.py                   # Unit tests
│   │   ├── urls.py                    # URL patterns
│   │   ├── views.py                   # Cart views
│   │   └── migrations/
│   │       ├── __init__.py
│   │       ├── 0001_initial.py        # Initial migration
│   │       └── 0002_cartitem_total_price.py
│   │
│   ├── common/                        # Shared utilities
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py                    # App configuration
│   │   ├── models.py                  # Common models
│   │   ├── tests.py                   # Unit tests
│   │   ├── views.py                   # Common views
│   │   └── migrations/
│   │       └── __init__.py
│   │
│   ├── main/                          # Landing page & dashboard
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py                    # App configuration
│   │   ├── models.py
│   │   ├── tests.py                   # Unit tests
│   │   ├── urls.py                    # URL patterns
│   │   ├── views.py                   # Dashboard & landing views
│   │   └── migrations/
│   │       └── __init__.py
│   │
│   ├── orders/                        # Order management
│   │   ├── __init__.py
│   │   ├── admin.py                   # Admin panel configuration
│   │   ├── apps.py                    # App configuration
│   │   ├── models.py                  # Order & OrderItem models
│   │   ├── tests.py                   # Unit tests
│   │   ├── urls.py                    # URL patterns
│   │   ├── views.py                   # Order placement & tracking views
│   │   └── migrations/
│   │       ├── __init__.py
│   │       ├── 0001_initial.py        # Initial migration
│   │       ├── 0002_remove_order_price.py
│   │       ├── 0003_order_total_amount_orderitem_unit_price.py
│   │       └── 0004_order_status_alter_order_total_amount_and_more.py
│   │
│   └── products/                      # Product catalog
│       ├── __init__.py
│       ├── admin.py                   # Admin panel configuration
│       ├── apps.py                    # App configuration
│       ├── forms.py                   # Product forms
│       ├── models.py                  # Product, Category, Tag models
│       ├── tests.py                   # Unit tests
│       ├── urls.py                    # URL patterns
│       ├── views.py                   # Product CRUD views
│       └── migrations/
│           ├── __init__.py
│           ├── 0001_initial.py        # Initial migration
│           ├── 0002_product_image.py
│           └── 0003_remove_product_user_product_description_and_more.py
│
├── core/                              # Django project configuration
│   ├── __init__.py
│   ├── asgi.py                        # ASGI configuration
│   ├── settings.py                    # Project settings
│   ├── urls.py                        # Main URL router
│   └── wsgi.py                        # WSGI configuration
│
├── media/                             # User-uploaded files
│   ├── products/                      # Product images directory
│   └── profiles/                      # Profile images directory
│
├── static/                            # Static files (CSS, JS, images)
│   ├── css/
│   │   ├── base.css                   # Main styles, navbar, sidebar
│   │   ├── cart.css                   # Cart page styles
│   │   ├── dashboard.css              # Dashboard styles
│   │   ├── login.css                  # Login/Register form styles
│   │   ├── orders.css                 # Orders page styles
│   │   └── products.css               # Product listing styles
│   └── images/                        # Static images directory
│
└── templates/                         # Django templates
    ├── base.html                      # Master template (navbar, sidebar)
    │
    ├── accounts/                      # Authentication templates
    │   ├── login.html                 # Login form
    │   └── register.html              # Registration form
    │
    ├── carts/                         # Shopping cart templates
    │   └── cart.html                  # Cart display & checkout
    │
    ├── components/                    # Reusable components
    │   ├── button.html                # Button component
    │   ├── modal.html                 # Modal component
    │   ├── stats_card.html            # Statistics card
    │   └── table.html                 # Table component
    │
    ├── main/                          # Landing & dashboard
    │   ├── dashboard.html             # User dashboard
    │   ├── landing.html               # Homepage
    │   ├── navbar.html                # Navigation bar
    │   └── sidebar.html               # Sidebar navigation
    │
    ├── orders/                        # Order templates
    │   └── order_success.html         # Order confirmation page
    │
    └── products/                      # Product templates
        ├── addCategory.html           # Add category form (admin)
        ├── addProducts.html           # Add product form (admin)
        ├── addTags.html               # Add tags form (admin)
        └── listProducts.html          # Product listing
```

## File Descriptions

### Root Level Files
- **manage.py** - Django management utility for running commands
- **requirements.txt** - Python package dependencies
- **LICENSE** - Project license
- **README.md** - Project documentation
- **PROJECT_NOTES.md** - Quick reference file for project components

### Core Configuration (`core/`)
- **settings.py** - Django settings (database, installed apps, middleware)
- **urls.py** - Main URL router that includes all app URLs
- **wsgi.py** - WSGI application entry point for production
- **asgi.py** - ASGI application entry point for async support

### Apps (`apps/`)

#### Accounts App
- **models.py** - Profile model (extends Django User)
- **views.py** - Login, register, logout views
- **forms.py** - User registration and login forms
- **urls.py** - URL patterns for auth routes
- **admin.py** - Django admin configuration

#### Products App
- **models.py** - Product, Category, Tag models
- **views.py** - Product listing, detail, CRUD operations
- **forms.py** - Product creation/editing forms
- **urls.py** - URL patterns for product routes
- **admin.py** - Django admin configuration

#### Carts App
- **models.py** - Cart (1:1 User), CartItem models
- **views.py** - Add/remove items, cart display
- **urls.py** - URL patterns for cart routes
- **admin.py** - Django admin configuration

#### Orders App
- **models.py** - Order, OrderItem models
- **views.py** - Checkout, order history, order details
- **urls.py** - URL patterns for order routes
- **admin.py** - Django admin configuration

#### Main App
- **views.py** - Landing page, dashboard views
- **urls.py** - URL patterns for main routes

#### Common App
- **models.py** - Shared models used across apps
- **views.py** - Shared utility views

### Static Files (`static/`)
- **css/base.css** - Main stylesheet (navbar, sidebar, layout)
- **css/cart.css** - Shopping cart specific styles
- **css/dashboard.css** - Dashboard specific styles
- **css/login.css** - Login/register form styles
- **css/orders.css** - Orders page styles
- **css/products.css** - Product listing styles

### Templates (`templates/`)
- **base.html** - Master template with navbar and sidebar
- **accounts/** - Login and registration templates
- **products/** - Product browsing and admin templates
- **carts/** - Shopping cart template
- **orders/** - Order confirmation template
- **main/** - Landing page and dashboard templates
- **components/** - Reusable UI components

### Media Files (`media/`)
- **products/** - Uploaded product images
- **profiles/** - Uploaded user profile pictures

### Migrations
Each app includes a `migrations/` folder with database migrations:
- 0001_initial.py - Initial database schema
- Additional migrations for schema updates