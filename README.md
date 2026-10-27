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

## Demo Credentials

The app comes with seeded demo accounts:

- **Admin**: `admin@morrow.test` / `admin123`
- **Staff**: `staff@morrow.test` / `staff123`

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
