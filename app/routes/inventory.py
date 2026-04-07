from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, send_file
from flask_login import login_required, current_user
from app.extensions import db
from app.models import Product, Order, User
from app.utils.decorators import admin_required
from datetime import datetime, timedelta
import csv
import io

bp = Blueprint('inventory', __name__, url_prefix='/inventory')

@bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    """Inventory dashboard with analytics"""
    products = Product.query.all()
    
    # Calculate inventory stats
    total_products = len(products)
    total_value = sum(p.price * p.stock for p in products)
    low_stock_products = [p for p in products if p.is_low_stock()]
    out_of_stock_products = [p for p in products if p.is_out_of_stock()]
    
    # Category breakdown
    categories = {}
    for product in products:
        if product.category:
            categories[product.category] = categories.get(product.category, 0) + 1
    
    # Recent orders
    recent_orders = Order.query.order_by(Order.order_date.desc()).limit(10).all()
    
    # Sales data for last 7 days
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    recent_sales = Order.query.filter(Order.order_date >= seven_days_ago).all()
    total_sales = sum(o.total_amount for o in recent_sales)
    
    return render_template('inventory/dashboard.html',
                         products=products,
                         total_products=total_products,
                         total_value=total_value,
                         low_stock_products=low_stock_products,
                         out_of_stock_products=out_of_stock_products,
                         categories=categories,
                         recent_orders=recent_orders,
                         recent_sales=recent_sales,
                         total_sales=total_sales)

@bp.route('/low-stock')
@login_required
@admin_required
def low_stock():
    """View low stock products"""
    products = Product.query.filter(Product.stock <= Product.low_stock_threshold).all()
    return render_template('inventory/low_stock.html', products=products)

@bp.route('/update-stock/<int:product_id>', methods=['POST'])
@login_required
@admin_required
def update_stock(product_id):
    """Update product stock quantity"""
    product = Product.query.get_or_404(product_id)
    new_stock = int(request.form.get('stock', 0))
    old_stock = product.stock
    product.stock = new_stock
    product.updated_at = datetime.utcnow()
    db.session.commit()
    
    if old_stock <= product.low_stock_threshold and new_stock > product.low_stock_threshold:
        flash(f'Stock updated! {product.name} is now above low stock threshold.', 'success')
    else:
        flash(f'Stock for {product.name} updated from {old_stock} to {new_stock}.', 'success')
    
    return redirect(url_for('inventory.dashboard'))

@bp.route('/bulk-update', methods=['POST'])
@login_required
@admin_required
def bulk_update():
    """Bulk update product stocks"""
    for key, value in request.form.items():
        if key.startswith('stock_'):
            product_id = int(key.split('_')[1])
            product = Product.query.get(product_id)
            if product:
                product.stock = int(value)
                product.updated_at = datetime.utcnow()
    
    db.session.commit()
    flash('Bulk stock update completed!', 'success')
    return redirect(url_for('inventory.dashboard'))

@bp.route('/export-report')
@login_required
@admin_required
def export_report():
    """Export inventory report as CSV"""
    products = Product.query.all()
    
    # Create CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write headers
    writer.writerow(['SKU', 'Name', 'Category', 'Price', 'Stock', 'Low Stock Threshold', 'Status', 'Total Value'])
    
    # Write data
    for product in products:
        status = 'Low Stock' if product.is_low_stock() else ('Out of Stock' if product.is_out_of_stock() else 'In Stock')
        writer.writerow([
            product.sku or 'N/A',
            product.name,
            product.category or 'N/A',
            product.price,
            product.stock,
            product.low_stock_threshold,
            status,
            product.price * product.stock
        ])
    
    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8')),
        mimetype='text/csv',
        as_attachment=True,
        download_name='inventory_report.csv'
    )

@bp.route('/set-threshold/<int:product_id>', methods=['POST'])
@login_required
@admin_required
def set_threshold(product_id):
    """Set low stock threshold for product"""
    product = Product.query.get_or_404(product_id)
    threshold = int(request.form.get('threshold', 10))
    product.low_stock_threshold = threshold
    db.session.commit()
    flash(f'Low stock threshold for {product.name} set to {threshold}.', 'success')
    return redirect(url_for('inventory.dashboard'))

@bp.route('/api/stats')
@login_required
@admin_required
def api_stats():
    """API endpoint for inventory stats (for charts)"""
    products = Product.query.all()
    
    # Category distribution
    category_data = {}
    for product in products:
        if product.category:
            category_data[product.category] = category_data.get(product.category, 0) + 1
    
    # Stock levels
    stock_data = {
        'In Stock': sum(1 for p in products if not p.is_low_stock() and p.stock > 0),
        'Low Stock': sum(1 for p in products if p.is_low_stock() and p.stock > 0),
        'Out of Stock': sum(1 for p in products if p.is_out_of_stock())
    }
    
    return jsonify({
        'categories': category_data,
        'stock_levels': stock_data,
        'total_products': len(products),
        'total_inventory_value': sum(p.price * p.stock for p in products)
    })