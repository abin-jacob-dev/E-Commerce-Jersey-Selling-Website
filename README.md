<div align="center">
  <h1>Campeon Sports E-Commerce Platform</h1>
  <p><strong>A fully-featured sports jersey e-commerce platform built with Django</strong></p>
  <p>
    <a href="#features">Features</a> •
    <a href="#tech-stack">Tech Stack</a> •
    <a href="#installation">Installation</a> •
    <a href="#route-reference">Routes</a> •
    <a href="#environment-variables">Environment</a> •
    <a href="#deployment">Deployment</a>
  </p>
</div>

<p align="center">
  <img alt="Django" src="https://img.shields.io/badge/Django-6.0.5-092E20?style=for-the-badge&logo=django">
  <img alt="Python" src="https://img.shields.io/badge/Python-3.8%2B-3776AB?style=for-the-badge&logo=python">
  <img alt="PostgreSQL" src="https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white">
  <img alt="Bootstrap" src="https://img.shields.io/badge/Bootstrap-5.3-7952B3?style=for-the-badge&logo=bootstrap">
  <img alt="Razorpay" src="https://img.shields.io/badge/Razorpay-02042B?style=for-the-badge&logo=razorpay&logoColor=white">
  <img alt="Cloudinary" src="https://img.shields.io/badge/Cloudinary-3448C5?style=for-the-badge&logo=cloudinary&logoColor=white">
  <img alt="License" src="https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge">
</p>

---

## 📋 Overview

**Campeon** is a comprehensive E-Commerce platform built with **Django 6.0**, designed specifically for selling sports jerseys. It provides a seamless shopping experience for customers and a powerful management interface for administrators.

The platform features complete user authentication (email-based with social login via Google), product catalog management with variants (size/color), a full shopping cart and wishlist system, coupon and offer discount engines, order lifecycle management with cancellations & returns, wallet and referral systems, Razorpay payment integration, and an advanced admin dashboard with sales analytics, PDF/Excel reporting, and user management.

---

## ✨ Features

### 🛍️ Customer-Facing

- **Product Catalog** – Browse sports jerseys with category filtering and search
- **Product Variants** – Size selection (S, M, L, XL, XXL) with per-variant pricing, stock, and images
- **Image Gallery** – Multiple images per variant with click-to-zoom functionality
- **Shopping Cart** – Add/remove items, update quantities, real-time price calculation with offer support
- **Wishlist** – Save items for later, move items to cart individually or in bulk
- **Checkout Flow** – Address selection, coupon application, offer discounts, multiple payment methods
- **User Authentication** – Email-based signup/login, password reset, account activation, Google OAuth (via django-allauth)
- **Profile Management** – Edit personal details, change password, change email, upload/remove profile photo
- **Address Book** – Add, edit, delete, and set default shipping addresses
- **Order Management** – View order history, detailed order view, download invoices (PDF)
- **Order Cancellations** – Request cancellation of individual order items with reason
- **Order Returns** – Request returns for delivered items with reason
- **Wallet System** – View wallet balance and transaction history (credits from refunds/referrals)
- **Referral Program** – Unique referral code for each user, track referrals and earned amounts
- **Coupon Application** – Apply discount coupons at checkout with validation (expiry, min purchase)
- **Offer Discounts** – Automatic best-offer calculation per product/category
- **Payment Methods** – Cash on Delivery (COD), Wallet payment, Razorpay integration

### ⚙️ Admin Panel

- **Dashboard** – Real-time metrics: total sales, order count, user count, delivered orders
- **Sales Analytics** – Monthly/yearly sales charts with top products and categories
- **Sales Reports** – Generate PDF and Excel sales reports with daily/monthly/yearly breakdowns
- **User Management** – View, search, sort, block/unblock, and delete users
- **Product Management** – Add/edit/delete products with variants, images, and categories
- **Category Management** – Create and manage product categories with images
- **Color Management** – Manage available colors for product variants
- **Order Management** – View all orders, update order/item status, manage cancellations and returns
- **Coupon Management** – Create, edit, and delete discount coupons (percentage/fixed)
- **Offer Management** – Create product-level and category-level offers with date ranges
- **Custom Admin Authentication** – Separate admin sign-in page

---

## 🛠️ Tech Stack

### Client (Frontend)
| Technology | Purpose |
|:-----------|:--------|
| **HTML5** | Template structure |
| **CSS3** | Styling and layout |
| **JavaScript** | Client-side interactivity |
| **Bootstrap 5.3** | Responsive UI framework & components |
| **Django Template Engine** | Server-side rendering |

