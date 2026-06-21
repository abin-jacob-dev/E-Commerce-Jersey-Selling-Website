# Campeon — Sports Jersey E-Commerce Platform

A production-grade e-commerce platform purpose-built for selling sports jerseys, engineered with Django's MVT architecture, PostgreSQL, and a modern frontend stack. Designed for scale, security, and operational clarity.

---

## Demo

> 🎬 *A live demo is available at the production URL below. Screen recordings and GIFs can be added to showcase the shopping flow, admin dashboard, and payment process.*

| Environment | URL |
| :--- | :--- |
| Production | `https://your-production-domain.com` |
| Local | `http://127.0.0.1:8000` |

---

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                    CLIENT LAYER                      │
│  HTML · CSS · JavaScript · Bootstrap 5.3 · Tailwind │
├─────────────────────────────────────────────────────┤
│                  DJANGO MVT LAYER                    │
│  Templates ← Views ← URL Routing ← Context Procs   │
├─────────────────────────────────────────────────────┤
│                   SERVICE LAYER                      │
│  WalletService · OfferService · PaymentService      │
├─────────────────────────────────────────────────────┤
│                   DATA LAYER                         │
│  PostgreSQL · Cloudinary (Media)                    │
├─────────────────────────────────────────────────────┤
│                EXTERNAL SERVICES                     │
│  Razorpay (Payments) · Google OAuth · SMTP (Email)  │
└─────────────────────────────────────────────────────┘
```

### Project Structure

```
E-Commerce-Jersey-Selling-Website/
├── campeon/                    # Django project root
│   ├── campeon/               # Project settings & configuration
│   │   ├── settings.py        # Central configuration
│   │   ├── urls.py            # Root URL dispatcher
│   │   ├── wsgi.py            # WSGI entry point
│   │   └── asgi.py            # ASGI entry point
│   ├── core/                  # Landing pages (Home, Shop, About, Contact)
│   ├── userauths/             # Authentication, OTP, Social Login
│   ├── user/                  # Profile, Addresses, Wallet, Referrals
│   ├── products/              # Catalog, Cart, Wishlist, Orders, Offers, Coupons
│   ├── payment/               # Razorpay payment processing & verification
│   ├── admin_panel/           # Custom admin dashboard & sales reports
│   ├── templates/             # Django HTML templates (organized by app)
│   ├── static/                # Static assets (CSS, JS, images)
│   ├── manage.py              # Django management script
│   └── requirements.txt       # Python dependencies
├── docs/                      # Project documentation
├── .gitignore
└── README.md
```

---

## Features

- **Authentication & Authorization** — Email-based signup/login, OTP verification, password reset, Google OAuth via `django-allauth`, custom `user_login_required` decorator with block-check
- **Product Catalog** — Category management, product CRUD, variant system (S/M/L/XL/XXL), SKU generation, Cloudinary-hosted images, stock tracking
- **Smart Offers** — Product-level and category-level offer engine with automatic best-discount selection, percentage and fixed-amount discount types, date-range validation
- **Coupon System** — Percentage/fixed coupons with minimum purchase thresholds, single-use enforcement, session-based apply/remove flow
- **Shopping Flow** — Cart with quantity limits (1-5), wishlist with bulk cart transfer, multi-step checkout, address selection
- **Payment Processing** — Razorpay integration with server-side signature verification, Cash on Delivery, Wallet payments, payment failure handling
- **Wallet System** — Auto-created per user, atomic debit/credit via `WalletService`, transaction history with source tracking (order payment / refund)
- **Order Management** — Granular item-level status tracking (pending → processing → shipped → delivered), cancel/return requests per item, partial cancellation and return support
- **Invoice Generation** — PDF invoice export via WeasyPrint/ReportLab for completed orders
- **Referral Program** — Unique referral codes, wallet credit on successful referral signup, referral dashboard
- **Admin Dashboard** — Custom admin panel with user management (block/unblock), sales reports (daily/monthly/yearly), top products & categories analytics, Excel & PDF export
- **User Profile** — Profile editing, photo upload/removal, email change, password change, address book with default address support

---

## Tech Stack

| Layer | Technology | Version |
| :--- | :--- | :--- |
| **Language** | Python | 3.8+ |
| **Framework** | Django | 6.0.5 |
| **Database** | PostgreSQL | 14+ |
| **Auth** | django-allauth | 65.16.1 |
| **Media** | Cloudinary | 1.44.2 |
| **Payments** | Razorpay | 2.0.1 |
| **PDF Generation** | WeasyPrint | 68.1 |
| **PDF Generation** | ReportLab | 4.5.1 |
| **Excel Export** | openpyxl | 3.1.5 |
| **Image Processing** | Pillow | 12.2.0 |
| **HTML Parsing** | lxml | 6.1.1 |
| **Frontend** | Bootstrap 5.3, Tailwind CSS | — |

---

## Deployment

### Production Deployment

```bash
# Set production environment
export DEBUG=False
export SECRET_KEY=<your-production-secret-key>

