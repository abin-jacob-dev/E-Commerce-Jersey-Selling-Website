# Campeón Sports E-Commerce Platform

[![Django](https://img.shields.io/badge/Django-6.0.3-green)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![SQLite](https://img.shields.io/badge/SQLite-Database-blue)](https://www.sqlite.org/)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-purple)](https://getbootstrap.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

A comprehensive **E-Commerce Platform** tailored for selling sports jerseys, built with Django. The platform offers a seamless shopping experience for customers and a robust management interface for administrators. It features complete user authentication (including social login), profile and address management, an integrated shopping interface, and a custom administrative dashboard for comprehensive user and store management.

---

## Table of Contents

- [Features](#features)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Installation and Setup](#installation-and-setup)
  - [Prerequisites](#prerequisites)
  - [Step-by-Step Installation](#step-by-step-installation)
  - [Database Setup](#database-setup)
  - [Running the Server](#running-the-server)
- [Application Modules](#application-modules)
  - [Core (Shop)](#core-shop)
  - [User Authentication (`userauths`)](#user-authentication-userauths)
  - [User Profile (`user`)](#user-profile-user)
  - [Admin Panel (`admin_panel`)](#admin-panel-admin_panel)
- [Usage Guide](#usage-guide)
  - [Customer (Regular User)](#customer-regular-user)
  - [Administrator](#administrator)
- [Security Considerations](#security-considerations)
- [Roadmap](#roadmap)
- [Acknowledgements](#acknowledgements)

---

## Features

- **User Authentication (`userauths`)**
  - Sign up with email verification (OTP/Activation Link)
  - Secure login and logout flows
  - Password reset via email
  - Social authentication integrated using `django-allauth` (Google Login)
- **User Profile Management (`user`)**
  - Personalized profile dashboard
  - Update personal details and profile picture upload/removal
  - Address book management (Add, edit, delete, set default address)
  - Secure email and password change functionality
- **E-Commerce Core (`core`)**
  - Interactive Home page
  - Shop catalog for browsing sports jerseys
  - About and Contact pages
- **Custom Admin Dashboard (`admin_panel`)**
  - Separate admin login and authentication
  - Dashboard overview of platform metrics
  - Comprehensive user management (Search, block/unblock, delete users)
- **Security**
  - Custom User model overriding Django's default for email-based authentication
  - Secure route protection and cache control

---

## Technology Stack

- **Backend**: Python 3.x, Django 6.0.3
- **Database**: SQLite (Development) – easily scalable to PostgreSQL
- **Frontend**: HTML, CSS, JavaScript (Bootstrap 5.3)
- **Additional Libraries**: `django-allauth` (Social Auth)

---

## Project Structure

```
E-Commerce-Jersey-Selling-Website/
├── campeon/                 # Main Project Directory
│   ├── campeon/             # Project Configuration (settings.py, urls.py)
│   ├── core/                # Core App (Home, Shop, Contact)
│   ├── user/                # User Profile & Address Management App
│   ├── userauths/           # Authentication App (Login, Signup, Reset)
│   ├── admin_panel/         # Custom Admin Dashboard App
│   ├── media/               # User-uploaded files (Profile pictures)
│   ├── static/              # Global static files (CSS, JS, Images)
│   ├── templates/           # Global HTML templates
│   ├── db.sqlite3           # Local SQLite Database
│   └── manage.py            # Django Management Script
├── .env                     # Environment Variables
└── requirements.txt         # Project Dependencies
```

---

## Installation and Setup

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Virtual environment tool (recommended)

### Step-by-Step Installation

1. **Clone or Download the Project**
   ```bash
   git clone <repository-url>
   cd E-Commerce-Jersey-Selling-Website
   ```

2. **Create and Activate a Virtual Environment**
   ```bash
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Variables**
   Create a `.env` file in the root directory based on the `.env-example` file and configure your secret keys, email settings, and database credentials.

### Database Setup

1. **Apply Migrations**
   Navigate to the directory containing `manage.py` and run:
   ```bash
   cd campeon
   python manage.py makemigrations
   python manage.py migrate
   ```

2. **Create a Superuser (Admin)**
   To access the admin dashboard, create a superuser:
   ```bash
   python manage.py createsuperuser
   ```
   Follow the prompts to set your email, username, and password.

### Running the Server

Start the development server:
```bash
python manage.py runserver
```
The application will be accessible at `http://127.0.0.1:8000/`.

---

## Application Modules

### Core (Shop)
Handles the public-facing storefront.
- **Routes:** `/` (Home), `/shop/` (Product Listing), `/about/`, `/contact/`

### User Authentication (`userauths`)
Manages the lifecycle of user sessions and registrations using a custom User model (`Account`).
- **Routes:** `/signup/`, `/signin/`, `/signout/`, `/reset-password/`, `/activate/`

### User Profile (`user`)
Provides a dashboard for registered users to manage their personal data and shipping addresses.
- **Routes:** `/profile/`, `/edit-profile/`, `/address/`, `/add-address/`, `/change-password/`

### Admin Panel (`admin_panel`)
A secure, custom-built interface for site administrators.
- **Routes:** `/admin_panel/dashboard/`, `/admin_panel/users/` (List & Search), `/admin_panel/block-user/<id>/`

---

## Usage Guide

### Customer (Regular User)
1. Navigate to the Home page and click **Sign Up** to create an account.
2. Verify your email if prompted, then log in.
3. Browse jerseys in the **Shop** section.
4. Visit your **Profile** to update your avatar, change your password, and add shipping addresses.
5. Log out securely when finished.

### Administrator
1. Navigate to `/userauths/signin-admin/` or the designated admin login portal.
2. Enter your superuser credentials.
3. Access the **Dashboard** to view platform metrics.
4. Navigate to **User Management** to search for users, block suspicious accounts, or delete records.
5. Manage products, categories, and orders (as integrated).

---

## Security Considerations

- **Authentication**: Built on Django's robust auth system, enhanced with a custom email-first user model.
- **Social Login**: Secure OAuth2 implementation using `django-allauth`.
- **CSRF & XSS Protection**: Enabled globally via Django middleware; all POST forms include `{% csrf_token %}`.
- **Password Storage**: Passwords are mathematically hashed using Django’s PBKDF2 algorithm.
- **Access Control**: Strict route protection separating regular users from administrative staff.

---

## Roadmap

- Implement complete Shopping Cart and Checkout flow.
- Add payment gateway integrations (Stripe/PayPal/Razorpay).
- Implement order tracking and return management logic.
- Introduce promotional codes and discount systems.
- Expand test coverage and CI/CD pipelines.

---

## Acknowledgements

- [Django Documentation](https://docs.djangoproject.com/)
- [Bootstrap 5](https://getbootstrap.com/)
- [Awesome Readme Templates](https://awesomeopensource.com/project/elangosundar/awesome-README-templates)
- [How to write a Good readme](https://bulldogjob.com/news/449-how-to-write-a-good-readme-for-your-github-project)