### Server (Backend)
| Technology | Purpose |
|:-----------|:--------|
| **Python 3.8+** | Runtime environment |
| **Django 6.0.5** | Web framework |
| **PostgreSQL** | Production database |
| **SQLite** | Development database (default) |

### Integrations & Services
| Service | Purpose |
|:--------|:--------|
| **Razorpay** | Payment gateway (UPI, cards, netbanking, wallets) |
| **Cloudinary** | Cloud media storage and CDN for product/user images |
| **django-allauth** | Google OAuth social authentication |
| **WeasyPrint** | PDF generation for invoices and sales reports |
| **OpenPyXL** | Excel sales report generation |
| **SMTP (Email)** | Account activation, password reset, and notification emails |

### Key Python Packages
| Package | Version | Usage |
|:--------|:--------|:------|
| `Django` | 6.0.5 | Web framework |
| `django-allauth` | 65.16.1 | Authentication & social auth |
| `cloudinary` | 1.44.2 | Cloud media storage SDK |
| `django-cloudinary-storage` | 0.3.0 | Django storage backend for Cloudinary |
| `razorpay` | 2.0.1 | Payment gateway integration |
| `pillow` | 12.2.0 | Image processing |
| `weasyprint` | 68.1 | PDF generation |
| `openpyxl` | 3.1.5 | Excel file generation |
| `reportlab` | 4.5.1 | Advanced PDF generation |
| `psycopg2-binary` | 2.9.12 | PostgreSQL adapter |
| `python-dotenv` | 1.2.2 | Environment variable management |
| `PyJWT` | 2.13.0 | JSON Web Token support |

---

## 🔐 Environment Variables

Create a `.env` file in the project root with the following variables:

### Django Core
| Variable | Description | Required |
|:---------|:------------|:---------|
| `SECRET_KEY` | Django secret key for cryptographic signing | ✅ Yes |
| `DEBUG` | Set to `True` for development, `False` for production | ✅ Yes |

### Database (PostgreSQL recommended for production)
| Variable | Description | Default | Required |
|:---------|:------------|:--------|:---------|
| `DB_NAME` | PostgreSQL database name | — | ✅ Yes |
| `DB_USER` | Database user | — | ✅ Yes |
| `DB_PASSWORD` | Database password | — | ✅ Yes |
| `DB_HOST` | Database host | `localhost` | ❌ No |
| `DB_PORT` | Database port | `5432` | ❌ No |

### Cloudinary (Media Storage)
| Variable | Description | Required |
|:---------|:------------|:---------|
| `CLOUD_NAME` | Cloudinary cloud name | ✅ Yes |
| `API_KEY` | Cloudinary API key | ✅ Yes |
| `API_SECRET` | Cloudinary API secret | ✅ Yes |

### Email (SMTP)
| Variable | Description | Required |
|:---------|:------------|:---------|
| `EMAIL_HOST` | SMTP server host | ✅ Yes |
| `EMAIL_PORT` | SMTP server port | ✅ Yes |
| `EMAIL_HOST_USER` | SMTP username/email | ✅ Yes |
| `EMAIL_HOST_PASSWORD` | SMTP password/app password | ✅ Yes |
| `EMAIL_USE_TLS` | Whether to use TLS (e.g., `True`) | ✅ Yes |

### Razorpay (Payment Gateway)
| Variable | Description | Required |
|:---------|:------------|:---------|
| `RAZOR_KEY_ID` | Razorpay API key ID | ✅ Yes |
| `RAZOR_KEY_SECRET` | Razorpay API key secret | ✅ Yes |

---

## 📦 Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Virtual environment (recommended)
- PostgreSQL (for production) or SQLite (for development)
- Git

### Step 1: Clone the Repository

```bash
git clone https://github.com/abin-jacob-dev/E-Commerce-Jersey-Selling-Website.git
cd E-Commerce-Jersey-Selling-Website
```