# Database — use managed PostgreSQL (AWS RDS, Neon, Supabase)
export DB_NAME=<database_name>
export DB_USER=<database_user>
export DB_PASSWORD=<database_password>
export DB_HOST=<database_host>
export DB_PORT=5432

# Apply migrations
python manage.py migrate --noinput

# Collect static files
python manage.py collectstatic --noinput

# Start with Gunicorn (behind Nginx)
gunicorn campeon.wsgi:application --bind 0.0.0.0:8000 --workers 4
```

> **Note:** A `Dockerfile` stub exists at `campeon/Dockerfile` but is not yet configured. For containerized deployment, write a Dockerfile using `python:3.13-slim` as the base image and follow the [Django Docker deployment guide](https://docs.djangoproject.com/en/6.0/howto/deployment/docker/).

### Production Checklist

| Area | Action |
| :--- | :--- |
| **DEBUG** | Set to `False` — never run with debug in production |
| **SECRET_KEY** | Generate a new, unique key; store in environment variable |
| **ALLOWED_HOSTS** | Set to your production domain(s) |
| **HTTPS** | Enforce `SECURE_SSL_REDIRECT=True`, `SESSION_COOKIE_SECURE=True` |
| **HSTS** | Enable `SECURE_HSTS_SECONDS=31536000` |
| **Static Files** | Serve via Nginx or WhiteNoise; configure `STATIC_ROOT` |
| **Media Files** | Cloudinary handles production media storage |
| **Database** | Use managed PostgreSQL; restrict connections to app server only |
| **Admin** | Change default `/admin/` URL; enable MFA |
| **Email** | Configure production SMTP (SendGrid, Mailgun, AWS SES) |

---

## Environment Variables

Configure your `.env` file based on `.env.example`:

```env
# ──────────────────────────────────────────────
# Django Core
# ──────────────────────────────────────────────
SECRET_KEY=your-256-bit-secret-key
DEBUG=True

# ──────────────────────────────────────────────
# PostgreSQL Database
# ──────────────────────────────────────────────
DB_NAME=campeon_db
DB_USER=campeon_user
DB_PASSWORD=secure_password_here
DB_HOST=127.0.0.1
DB_PORT=5432

# ──────────────────────────────────────────────
# Email / SMTP
# ──────────────────────────────────────────────
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
EMAIL_USE_TLS=True

# ──────────────────────────────────────────────
# Google OAuth (django-allauth)
# ──────────────────────────────────────────────
client_id=your-google-client-id
client_secret=your-google-client-secret

# ──────────────────────────────────────────────
# Cloudinary (Media Storage)
# ──────────────────────────────────────────────
CLOUDINARY_URL=cloudinary://api_key:api_secret@cloud_name

