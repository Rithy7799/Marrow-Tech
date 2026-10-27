from datetime import datetime
import sqlite3
from pathlib import Path
from flask import Blueprint, redirect, render_template, request, session, url_for
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename
from store import PAGE_SIZE, UPLOAD_DIR, admin_access_required, owner_admin_required, get_db

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

@admin_bp.route("")
def dashboard():
    access_error = admin_access_required()
    if access_error: return access_error
    connection = get_db()
    product_count = connection.execute("SELECT COUNT(*) FROM products").fetchone()[0]
    order_count = connection.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
    category_count = connection.execute("SELECT COUNT(*) FROM categories").fetchone()[0]
    can_manage_users = session["user"].get("role") == "admin"
    user_count = connection.execute("SELECT COUNT(*) FROM users").fetchone()[0] if can_manage_users else 0
    active_view = request.args.get("view", "products")
    if active_view not in {"products", "categories", "orders", "users"} or (active_view == "users" and not can_manage_users):
        active_view = "products"
    view_counts = {"products": product_count, "categories": category_count, "orders": order_count, "users": user_count}
    page_names = {"products": "products_page", "categories": "categories_page", "orders": "orders_page", "users": "users_page"}
    view_pages = {}
    for view, count in view_counts.items():
        total_pages = max(1, (count + PAGE_SIZE - 1) // PAGE_SIZE)
        view_pages[view] = min(max(request.args.get(page_names[view], 1, type=int), 1), total_pages)
    products = connection.execute("SELECT * FROM products ORDER BY id DESC LIMIT ? OFFSET ?", (PAGE_SIZE, (view_pages["products"] - 1) * PAGE_SIZE)).fetchall()
    categories = connection.execute("SELECT categories.id, categories.name, COUNT(products.id) AS product_count FROM categories LEFT JOIN products ON products.category = categories.name GROUP BY categories.id ORDER BY categories.name LIMIT ? OFFSET ?", (PAGE_SIZE, (view_pages["categories"] - 1) * PAGE_SIZE)).fetchall()
    orders = connection.execute("SELECT * FROM orders ORDER BY id DESC LIMIT ? OFFSET ?", (PAGE_SIZE, (view_pages["orders"] - 1) * PAGE_SIZE)).fetchall()
    users = connection.execute("SELECT id, name, email, role, created_at FROM users ORDER BY id DESC LIMIT ? OFFSET ?", (PAGE_SIZE, (view_pages["users"] - 1) * PAGE_SIZE)).fetchall() if can_manage_users else []
    revenue = connection.execute("SELECT COALESCE(SUM(total), 0) FROM orders WHERE status != 'Cancelled'").fetchone()[0]
    connection.close()
    page_data = {f"{view}_page": view_pages[view] for view in view_pages}
    page_data.update({f"{view}_total_pages": max(1, (view_counts[view] + PAGE_SIZE - 1) // PAGE_SIZE) for view in view_counts})
    return render_template("admin.html", products=products, product_count=product_count, orders=orders, order_count=order_count, categories=categories, category_count=category_count, users=users, user_count=user_count, active_view=active_view, can_manage_users=can_manage_users, revenue=revenue, **page_data)

@admin_bp.route("/products")
def products():
    access_error = admin_access_required()
    if access_error: return access_error
    connection = get_db()
    query = request.args.get("q", "").strip()
    page = max(request.args.get("page", 1, type=int), 1)
    if query:
        values = tuple(f"%{query}%" for _ in range(3))
        product_count = connection.execute("SELECT COUNT(*) FROM products WHERE name LIKE ? OR description LIKE ? OR category LIKE ?", values).fetchone()[0]
    else:
        product_count = connection.execute("SELECT COUNT(*) FROM products").fetchone()[0]
        values = ()
    total_pages = max(1, (product_count + PAGE_SIZE - 1) // PAGE_SIZE)
    page = min(page, total_pages)
    offset = (page - 1) * PAGE_SIZE
    if query:
        rows = connection.execute("SELECT * FROM products WHERE name LIKE ? OR description LIKE ? OR category LIKE ? ORDER BY id DESC LIMIT ? OFFSET ?", values + (PAGE_SIZE, offset)).fetchall()
    else:
        rows = connection.execute("SELECT * FROM products ORDER BY id DESC LIMIT ? OFFSET ?", (PAGE_SIZE, offset)).fetchall()
    category_count = connection.execute("SELECT COUNT(*) FROM categories").fetchone()[0]
    categories_total_pages = max(1, (category_count + PAGE_SIZE - 1) // PAGE_SIZE)
    categories_page = min(max(request.args.get("categories_page", 1, type=int), 1), categories_total_pages)
    categories = connection.execute("SELECT categories.id, categories.name, COUNT(products.id) AS product_count FROM categories LEFT JOIN products ON products.category = categories.name GROUP BY categories.id ORDER BY categories.name LIMIT ? OFFSET ?", (PAGE_SIZE, (categories_page - 1) * PAGE_SIZE)).fetchall()
    connection.close()
    return render_template("admin_products.html", products=rows, query=query, categories=categories, page=page, total_pages=total_pages, product_count=product_count, categories_page=categories_page, categories_total_pages=categories_total_pages, category_count=category_count)

@admin_bp.post("/categories")
def create_category():
    access_error = admin_access_required()
    if access_error: return access_error
    name = request.form.get("name", "").strip()
    if name:
        connection = get_db()
        connection.execute("INSERT OR IGNORE INTO categories (name, created_at) VALUES (?, ?)", (name, datetime.now().isoformat(timespec="seconds")))
        connection.commit()
        connection.close()
    return redirect(url_for("admin.products"))

@admin_bp.post("/categories/<int:category_id>/edit")
def update_category(category_id):
    access_error = admin_access_required()
    if access_error: return access_error
    name = request.form.get("name", "").strip()
    if name:
        connection = get_db()
        category = connection.execute("SELECT name FROM categories WHERE id = ?", (category_id,)).fetchone()
        if category:
            try:
                connection.execute("UPDATE categories SET name = ? WHERE id = ?", (name, category_id))
                connection.execute("UPDATE products SET category = ? WHERE category = ?", (name, category["name"]))
                connection.commit()
            except sqlite3.IntegrityError:
                connection.rollback()
        connection.close()
    return redirect(url_for("admin.products"))

@admin_bp.post("/categories/<int:category_id>/delete")
def delete_category(category_id):
    access_error = admin_access_required()
    if access_error: return access_error
    connection = get_db()
    category = connection.execute("SELECT name FROM categories WHERE id = ?", (category_id,)).fetchone()
    if category and not connection.execute("SELECT 1 FROM products WHERE category = ? LIMIT 1", (category["name"],)).fetchone():
        connection.execute("DELETE FROM categories WHERE id = ?", (category_id,))
        connection.commit()
    connection.close()
    return redirect(url_for("admin.products"))

@admin_bp.post("/products")
def add_product():
    access_error = admin_access_required()
    if access_error: return access_error
    form = request.form
    name, description = form.get("name", "").strip(), form.get("description", "").strip()
    if not name or not description: return redirect(url_for("admin.dashboard"))
    try: price = float(form.get("price", "0"))
    except ValueError: price = 0
    connection = get_db()
    category = form.get("category", "").strip()
    if not connection.execute("SELECT 1 FROM categories WHERE name = ?", (category,)).fetchone():
        connection.close()
        return redirect(url_for("admin.products"))
    cursor = connection.execute("INSERT INTO products (name, description, category, price, color, initials, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)", (name, description, category, price, form.get("color", "#d9c7bd"), "".join(word[0] for word in name.split()[:2]).upper(), datetime.now().isoformat(timespec="seconds")))
    product_id = cursor.lastrowid
    images = []
    for slot in (1, 2, 3):
        image = request.files.get(f"image{slot}")
        if image and image.filename and Path(image.filename).suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"}:
            filename = secure_filename(f"product-{product_id}-{slot}{Path(image.filename).suffix.lower()}")
            image.save(UPLOAD_DIR / filename)
            images.append(url_for("static", filename=f"uploads/{filename}"))
        else: images.append(None)
    connection.execute("UPDATE products SET image1 = ?, image2 = ?, image3 = ? WHERE id = ?", (*images, product_id))
    connection.commit()
    connection.close()
    return redirect(url_for("admin.dashboard"))

@admin_bp.post("/products/<int:product_id>/edit")
def edit_product(product_id):
    access_error = admin_access_required()
    if access_error: return access_error
    form = request.form
    try: price = float(form.get("price", "0"))
    except ValueError: price = 0
    connection = get_db()
    category = form.get("category", "").strip()
    if not connection.execute("SELECT 1 FROM categories WHERE name = ?", (category,)).fetchone():
        connection.close()
        return redirect(url_for("admin.products"))
    connection.execute("UPDATE products SET name = ?, description = ?, category = ?, price = ?, color = ? WHERE id = ?", (form.get("name", "").strip(), form.get("description", "").strip(), category, price, form.get("color", "#d9c7bd"), product_id))
    connection.commit()
    connection.close()
    return redirect(url_for("admin.products"))

@admin_bp.post("/products/<int:product_id>/delete")
def delete_product(product_id):
    access_error = admin_access_required()
    if access_error: return access_error
    connection = get_db()
    connection.execute("DELETE FROM products WHERE id = ?", (product_id,))
    connection.commit()
    connection.close()
    return redirect(url_for("admin.products"))

@admin_bp.post("/orders/<int:order_id>/status")
def update_order_status(order_id):
    access_error = admin_access_required()
    if access_error: return access_error
    status = request.form.get("status", "New")
    if status not in {"New", "Packed", "Shipped", "Cancelled"}: status = "New"
    connection = get_db()
    connection.execute("UPDATE orders SET status = ? WHERE id = ?", (status, order_id))
    connection.commit()
    connection.close()
    return redirect(url_for("admin.dashboard"))

@admin_bp.post("/customers")
def create_customer():
    access_error = owner_admin_required()
    if access_error: return access_error
    name, email, password = request.form.get("name", "").strip(), request.form.get("email", "").strip().lower(), request.form.get("password", "")
    if not name or not email or len(password) < 6 or password != request.form.get("confirm_password", ""): return redirect(url_for("admin.dashboard"))
    role = request.form.get("role", "customer") if request.form.get("role") in {"customer", "user"} else "customer"
    connection = get_db()
    try:
        connection.execute("INSERT INTO users (name, email, password, role, created_at) VALUES (?, ?, ?, ?, datetime('now'))", (name, email, generate_password_hash(password), role))
        connection.commit()
    except sqlite3.IntegrityError: pass
    connection.close()
    return redirect(url_for("admin.dashboard"))