### Step 2: Create and Activate a Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate it
# On Linux/macOS:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install -r campeon/requirements.txt
```

> **Note:** The project has requirements file (`requirements.txt`). The main `requirements.txt` file at `campeon/requirements.txt` contains the complete and most up-to-date list of dependencies and will install everything needed.

### Step 4: Configure Environment Variables

Copy the example environment file and fill in your values:

```bash
cp .env.example .env
```

Then edit `.env` with your configuration (see [Environment Variables](#-environment-variables) section above).

### Step 5: Apply Database Migrations

```bash
cd campeon
python manage.py makemigrations
python manage.py migrate
```

### Step 6: Create a Superuser

```bash
python manage.py createsuperuser
```

You will be prompted to enter `full_name`, `username`, `email`, and `password`.

### Step 7: Collect Static Files

```bash
python manage.py collectstatic
```

### Step 8: Start the Development Server

```bash
python manage.py runserver
```

The application will be available at **http://127.0.0.1:8000/**.

---

## 🚀 Deployment

### Production Checklist

1. **Database** – Switch from SQLite to PostgreSQL for production
2. **Debug Mode** – Set `DEBUG=False` in your `.env` file
3. **Secret Key** – Use a strong, unique `SECRET_KEY` (generate one using `python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'`)
4. **Allowed Hosts** – Update `ALLOWED_HOSTS` in `settings.py` with your domain
5. **Static Files** – Serve static files via a web server (Nginx) or CDN
6. **Media Files** – Cloudinary handles media storage, so no local media server needed
7. **Web Server** – Use Gunicorn or uWSGI as the WSGI server behind Nginx
8. **HTTPS** – Enable HTTPS with SSL/TLS certificates (Let's Encrypt)
<!-- 
### Example Production Setup (Nginx + Gunicorn)

```bash
# Install Gunicorn
pip install gunicorn

# Run Gunicorn
gunicorn campeon.wsgi:application --bind 0.0.0.0:8000 --workers 4
```

```nginx
# Nginx configuration
server {
    listen 80;
    server_name yourdomain.com;

    location /static/ {
        alias /path/to/staticfiles/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

--- -->

## 🧪 Usage

### Customer Flow

1. **Browse** – Visit the home page or `/shop/` to browse jerseys by category
2. **Select** – Click a product to view details, select size, and see available images
3. **Add to Cart** – Choose quantity and add items to your shopping cart
4. **Wishlist** – Save items for later or move them to cart
5. **Checkout** – Proceed to checkout, select or add a shipping address
6. **Apply Coupon** – Enter a coupon code if you have one
7. **Pay** – Choose payment method (COD, Wallet, or Razorpay)
8. **Track** – View order history and track status from your profile

### Admin Flow

1. **Sign In** – Visit `/auth/signin-admin/` and log in with superuser credentials
2. **Dashboard** – View sales metrics, top products, and category performance at `/admin-panel/dashboard/`
3. **Manage Products** – Add/edit products with variants and images
4. **Manage Orders** – View all orders, update statuses, handle cancellations/returns
5. **Marketing** – Create coupons and offers to drive sales
6. **User Management** – View, search, and block/unblock users
7. **Sales Reports** – Generate PDF or Excel sales reports with date filtering

---

## 📊 Admin Dashboard Features

The admin dashboard at `/admin-panel/dashboard/` provides:

- **Summary Cards** – Total sales, total orders, total users, delivered orders
- **Filter Toggle** – Switch between monthly and yearly views
- **Sales Chart** – Visual bar chart showing revenue trends (12 months or 5 years)
- **Top Products** – Top 10 best-selling products ranked by quantity sold
- **Top Categories** – Top 10 best-selling categories ranked by quantity sold

### Sales Reporting

The sales report page (`/admin-panel/sales/`) supports:

- **Daily/Monthly/Yearly/Custom** date range filtering
- **Detailed breakdown** – Orders count, total sales, offer discounts, coupon discounts, net revenue per period
- **PDF Export** – Professionally formatted PDF with `WeasyPrint`
- **Excel Export** – Downloadable `.xlsx` file with `OpenPyXL`, containing summary and breakdown sheets

---
<!-- 
## 💡 Lessons Learned

### Authentication Override
Building this project involved deeply understanding Django's authentication system. We overrode the default `User` model with a custom `Account` model to enforce **email-based authentication** instead of Django's default username-based approach. This required implementing a custom `BaseUserManager` and properly configuring `AUTH_USER_MODEL` in settings.

### Product Variants & Inventory
Handling product variants (sizes) with their own pricing, discount, stock, and images while maintaining relationships with the cart and order system provided valuable experience in **relational database design**. The `Variant` model with its `unique_together` constraint (product + size) prevents data inconsistency, and per-variant SKU auto-generation ensures traceability.

### Offer & Coupon Engine
Implementing a flexible discount system that supports both **percentage and fixed-amount discounts** at both the product and category level required careful architecture. The `Offer` model's validation (must belong to exactly one of product or category, date range validation, and discount limits) ensures data integrity. The best-offer calculation logic in `offer_service.py` automatically selects the most beneficial discount for the customer.

### Payment Integration
Integrating **Razorpay** taught us a lot about secure payment flow design: creating orders server-side, generating signatures, and verifying callbacks to prevent tampering. Supporting multiple payment methods (COD, Wallet, Razorpay) alongside the payment gateway required careful state management.

### PDF & Report Generation
Using **WeasyPrint** for PDF invoices and **OpenPyXL** for Excel reports gave insight into server-side document generation. The sales report feature especially demonstrates how to aggregate and present complex query data in downloadable formats.

### Admin Panel Design
Creating a custom admin panel alongside Django's built-in admin provided experience in building **admin-specific authentication** (separate sign-in), role-based access control (superuser_required decorator), and data visualization within Django templates.

--- -->
<!-- 
## 🗺️ Roadmap

- [ ] **Additional Payment Gateways** – Integrate Stripe, PayPal, and additional regional payment providers
- [ ] **Advanced Analytics** – Enhanced admin dashboard with predictive sales trends, customer segmentation, and churn analysis
- [ ] **Order Tracking** – Real-time order tracking with shipment integration (Shiprocket, Delhivery, etc.)
- [ ] **Mobile App** – React Native or Flutter companion app
- [ ] **Multi-Language Support** – i18n for regional language support
- [ ] **Progressive Web App (PWA)** – Offline capability and installable web app
- [ ] **Email Notifications** – Automated order confirmation, shipping updates, and promotional emails
- [ ] **Reviews & Ratings** – Customer product reviews with image uploads
- [ ] **Inventory Alerts** – Low-stock notifications for admin
- [ ] **Bulk Import/Export** – CSV/Excel import for products and variants

--- -->

## 👥 Authors

- **[@abin-jacob-dev](https://www.github.com/abin-jacob-dev)** – Full-stack developer and project maintainer

---
<!-- 
## 🙏 Acknowledgements

- [Django Documentation](https://docs.djangoproject.com/) – The excellent Django framework and its comprehensive documentation
- [Bootstrap 5](https://getbootstrap.com/) – Responsive UI components and grid system
- [Razorpay](https://razorpay.com/) – Payment gateway integration
- [Cloudinary](https://cloudinary.com/) – Media storage and CDN
- [django-allauth](https://django-allauth.readthedocs.io/) – Social authentication made easy
- [WeasyPrint](https://weasyprint.org/) – PDF generation library
- [OpenPyXL](https://openpyxl.readthedocs.io/) – Excel file generation
- [Awesome Readme Templates](https://awesomeopensource.com/project/elangosundar/awesome-README-templates) – README inspiration
- [How to write a Good Readme](https://bulldogjob.com/news/449-how-to-write-a-good-readme-for-your-github-project) – README best practices

---

## 📄 License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for more details.

--- -->

## ⚙️ Project Structure

```
E-Commerce-Jersey-Selling-Website/
├── campeon/
│   ├── campeon/                    # Django project settings
│   │   ├── settings.py            # Main configuration (DB, auth, cloudinary, etc.)
│   │   ├── urls.py                # Root URL configuration
│   │   ├── asgi.py                # ASGI entry point
│   │   └── wsgi.py                # WSGI entry point
│   ├── core/                       # Core app (home, shop, contact, about)
│   ├── userauths/                  # User authentication app
│   ├── user/                       # User profile management app
│   ├── admin_panel/                # Custom admin dashboard app
│   ├── products/                   # Products, cart, orders, coupons, offers app
│   ├── payment/                    # Payment processing app
│   ├── templates/                  # HTML templates
│   │   ├── admin/                  # Admin panel templates
│   │   ├── user/                   # User profile templates
│   │   ├── userauths/              # Authentication templates
│   │   ├── products/               # Product, cart, checkout templates
│   │   ├── core/                   # Core page templates
│   │   └── partials/               # Reusable template partials
│   ├── static/                     # Static files (CSS, JS, images)
│   ├── manage.py                   # Django CLI entry point
│   └── requirements.txt           # Full dependencies (duplicate of main)
├── .env.example                    # Environment variable template
├── .gitignore
└── README.md
```

---

<div align="center">
  <br>
  <p>Built with ❤️ by <a href="https://www.github.com/abin-jacob-dev">@abin-jacob-dev</a></p>
  <p>
    <a href="https://github.com/abin-jacob-dev/E-Commerce-Jersey-Selling-Website/issues">Report Bug</a>
    •
    <a href="https://github.com/abin-jacob-dev/E-Commerce-Jersey-Selling-Website/issues">Request Feature</a>
  </p>
</div>