# ──────────────────────────────────────────────
# Razorpay (Payments)
# ──────────────────────────────────────────────
RAZOR_KEY_ID=rzp_test_xxxxxxxxxxxxx
RAZOR_KEY_SECRET=your-razorpay-secret
```

| Variable | Required | Description |
| :--- | :--- | :--- |
| `SECRET_KEY` | ✅ | Django secret key for cryptographic signing |
| `DEBUG` | ✅ | `True` for development, `False` for production |
| `DB_NAME` | ✅ | PostgreSQL database name |
| `DB_USER` | ✅ | PostgreSQL username |
| `DB_PASSWORD` | ✅ | PostgreSQL password |
| `DB_HOST` | ✅ | Database host (default: `127.0.0.1`) |
| `DB_PORT` | ❌ | Database port (default: `5432`) |
| `EMAIL_HOST` | ✅ | SMTP server hostname |
| `EMAIL_PORT` | ✅ | SMTP port (typically `587`) |
| `EMAIL_HOST_USER` | ✅ | SMTP authentication username |
| `EMAIL_HOST_PASSWORD` | ✅ | SMTP authentication password |
| `EMAIL_USE_TLS` | ✅ | Enable TLS for SMTP (`True`/`False`) |
| `client_id` | ✅ | Google OAuth client ID |
| `client_secret` | ✅ | Google OAuth client secret |
| `CLOUDINARY_URL` | ✅ | Cloudinary connection string |
| `RAZOR_KEY_ID` | ✅ | Razorpay API key ID |
| `RAZOR_KEY_SECRET` | ✅ | Razorpay API secret |

---

## Data Models

### Core Entities

```
Account (Custom User)
├── Addresses (1:N)
├── Wallet (1:1)
│   └── WalletTransaction (1:N)
├── Cart (1:1)
│   └── CartItem (1:N) → Variant
├── Wishlist (N:M) → Variant
├── Orders (1:N)
│   ├── OrderItem (1:N) → Variant, Offer
│   └── → Coupon, Offer
└── Referrals (self-referencing FK)

Category
├── Products (1:N)
│   ├── Variants (1:N) → size, price, stock, SKU
│   │   └── VariantImage (1:N)
│   └── Offers (1:N, optional FK)
└── Offers (1:N, optional FK)

Coupon → code, discount_type, discount_value, min_purchase, date_range

