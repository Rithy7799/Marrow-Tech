# Marrow Tech

A modern Flask-based e-commerce web application for browsing, shopping, and managing tech products. Features a complete storefront with user authentication, shopping cart functionality, product reviews, favorites, and an admin dashboard.

## Features

### For Customers
- **Product Storefront** - Browse products by category with search and filtering
- **Product Details** - View product information, images, and customer reviews
- **Shopping Cart & Checkout** - Add products to cart and complete orders
- **User Accounts** - Register, login, and manage your profile
- **Favorites** - Save products to your favorites list
- **Reviews** - Leave ratings and comments on products
- **Notifications** - View order updates and notifications
- **Responsive Design** - Mobile-friendly interface

### For Admins/Staff
- **Admin Dashboard** - Overview of products, orders, and customers
- **Product Management** - Add, edit, and delete products
- **Order Management** - Update order status
- **Customer Management** - Create and manage customer accounts

## Tech Stack

- **Backend**: Flask (Python)
- **Database**: SQLite
- **Frontend**: HTML, CSS, JavaScript (Jinja2 templates)
- **Authentication**: Werkzeug password hashing
- **File Uploads**: Support for product images

## Installation

### Prerequisites
- Python 3.8+
- pip

### Setup

1. Clone the repository:
```bash
git clone https://github.com/Rithy7799/Marrow-Tech.git
cd Marrow-Tech
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the application:
```bash
python app.py
```

5. Open your browser and navigate to `http://127.0.0.1:8555`

## Development Demo Credentials

Demo accounts and sample products are seeded into an empty database during local development:

- **Admin**: `admin@morrow.test` / `admin123`
- **Staff**: `staff@morrow.test` / `staff123`

Demo data is disabled when `APP_ENV=production`.

## Production Deployment

The included `Procfile` runs the app with Gunicorn on a Linux host or platform that supports Procfiles. Configure these environment variables in the host's dashboard:

- `APP_ENV=production`
- `SECRET_KEY` — a long, random value. Generate one with `python -c "import secrets; print(secrets.token_hex(32))"` and keep it out of source control.
- `DATABASE_PATH` — an absolute path on a persistent disk, such as `/data/shop.db`.
- `PORT` — normally supplied by the hosting platform; the Procfile defaults to `8000`.

Keep the directory `static/uploads` on persistent storage too; product images and profile photos are saved there. Back up the database and uploads together. For a fresh production database, run `flask --app app create-admin` as a one-off command after configuring the environment and persistent disk. The command prompts for the administrator's name, email, and a password of at least 12 characters. Add products and categories from the admin desk after signing in.

When moving an existing store, copy its database and `static/uploads` contents to the host's persistent storage before starting the service. Before making it public, replace or remove any development demo accounts in that database—the documented demo passwords are public. Enforce HTTPS at the hosting platform or reverse proxy; production session cookies are marked secure.

## Project Structure

```
Marrow-Tech/
├── app.py              # Main application entry point
├── store.py            # Database models, utilities, and seeding
├── requirements.txt    # Python dependencies
├── routes/             # Route blueprints
│   ├── admin.py        # Admin dashboard routes
│   ├── auth.py         # Authentication routes
│   └── front.py        # Frontend/storefront routes
├── static/             # Static assets (CSS, JS, images)
├── templates/          # Jinja2 HTML templates
└── shop.db             # SQLite database (auto-created)
```

## Database

The application uses SQLite and automatically initializes the database on first run with:
- Products (seeded with sample tech products)
- Users (with roles: customer, staff, admin)
- Orders
- Favorites
- Reviews
- Categories

## License

This project is open source and available under the MIT License.
