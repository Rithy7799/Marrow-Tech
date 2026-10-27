from flask import Flask

from routes.admin import admin_bp, add_product, create_customer, dashboard, delete_product, edit_product, products, update_order_status
from routes.auth import auth_bp, login, logout, register
from routes.front import about_page, add_review, category, checkout, create_order, front_bp, notifications_page, product_detail, profile, storefront, toggle_favorite, update_profile
from store import current_user_context, currency, init_db

app = Flask(__name__)
app.secret_key = "morrow-development-key"

app.register_blueprint(front_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)

# Keep existing templates and links compatible with the pre-blueprint endpoint names.
compatibility_rules = [
    ("storefront", "/", storefront, ["GET"]),
    ("about", "/about", about_page, ["GET"]),
    ("category", "/category/<category_name>", category, ["GET"]),
    ("product_detail", "/product/<int:product_id>", product_detail, ["GET"]),
    ("checkout", "/checkout", checkout, ["GET"]),
    ("profile", "/profile", profile, ["GET"]),
    ("notifications_page", "/notifications", notifications_page, ["GET"]),
    ("update_profile", "/profile/update", update_profile, ["POST"]),
    ("toggle_favorite", "/product/<int:product_id>/favorite", toggle_favorite, ["POST"]),
    ("add_review", "/product/<int:product_id>/review", add_review, ["POST"]),
    ("create_order", "/api/orders", create_order, ["POST"]),
    ("register", "/register", register, ["GET", "POST"]),
    ("login", "/login", login, ["GET", "POST"]),
    ("logout", "/logout", logout, ["GET"]),
    ("admin", "/admin", dashboard, ["GET"]),
    ("manage_products", "/admin/products", products, ["GET"]),
    ("add_product", "/admin/products", add_product, ["POST"]),
    ("edit_product", "/admin/products/<int:product_id>/edit", edit_product, ["POST"]),
    ("delete_product", "/admin/products/<int:product_id>/delete", delete_product, ["POST"]),
    ("update_order_status", "/admin/orders/<int:order_id>/status", update_order_status, ["POST"]),
    ("create_customer", "/admin/customers", create_customer, ["POST"]),
]
for endpoint, path, view, methods in compatibility_rules:
    app.add_url_rule(path, endpoint=endpoint, view_func=view, methods=methods)

app.template_filter("currency")(currency)
app.context_processor(current_user_context)

init_db()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8555, debug=True)