Payment → Order (1:1), razorpay_order_id, razorpay_payment_id, status
```

### Key Model Summary

| Model | Purpose | Key Fields |
| :--- | :--- | :--- |
| `Account` | Custom user with email auth | email, referral_code, is_blocked |
| `Category` | Product categories (soft delete) | name, slug, image (Cloudinary) |
| `Product` | Jersey products | name, slug, category FK |
| `Variant` | Size variants per product | size (S/M/L/XL/XXL), price, stock, SKU |
| `Offer` | Discount promotions | discount_type/value, product/category FK |
| `Coupon` | User-applied coupons | code, min_purchase, date_range |
| `Cart/CartItem` | Shopping cart | user FK, variant FK, quantity (1-5) |
| `Order` | Purchase orders | order_id (auto), payment_method, status |
| `OrderItem` | Individual line items | offer_discount_amount, final_paid_price |
| `Payment` | Razorpay transactions | razorpay IDs, signature, status |
| `Wallet` | User balance | current_balance |
| `WalletTransaction` | Wallet ledger | amount, source, transaction_type |
| `Addresses` | Shipping addresses | address_line, city, state, postal_code |

---

## Route Reference

### Core (Shop)

| Method | Path | Description |
| :--- | :--- | :--- |
| `GET` | `/` | Home page with featured products |
| `GET` | `/shop/` | Full product catalog with filters |
| `GET` | `/contact/` | Contact page |
| `GET` | `/about/` | About page |

### User Authentication

| Method | Path | Description |
| :--- | :--- | :--- |
| `GET/POST` | `/auth/signin/` | User sign in |
| `GET/POST` | `/auth/signup/` | User sign up with OTP verification |
| `GET` | `/auth/signout/` | User sign out |
| `GET/POST` | `/auth/forgot-password/` | Forgot password flow |
| `GET` | `/auth/activate/<uidb64>/<token>/` | Email account activation |
| `GET` | `/auth/activate-account` | Account activation page |
| `GET` | `/auth/reset-password-validate/<uidb64>/<token>/` | Reset password token validation |
| `GET/POST` | `/auth/reset-password/` | Reset password with token |
| `GET/POST` | `/auth/signin-admin/` | Admin sign in |
| `GET` | `/auth/signout-admin/` | Admin sign out |
| `GET` | `/accounts/google/login/` | Google OAuth login |

### User Profile Management

| Method | Path | Description |
| :--- | :--- | :--- |
| `GET` | `/user/profile/` | User profile dashboard |
| `GET/POST` | `/user/edit-profile/` | Edit personal details |
| `POST` | `/user/remove-photo/` | Remove profile photo |
| `GET/POST` | `/user/change-email/` | Change email address |
| `GET/POST` | `/user/change-password/` | Change password |
| `GET` | `/user/address/` | Address book |
| `GET/POST` | `/user/add-address/` | Add new address |
| `GET/POST` | `/user/edit-address/<id>/` | Edit address |
| `POST` | `/user/delete-address/<id>/` | Delete address |
| `POST` | `/user/set-default-address/<id>/` | Set default address |
| `GET` | `/user/wallet/` | Wallet balance & transaction history |
| `GET` | `/user/referral/` | Referral code & stats |

### Products & Shopping

| Method | Path | Description |
| :--- | :--- | :--- |
| `GET` | `/products/all-products` | Product listing with search & filters |
| `GET` | `/products/product-detail/<slug>/` | Product detail with variant selection |
| `GET` | `/products/cart/` | View shopping cart |
| `POST` | `/products/add-to-cart/` | Add product variant to cart |
| `POST` | `/products/update-cart-quantity/` | Update item quantity |
| `POST` | `/products/remove-from-cart/<item_id>/` | Remove item from cart |
| `GET` | `/products/wishlist/` | View wishlist |
| `POST` | `/products/add-to-wishlist/<slug>/` | Add to wishlist |
| `POST` | `/products/remove-from-wishlist/<id>/` | Remove from wishlist |
| `POST` | `/products/clear-wishlist/` | Clear entire wishlist |
| `POST` | `/products/wishlist-to-cart/` | Move all wishlist items to cart |
| `POST` | `/products/wishlist-item-to-cart/<variant_id>/` | Move single item to cart |

### Checkout & Payment

| Method | Path | Description |
| :--- | :--- | :--- |
| `GET/POST` | `/products/checkout/` | Checkout with address selection |
| `GET/POST` | `/products/select-payment/` | Choose payment method |
| `POST` | `/products/verify-payment/` | Razorpay signature verification |
| `GET` | `/products/payment-successful/<order_id>/` | Payment success page |
| `GET` | `/products/payment-failed/<order_id>/` | Payment failure page |

### Orders

| Method | Path | Description |
| :--- | :--- | :--- |
| `GET` | `/products/orders` | User order history |
| `GET` | `/products/order-details/<order_id>` | Order detail view |
| `POST` | `/products/cancel-order-item-request/<item_id>/` | Request item cancellation |
| `POST` | `/products/cancel-order-item/<item_id>/` | Cancel order item |
| `POST` | `/products/return-order-item-request/<item_id>/` | Request item return |
| `POST` | `/products/return-order-item/<item_id>/` | Return order item |
| `GET` | `/products/download-invoice/<order_id>/` | Download PDF invoice |

### Coupons & Offers

| Method | Path | Description |
| :--- | :--- | :--- |
| `POST` | `/products/apply-coupon/` | Apply coupon to cart |
| `POST` | `/products/remove-coupon/` | Remove applied coupon |

### Admin Panel

| Method | Path | Description |
| :--- | :--- | :--- |
| `GET` | `/admin-panel/dashboard/` | Sales dashboard with analytics |
| `GET` | `/admin-panel/users/` | User management with search |
| `POST` | `/admin-panel/block-user/<id>/` | Block/unblock user |
| `GET` | `/products/categories/` | Category management |
| `GET/POST` | `/products/add-new-category/` | Add category |
| `GET/POST` | `/products/edit-category/<slug>/` | Edit category |
| `POST` | `/products/delete-category/<slug>/` | Delete category |
| `GET` | `/products/products-list/` | Product management |
| `GET/POST` | `/products/add-product/` | Add product with variants |
| `GET/POST` | `/products/edit-product/<slug>/` | Edit product |
| `POST` | `/products/delete-product/<slug>/` | Delete product |
| `GET` | `/products/all-orders` | All orders management |
| `GET` | `/products/order-view/<order_id>/` | Admin order detail view |
| `GET` | `/products/coupons/` | Coupon management |
| `GET/POST` | `/products/add-coupon/` | Add coupon |
| `GET/POST` | `/products/edit-coupon/<id>/` | Edit coupon |
| `POST` | `/products/delete-coupon/<id>/` | Delete coupon |
| `GET` | `/products/offers` | Offer management |
| `GET/POST` | `/products/add-offer/` | Add offer |
| `GET/POST` | `/products/edit-offer/<id>/` | Edit offer |
| `POST` | `/products/delete-offer/<id>/` | Delete offer |

---

## Installation

### Prerequisites

- Python 3.8 or higher
- PostgreSQL 14+
- pip (Python package manager)
- Git
- Cloudinary account (for media storage)
- Razorpay account (for payment processing)
- Google Cloud Console project (for OAuth)

### Clone & Setup

```bash
# Clone the repository
git clone https://github.com/abin-jacob-dev/E-Commerce-Jersey-Selling-Website.git
cd E-Commerce-Jersey-Selling-Website

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate        # Linux/macOS
venv\Scripts\activate           # Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp campeon/.env.example campeon/.env
# Edit .env with your credentials

