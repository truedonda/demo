# COZYSHOP — Fashion E-Shop

A modern fashion e-commerce web application built with Django 5, HTMX, Alpine.js, and Tailwind CSS.

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Django 5.x |
| Frontend interactivity | HTMX + Alpine.js |
| Styling | Tailwind CSS (CDN) |
| Database | PostgreSQL |
| Containerization | Docker + Docker Compose |
| Web server | Nginx (reverse proxy) |

## Features

- SPA-like navigation with HTMX (no full page reloads)
- Product catalog with category filtering and sorting
- Product detail page with size/color selector (Alpine.js)
- Cart sidebar (session-based, no auth required)
- Checkout with order confirmation
- Django Admin for full content management

## Project Structure

```
cozyshop/
├── config/
│   ├── settings/
│   │   ├── base.py
│   │   ├── development.py
│   │   └── production.py
│   ├── urls.py
│   └── wsgi.py
├── apps/
│   ├── catalog/        # Product, Category models + views
│   ├── cart/           # Cart logic (session-based)
│   └── orders/         # Order model + views
├── templates/
│   ├── base.html
│   ├── partials/
│   ├── catalog/
│   ├── cart/
│   └── orders/
├── docker/
│   └── nginx/
├── docker-compose.yml
├── docker-compose.prod.yml
├── Dockerfile
└── requirements.txt
```

## Setup & Run (Development)

### 1. Clone and configure environment

```bash
cp .env.example .env
# Edit .env with your values
```

### 2. Start with Docker Compose

```bash
docker compose up --build
```

The app will be available at **http://localhost** (via Nginx) or **http://localhost:8000** (direct Django).

### 3. Seed sample data

```bash
docker compose exec web python manage.py seed_data
```

### 4. Create superuser for Admin

```bash
docker compose exec web python manage.py createsuperuser
```

Admin panel: **http://localhost/admin/**

## Deploy (Production)

### 1. Configure environment

```bash
cp .env.example .env
# Set DJANGO_DEBUG=False, strong DJANGO_SECRET_KEY, correct DJANGO_ALLOWED_HOSTS
```

### 2. Add SSL certificates

Place your SSL certificates at:
- `docker/nginx/ssl/fullchain.pem`
- `docker/nginx/ssl/privkey.pem`

### 3. Start production stack

```bash
docker compose -f docker-compose.prod.yml up -d --build
```

## Environment Variables

| Variable | Description | Example |
|---|---|---|
| `DJANGO_SECRET_KEY` | Django secret key | `your-secret-key` |
| `DJANGO_DEBUG` | Debug mode | `False` |
| `DJANGO_ALLOWED_HOSTS` | Comma-separated allowed hosts | `example.com,www.example.com` |
| `DB_NAME` | PostgreSQL database name | `cozyshop` |
| `DB_USER` | PostgreSQL user | `cozyshop` |
| `DB_PASSWORD` | PostgreSQL password | `strongpassword` |
| `DB_HOST` | PostgreSQL host | `db` |
| `DB_PORT` | PostgreSQL port | `5432` |

## Django Admin

After seeding data and creating a superuser, manage your store at `/admin/`:

- **Categories** — create/edit product categories
- **Products** — manage products, upload images, set sizes/colors/stock
- **Orders** — view and update order status
- **Cart Items** — inspect active session carts

## HTMX Interactions

| Trigger | Behavior |
|---|---|
| Category filter click | `hx-get` → returns product grid partial |
| Sort change | `hx-get` → returns product grid partial |
| "Add to Bag" | `hx-post` → updates cart sidebar + count badge |
| Quantity change in cart | `hx-post` → returns updated cart partial |
| Remove from cart | `hx-delete` → returns updated cart partial |
| Order form submit | `hx-post` → returns confirmation partial |
