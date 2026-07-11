Technical Specification: Fashion E-Shop
1. Project Overview
A modern fashion e-commerce web application for selling stylish clothing and accessories. The application must provide a seamless, SPA-like user experience without full page reloads, built on a robust and secure backend.

2. Tech Stack
LayerTechnologyBackendDjango 5.xFrontend interactivityHTMX + Alpine.jsStylingTailwind CSSDatabasePostgreSQLContainerizationDocker + Docker ComposeWeb serverNginx (reverse proxy)LanguageEnglish (UI + code)

3. Architecture Requirements

SPA-like behavior — all navigation, filtering, cart operations, and form submissions must be handled via HTMX (no full page reloads)
Django serves HTML partials for HTMX requests and full pages for direct URL access
Alpine.js handles local UI state (dropdowns, modals, quantity counters, toggles)
Tailwind CSS via CDN or PostCSS build pipeline
Docker Compose orchestrates: web (Django + Gunicorn), db (PostgreSQL), nginx
Nginx serves static/media files and proxies requests to Gunicorn


4. Application Modules
4.1 Product Catalog

Grid display of products with photo, name, price, category badge
Filtering by category — HTMX-powered, no page reload
Sorting — by price (asc/desc), by newest
Pagination — HTMX-based infinite scroll or paginator
Empty state message when no products match filters

4.2 Product Detail Page

Full product info: images gallery, name, description, price, available sizes, stock status
Size selector (Alpine.js local state)
"Add to Cart" button — HTMX request, updates cart counter in navbar
Related products section

4.3 Shopping Cart (Modal)

Cart accessible from any page via navbar icon
Rendered as a modal window (Alpine.js controls open/close)
Cart contents loaded and updated via HTMX
Operations without page reload:

Change item quantity
Remove item
Display subtotal, total


"Proceed to Checkout" button leads to order creation

4.4 Order Creation

Order form: full name, email, phone, shipping address
Order summary shown alongside the form
On submit — HTMX posts form, Django validates and creates order
Success state rendered as HTMX partial (confirmation message + order number)
Cart cleared after successful order
No payment gateway integration in this scope

4.5 Navigation & Layout

Sticky navbar: logo, category links, cart icon with item count badge
Footer: links, contact info
All navigation links use HTMX hx-boost for SPA-like transitions
Active category highlight


5. Django Project Structure
project/
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
│   ├── partials/       # HTMX partial templates
│   └── ...
├── static/
├── media/
├── docker/
│   ├── nginx/
│   └── ...
├── docker-compose.yml
├── docker-compose.prod.yml
├── Dockerfile
├── requirements.txt
└── .env.example

6. Data Models
Category
id, name, slug, image, created_at
Product
id, category (FK), name, slug, description,
price, sizes (JSON or M2M), stock, images,
is_active, created_at, updated_at
CartItem (session-based, no auth required)
session_key, product (FK), size, quantity
Order
id, full_name, email, phone, address,
total_price, status (pending/confirmed/shipped/delivered),
created_at
OrderItem
id, order (FK), product (FK), size, quantity, price_snapshot

7. Code Quality Requirements

OOP — class-based views throughout (ListView, DetailView, custom View subclasses)
DRY — reusable template partials, mixins for HTMX response detection, shared base views
Security:

CSRF protection on all POST requests (including HTMX)
Input validation via Django Forms / ModelForms
DEBUG=False in production settings
Secret keys and DB credentials via environment variables only
Secure headers via Nginx config (X-Frame-Options, X-Content-Type-Options)
.env never committed — .env.example provided


Mapping — use of DTOs / dataclasses where model data is transformed for views or context
No comments in code
Follow Django best practices: fat models, thin views, reusable apps
requirements.txt pinned versions


8. HTMX Patterns to Apply
TriggerHTMX behaviorCategory filter clickhx-get → returns product grid partial"Add to Cart"hx-post → returns updated cart count + toastCart icon clickhx-get → loads cart modal contentQuantity change in carthx-post → returns updated cart partialRemove from carthx-delete → returns updated cart partialOrder form submithx-post → returns confirmation partial

9. Docker Setup
docker-compose.yml (development):

web: Django dev server, volume-mounted code
db: PostgreSQL with persistent volume
nginx: serves static files

docker-compose.prod.yml (production):

web: Gunicorn
db: PostgreSQL
nginx: reverse proxy + static/media serving + SSL-ready config


10. Environment Variables
DJANGO_SECRET_KEY=
DJANGO_DEBUG=
DJANGO_ALLOWED_HOSTS=
DB_NAME=
DB_USER=
DB_PASSWORD=
DB_HOST=
DB_PORT=

11. Deliverables

 Fully working Django application matching all modules above
 All HTMX interactions working without page reload
 Docker Compose setup for dev and prod
 Nginx configuration file
 README.md with setup, run, and deploy instructions
 .env.example
 Django admin configured for Product/Category/Order management
 Tailwind CSS integrated and applied throughout 