# Navigate to Django project
cd campeon

# Apply database migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser for admin access
python manage.py createsuperuser

# Start development server
python manage.py runserver
```

### Verify Installation

```bash
# Run Django system checks
python manage.py check

# Run in production check mode
python manage.py check --deploy
```

---

## Run Locally

Clone the project

```bash
git clone https://github.com/abin-jacob-dev/E-Commerce-Jersey-Selling-Website.git
```

Go to the project directory

```bash
cd E-Commerce-Jersey-Selling-Website/campeon
```

Install dependencies

```bash
pip install -r requirements.txt
```

Configure environment

```bash
cp .env.example .env
# Edit .env with your database and API credentials
```

Apply migrations and start

```bash
python manage.py migrate
python manage.py runserver
```

Access the application

| URL | Description |
| :--- | :--- |
| `http://127.0.0.1:8000/` | Homepage |
| `http://127.0.0.1:8000/auth/signin/` | User login |
| `http://127.0.0.1:8000/auth/signin-admin/` | Admin login |
| `http://127.0.0.1:8000/admin/` | Django admin (superuser) |

---

## Usage / Examples

### Admin Access

```bash
# Create a superuser
python manage.py createsuperuser

# Start the server
python manage.py runserver
```

Navigate to `http://127.0.0.1:8000/auth/signin-admin/` to access the custom admin dashboard, or `http://127.0.0.1:8000/admin/` for the Django admin panel.

### Key Admin Workflows

| Task | Navigation |
| :--- | :--- |
| Manage products & variants | `/products/products-list/` |
| Create category offers | `/products/add-offer/` |
| Generate coupon codes | `/products/add-coupon/` |
| View sales analytics | `/admin-panel/dashboard/` |
| Export sales reports | `/admin-panel/dashboard/` → Excel/PDF export |
| Block/unblock users | `/admin-panel/users/` |

### User Workflows

