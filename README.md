# Campeón Sports E-Commerce Platform

A comprehensive E-Commerce Platform tailored for selling sports jerseys, built with Django. The platform offers a seamless shopping experience for customers and a robust management interface for administrators. It features complete user authentication, profile and address management, an integrated shopping interface, order management, and a custom administrative dashboard.

## Acknowledgements

- [Django Documentation](https://docs.djangoproject.com/)
- [Bootstrap 5](https://getbootstrap.com/)
- [Awesome Readme Templates](https://awesomeopensource.com/project/elangosundar/awesome-README-templates)
- [How to write a Good readme](https://bulldogjob.com/news/449-how-to-write-a-good-readme-for-your-github-project)

## Route Reference

### Core (Shop)

| Method | Path | Description |
| :--- | :--- | :--- |
| `GET` | `/` | Home page |
| `GET` | `/shop/` | Shop catalog for browsing sports jerseys |
| `GET` | `/contact/` | Contact page |
| `GET` | `/about/` | About page |

### User Authentication

| Method | Path | Description |
| :--- | :--- | :--- |
| `GET/POST` | `/auth/signin/` | User sign in |
| `GET/POST` | `/auth/signup/` | User sign up |
| `GET` | `/auth/signout/` | User sign out |
| `GET/POST` | `/auth/reset-password/` | Reset password |
| `GET/POST` | `/auth/signin-admin/` | Admin sign in |

### User Profile Management

| Method | Path | Description |
| :--- | :--- | :--- |
| `GET/POST` | `/user/profile/` | User profile dashboard |
| `GET/POST` | `/user/edit-profile/` | Edit personal details |
| `GET/POST` | `/user/address/` | Address book management |
| `GET/POST` | `/user/add-address/` | Add a new address |
| `POST` | `/user/set-default-address/<address_id>/` | Set default shipping address |
| `POST` | `/user/delete-address/<id>` | Delete an address |

### Admin Panel

| Method | Path | Description |
| :--- | :--- | :--- |
| `GET` | `/admin-panel/dashboard/` | Dashboard overview of platform metrics |
| `GET` | `/admin-panel/users/` | Comprehensive user management |
| `POST` | `/admin-panel/block-user/<id>/` | Block a user |

### Products & Shopping

| Method | Path | Description |
| :--- | :--- | :--- |
| `GET` | `/products/product-detail/<slug>/` | View product details |
| `GET` | `/products/cart/` | View shopping cart |
| `POST` | `/products/add-to-cart/` | Add product to cart |
| `POST` | `/products/update-cart-quantity/` | Update item quantity in cart |
| `POST` | `/products/remove-from-cart/<item_id>/` | Remove item from cart |
| `GET/POST` | `/products/checkout/` | Checkout process |
| `GET` | `/products/wishlist/` | View wishlist |
| `POST` | `/products/add-to-wishlist/<slug>` | Add product to wishlist |
| `POST` | `/products/wishlist-to-cart/` | Move all wishlist items to cart |
| `GET` | `/products/orders` | View user orders |
| `GET` | `/products/order-details/<order_id>` | View order details |
| `POST` | `/products/cancel-order-item/<item_id>/` | Cancel an order item |

## Appendix

This project uses a custom User model (`Account`) to enforce email-based authentication instead of Django's default username-based authentication.

## Authors

- [@abin-jacob-dev](https://www.github.com/abin-jacob-dev)

## Badges

[![Django](https://img.shields.io/badge/Django-6.0.3-green)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![SQLite](https://img.shields.io/badge/SQLite-Database-blue)](https://www.sqlite.org/)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-purple)](https://getbootstrap.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

## Deployment

To deploy this project to production, ensure you use a production-ready database like PostgreSQL, set `DEBUG=False` in your `.env` file, and serve static files using a web server like Nginx with Gunicorn.

## Environment Variables

To run this project, you will need to add the following environment variables to your `.env` file based on the provided `.env-example`:

`SECRET_KEY`

`DEBUG`

`DB_NAME` (If using a custom DB)

Email settings (e.g., `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`)

## Features

- **User Authentication**: Secure login, signup, password reset, and social auth (`django-allauth`).
- **Profile Management**: Address book, profile picture upload, account settings.
- **E-Commerce**: Product catalog, variant selection (size/color), image zooming.
- **Shopping Flow**: Cart management, wishlist, and secure checkout.
- **Order Management**: View order history, cancel specific order items, and returns.
- **Admin Dashboard**: Custom UI for user, product, category, and order management.

## Installation

Install dependencies and set up the project:

```bash
git clone <repository-url>
cd E-Commerce-Jersey-Selling-Website
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
pip install -r requirements.txt
```
    
## Lessons Learned

Building this project involved deeply understanding Django's authentication system, specifically overriding the default user model for email-based login. Handling product variants (size and colors) and maintaining their relationship with the inventory and cart provided valuable experience in relational database design and complex state management in the backend.

## License

[MIT](https://choosealicense.com/licenses/mit/)

## Roadmap

- Additional browser support & cross-platform optimizations
- Integrate third-party payment gateways (Stripe, Razorpay)
- Advanced analytics for the admin dashboard
- Order tracking system integration

## Run Locally

Clone the project

```bash
  git clone <repository-url>
```

Go to the project directory

```bash
  cd E-Commerce-Jersey-Selling-Website
```

Install dependencies

```bash
  pip install -r requirements.txt
```

Apply database migrations

```bash
  python manage.py makemigrations
  python manage.py migrate
```

Start the server

```bash
  python manage.py runserver
```

## Tech Stack

**Client:** HTML, CSS, JavaScript, Bootstrap 5.3

**Server:** Python 3.8+, Django 6.0.3, SQLite (Development)

## Usage/Examples

To create a superuser for accessing the custom admin panel:

```bash
python manage.py createsuperuser
```

After starting the server, you can access the admin dashboard at `http://127.0.0.1:8000/auth/signin-admin/` or `http://127.0.0.1:8000/admin-panel/dashboard/` once logged in as a superuser.
