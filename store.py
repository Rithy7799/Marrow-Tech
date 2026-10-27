from datetime import datetime
import sqlite3
from pathlib import Path

from flask import render_template, request, session, url_for
from werkzeug.security import generate_password_hash

BASE_DIR = Path(__file__).parent
DATABASE = BASE_DIR / "shop.db"
UPLOAD_DIR = BASE_DIR / "static" / "uploads"
PAGE_SIZE = 20
DEMO_ADMIN_EMAIL = "admin@morrow.test"
DEMO_ADMIN_PASSWORD = "admin123"
DEMO_STAFF_EMAIL = "staff@morrow.test"
DEMO_STAFF_PASSWORD = "staff123"

SEED_PRODUCT_FAMILIES = [
    ("Pulse wireless earbuds", "Noise-aware sound with a pocket-sized charging case.", "Audio", 59.00, "#d8f2df", "PW"),
    ("Orbit smart watch", "A focused daily dashboard for movement and messages.", "Wearables", 129.00, "#c7ebd2", "OS"),
    ("Volt power bank", "Fast USB-C charging for the days that run long.", "Power", 39.00, "#e1f5e6", "VP"),
    ("Beam mini projector", "Turn any blank wall into a bigger night in.", "Entertainment", 189.00, "#b9e5c7", "BM"),
    ("Key mechanical keyboard", "Tactile, compact, and built for long sessions.", "Workspace", 84.00, "#d0efda", "KM"),
    ("Loop portable speaker", "Room-filling sound in a carry-anywhere shell.", "Audio", 74.00, "#c3ebcf", "LS"),
]
SEED_PRODUCTS = [
    (f"{name} {edition:02d}", description, category, price + ((edition - 1) % 5) * 3, color, initials)
    for edition in range(1, 18)
    for name, description, category, price, color, initials in SEED_PRODUCT_FAMILIES
][:100]


def get_db():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    connection = get_db()
    connection.executescript("""
        CREATE TABLE IF NOT EXISTS products (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, description TEXT NOT NULL, category TEXT NOT NULL, price REAL NOT NULL, color TEXT NOT NULL, initials TEXT NOT NULL, created_at TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS orders (id INTEGER PRIMARY KEY AUTOINCREMENT, customer_name TEXT NOT NULL, email TEXT NOT NULL, address TEXT NOT NULL, items TEXT NOT NULL, total REAL NOT NULL, status TEXT NOT NULL DEFAULT 'New', created_at TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, email TEXT NOT NULL UNIQUE, password TEXT NOT NULL, created_at TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS favorites (user_id INTEGER NOT NULL, product_id INTEGER NOT NULL, PRIMARY KEY (user_id, product_id));
        CREATE TABLE IF NOT EXISTS reviews (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL, product_id INTEGER NOT NULL, rating INTEGER NOT NULL, comment TEXT NOT NULL, created_at TEXT NOT NULL);
    """)
    connection.execute("CREATE TABLE IF NOT EXISTS categories (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL UNIQUE, created_at TEXT NOT NULL)")
    product_columns = {row[1] for row in connection.execute("PRAGMA table_info(products)").fetchall()}
    for column in ("image1", "image2", "image3"):
        if column not in product_columns:
            connection.execute(f"ALTER TABLE products ADD COLUMN {column} TEXT")
    user_columns = {row[1] for row in connection.execute("PRAGMA table_info(users)").fetchall()}
    for column, definition in {"role": "TEXT NOT NULL DEFAULT 'customer'", "avatar": "TEXT", "phone": "TEXT", "address": "TEXT", "card_name": "TEXT", "card_last4": "TEXT", "card_expiry": "TEXT"}.items():
        if column not in user_columns:
            connection.execute(f"ALTER TABLE users ADD COLUMN {column} {definition}")
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    count = connection.execute("SELECT COUNT(*) FROM products").fetchone()[0]
    if count == 0:
        if not connection.execute("SELECT 1 FROM users WHERE role = 'admin' LIMIT 1").fetchone():
            connection.execute("INSERT OR IGNORE INTO users (name, email, password, role, created_at) VALUES (?, ?, ?, ?, ?)", ("Morrow Admin", DEMO_ADMIN_EMAIL, generate_password_hash(DEMO_ADMIN_PASSWORD), "admin", datetime.now().isoformat(timespec="seconds")))
        if not connection.execute("SELECT 1 FROM users WHERE email = ?", (DEMO_STAFF_EMAIL,)).fetchone():
            connection.execute("INSERT INTO users (name, email, password, role, created_at) VALUES (?, ?, ?, ?, ?)", ("Morrow Staff", DEMO_STAFF_EMAIL, generate_password_hash(DEMO_STAFF_PASSWORD), "user", datetime.now().isoformat(timespec="seconds")))
        now = datetime.now().isoformat(timespec="seconds")
        connection.executemany("INSERT INTO products (name, description, category, price, color, initials, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)", [product + (now,) for product in SEED_PRODUCTS])
    connection.execute("INSERT OR IGNORE INTO categories (name, created_at) SELECT DISTINCT category, datetime('now') FROM products WHERE TRIM(category) != ''")
    connection.commit()
    connection.close()


def admin_access_required():
    user = session.get("user")
    if not user:
        return render_template("auth.html", mode="login", error="Please log in to access the admin desk."), 302
    if user.get("role") not in {"admin", "user"}:
        return render_template("access_denied.html"), 403
    return None


def owner_admin_required():
    access_error = admin_access_required()
    if access_error:
        return access_error
    if session["user"].get("role") != "admin":
        return render_template("access_denied.html"), 403
    return None


def currency(value):
    return f"${value:,.2f}"


def current_user_context():
    user = session.get("user")
    notifications = []
    if user:
        connection = get_db()
        account = connection.execute("SELECT id, name, email, role, avatar FROM users WHERE id = ?", (user["id"],)).fetchone()
        if account:
            user = dict(account)
        notifications = connection.execute("SELECT id, total, status, created_at FROM orders WHERE email = ? ORDER BY id DESC LIMIT 5", (user["email"],)).fetchall()
        connection.close()
    return {"current_user": user, "notifications": notifications}