| Task | Navigation |
| :--- | :--- |
| Browse products | `/shop/` or `/products/all-products` |
| Add to cart | Product detail → Select size → Add to Cart |
| Apply coupon | Cart → Enter coupon code → Apply |
| Complete purchase | Cart → Checkout → Select address → Payment |
| Track orders | `/products/orders` |
| Download invoice | Order details → Download Invoice |
| Use referral code | Sign up with referral link → Both get wallet credit |

---

## Roadmap

- [ ] Real-time order tracking integration
- [ ] Product review and rating system
- [ ] Advanced search with Elasticsearch
- [ ] Redis caching layer for product catalog
- [ ] Celery background task queue (email, reports)
- [ ] Multi-language support (i18n)
- [ ] Mobile-responsive PWA wrapper
- [ ] Inventory alerts and low-stock notifications
- [ ] A/B testing framework for conversion optimization
- [ ] Webhook-based payment event handling
- [ ] API layer (DRF) for mobile app integration

---

## Optimizations

- **Offer Engine** — `get_best_offer()` computes the optimal discount across product-level and category-level offers, comparing actual savings rather than raw percentages to ensure customers always receive the best price.
- **Atomic Wallet Operations** — `WalletService` uses `transaction.atomic()` with `select_for_update()` to prevent race conditions during concurrent payment and refund operations.
- **Query Optimization** — Strategic use of `select_related()`, `prefetch_related()`, and `only()` throughout views to minimize database round trips. Database indexes on frequently queried fields (`variant.product`, `is_active`, `slug`).
- **Context Processors** — Cart data and summary computed once per request via context processors, eliminating redundant queries across templates.
- **Soft Deletes** — Categories and products use `is_deleted` flags instead of hard deletes, preserving referential integrity and order history.
- **SKU Auto-Generation** — Variant SKUs follow a deterministic format (`CAT{cat_id}-P{prod_id}-{size}`), enabling quick identification without a separate lookup.
- **Session-Based Coupon Tracking** — Coupons stored in session during cart flow, validated server-side at checkout, preventing client-side manipulation.

---

## Lessons Learned

Building Campeón surfaced several hard-won insights about Django e-commerce architecture:

- **Custom User Models Are Non-Negotiable** — Overriding `AbstractBaseUser` for email-based authentication from day one saved months of painful migration work later. The decision to use a custom `Account` model enabled the referral system, wallet integration, and block/unblock functionality without fighting Django's defaults.

- **Variant Systems Are Deceptively Complex** — The relationship between products, variants (size), variant images, and offers required careful schema design. A single product can have 5+ variants, each with its own stock count, pricing, and images. Getting the `unique_together` constraint right on `["product", "size"]` prevented data corruption.

- **Offer Stacking Requires Clear Rules** — Determining whether product-level or category-level offers apply demanded a deterministic comparison algorithm. The `get_best_offer()` function compares actual monetary savings rather than percentage values, which prevents edge cases where a 10% product offer could beat a 20% category offer on expensive items.

- **Payment Verification Must Be Server-Side** — Razorpay signature verification on the backend (never trusting client-side callbacks) is the only safe approach. The payment flow stores `order_id` and `razorpay_order_id` in the session, creating a server-side audit trail.

- **Wallet Refunds Require Atomicity** — Concurrent cancel/return requests on the same order could double-credit a wallet. Wrapping `debit_wallet()` and `credit_wallet()` in `transaction.atomic()` with `select_for_update()` eliminated this race condition entirely.

- **Soft Deletes Preserve Business Data** — Using `is_deleted` flags on categories and products instead of hard deletes ensures that historical order data and analytics remain intact even after catalog cleanup.

---

## About Me

# Hi, I'm Abin! 👋

## 🚀 About Me

I'm a full stack developer passionate about building scalable e-commerce solutions. Campeón represents my deep dive into Django's MVT architecture, complex relational database design, and production-grade payment integration. Every feature — from the atomic wallet system to the multi-level offer engine — was built with real-world reliability in mind.

---

## Acknowledgements

- [Django Documentation](https://docs.djangoproject.com/) — The backbone of this platform
- [django-allauth](https://docs.allauth.org/) — Authentication and social login
- [Razorpay Docs](https://razorpay.com/docs/) — Payment integration reference
- [Cloudinary](https://cloudinary.com/documentation) — Media management and CDN
- [Bootstrap 5](https://getbootstrap.com/) — Frontend component framework
- [Awesome README Templates](https://awesomeopensource.com/project/elangosundar/awesome-README-templates) — Documentation inspiration
- [How to write a Good README](https://bulldogjob.com/news/449-how-to-write-a-good-readme-for-your-github-project) — Writing guidelines

---

## Color Reference

| Color | Hex | Usage |
| :--- | :--- | :--- |
| Primary Dark | ![#0a192f](https://dummyimage.com/10/0a192f/white?text=+) `#0a192f` | Navigation, headers, primary backgrounds |
| Light Surface | ![#f8f8f8](https://dummyimage.com/10/f8f8f8/white?text=+) `#f8f8f8` | Card backgrounds, content areas |
| Accent Green | ![#00b48a](https://dummyimage.com/10/00b48a/white?text=+) `#00b48a` | Success states, CTAs, active elements |
| Accent Light | ![#00d1a0](https://dummyimage.com/10/00d1a0/white?text=+) `#00d1a0` | Hover states, secondary highlights |

---

## Badges

[![Django](https://img.shields.io/badge/Django-6.0.5-092E20?style=for-the-badge&logo=django&logoColor=white)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.8%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14%2B-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-7952B3?style=for-the-badge&logo=bootstrap&logoColor=white)](https://getbootstrap.com/)
[![Razorpay](https://img.shields.io/badge/Razorpay-Payments-07263D?style=for-the-badge&logo=razorpay&logoColor=white)](https://razorpay.com/)
[![Cloudinary](https://img.shields.io/badge/Cloudinary-Media-3448C5?style=for-the-badge&logo=cloudinary&logoColor=white)](https://cloudinary.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)](LICENSE)

---

## License

Distributed under the MIT License. See `LICENSE` for more information.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## Appendix

### Database ERD Summary

```
Account ──1:1──> Cart ──1:N──> CartItem ──N:1──> Variant ──N:1──> Product ──N:1──> Category
Account ──1:N──> Order ──1:N──> OrderItem ──N:1──> Variant
Account ──1:1──> Wallet ──1:N──> WalletTransaction
Account ──1:N──> Addresses
Account ──N:1──> Account (referrals)
Payment ──1:1──> Order
Offer ──N:1──> Product
Offer ──N:1──> Category
Coupon ──N:1──> Order
Wishlist ──N:M──> Variant (through Account)
```

### URL Namespace Mapping

| Namespace | Prefix | App |
| :--- | :--- | :--- |
| `core` | `/` | Core views |
| `userauths` | `/auth/` | Authentication |
| `allauth` | `/accounts/` | Social auth |
| `user` | `/user/` | Profile management |
| `products` | `/products/` | Catalog, cart, orders |
| `payment` | `/payment/` | Payment processing |
| `admin_panel` | `/admin-panel/` | Admin dashboard |

### Key Dependencies

| Package | Purpose |
| :--- | :--- |
| `Django==6.0.5` | Web framework |
| `django-allauth==65.16.1` | Authentication & social login |
| `psycopg2-binary==2.9.12` | PostgreSQL adapter |
| `cloudinary==1.44.2` | Cloud media management |
| `django-cloudinary-storage==0.3.0` | Django-Cloudinary bridge |
| `razorpay==2.0.1` | Payment gateway SDK |
| `weasyprint==68.1` | HTML-to-PDF generation |
| `reportlab==4.5.1` | PDF generation |
| `openpyxl==3.1.5` | Excel file generation |
| `Pillow==12.2.0` | Image processing |
| `lxml==6.1.1` | XML/HTML parsing |
| `python-dotenv==1.2.2` | Environment variable loading |
