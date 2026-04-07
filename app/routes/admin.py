from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app.extensions import db
from app.models import Product, Order, User, Category
from app.forms import ProductForm
from app.utils.decorators import admin_required
from app.utils.email_service import send_product_added_notification
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
import os

bp = Blueprint('admin', __name__, url_prefix='/admin')

@bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    products_count = Product.query.count()
    orders_count = Order.query.count()
    users_count = User.query.filter_by(is_admin=False).count()
    recent_orders = Order.query.order_by(Order.order_date.desc()).limit(5).all()
    
    return render_template('admin/dashboard.html', 
                         products_count=products_count,
                         orders_count=orders_count,
                         users_count=users_count,
                         recent_orders=recent_orders)

@bp.route('/products')
@login_required
@admin_required
def products():
    products = Product.query.all()
    return render_template('admin/products.html', products=products)

@bp.route('/add-product', methods=['GET', 'POST'])
@login_required
@admin_required
def add_product():
    from app.models import Category
    
    form = ProductForm()
    form.category.choices = [(c.id, c.name) for c in Category.query.all()]
    
    if form.validate_on_submit():
        product = Product(
            name=form.name.data,
            description=form.description.data,
            price=form.price.data,
            category_id=form.category.data,
            stock=form.stock.data,
            image_url=form.image_url.data or 'https://via.placeholder.com/300x200'
        )
        
        db.session.add(product)
        db.session.commit()
        
        # Notify all customers about new product
        customers = User.query.filter_by(is_admin=False).all()
        for customer in customers:
            send_product_added_notification(customer.email, customer.username, product.name)
        
        flash('Product added successfully! Customers have been notified.', 'success')
        return redirect(url_for('admin.products'))
    
    return render_template('admin/add_product.html', form=form)

@bp.route('/edit-product/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_product(id):
    from app.models import Category
    
    product = Product.query.get_or_404(id)
    form = ProductForm(obj=product)
    form.category.choices = [(c.id, c.name) for c in Category.query.all()]
    
    if form.validate_on_submit():
        product.name = form.name.data
        product.description = form.description.data
        product.price = form.price.data
        product.category_id = form.category.data
        product.stock = form.stock.data
        if form.image_url.data:
            product.image_url = form.image_url.data
        
        db.session.commit()
        flash('Product updated successfully!', 'success')
        return redirect(url_for('admin.products'))
    
    return render_template('admin/edit_product.html', form=form, product=product)

@bp.route('/inventory')
@login_required
@admin_required
def inventory():
    """Inventory management dashboard"""
    from app.models import Product
    
    # Get low stock products (less than 10)
    low_stock = Product.query.filter(Product.stock < 10, Product.stock > 0).all()
    
    # Get out of stock products
    out_of_stock = Product.query.filter(Product.stock == 0).all()
    
    # Get all products with stock count
    products = Product.query.all()
    total_value = sum(p.price * p.stock for p in products)
    
    return render_template('admin/inventory.html',
                         low_stock=low_stock,
                         out_of_stock=out_of_stock,
                         products=products,
                         total_value=total_value)

@bp.route('/categories')
@login_required
@admin_required
def categories():
    """Manage product categories"""
    from app.models import Category
    categories = Category.query.all()
    return render_template('admin/categories.html', categories=categories)

@bp.route('/export-products')
@login_required
@admin_required
def export_products():
    """Export products to CSV"""
    import csv
    from io import StringIO
    from flask import Response
    
    products = Product.query.all()
    
    si = StringIO()
    cw = csv.writer(si)
    cw.writerow(['ID', 'Name', 'Description', 'Price', 'Category', 'Stock', 'Image URL', 'Created At'])
    
    for product in products:
        cw.writerow([
            product.id,
            product.name,
            product.description,
            product.price,
            product.category.name if product.category else 'Uncategorized',
            product.stock,
            product.image_url,
            product.created_at.strftime('%Y-%m-%d %H:%M:%S')
        ])
    
    output = si.getvalue()
    return Response(output, mimetype='text/csv', headers={"Content-Disposition": "attachment; filename=products.csv"})

@bp.route('/delete-product/<int:id>')
@login_required
@admin_required
def delete_product(id):
    product = Product.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()
    flash('Product deleted successfully!', 'success')
    return redirect(url_for('admin.products'))

@bp.route('/orders')
@login_required
@admin_required
def orders():
    orders = Order.query.order_by(Order.order_date.desc()).all()
    return render_template('admin/orders.html', orders=orders)

@bp.route('/update-order-status/<int:order_id>', methods=['POST'])
@login_required
@admin_required
def update_order_status(order_id):
    """Update order status and notify customer"""
    order = Order.query.get_or_404(order_id)
    new_status = request.form.get('status')
    
    if new_status:
        old_status = order.status
        order.status = new_status
        db.session.commit()
        
        # Get customer info
        customer = User.query.get(order.user_id)
        
        # Send status update email to customer
        from app.utils.email_service import send_order_status_update_email
        send_order_status_update_email(
            customer.email,
            customer.username,
            order.id,
            new_status
        )
        
        flash(f'Order #{order_id} status updated from {old_status} to {new_status}. Customer notified.', 'success')
    
    return redirect(url_for('admin.orders'))

@bp.route('/add-category', methods=['GET', 'POST'])
@login_required
@admin_required
def add_category():
    """Add a new product category"""
    from app.models import Category
    
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        
        if not name:
            flash('Category name is required.', 'danger')
            return redirect(url_for('admin.add_category'))
        
        # Check if category already exists
        existing = Category.query.filter_by(name=name).first()
        if existing:
            flash('Category with this name already exists.', 'danger')
            return redirect(url_for('admin.add_category'))
        
        category = Category(name=name, description=description)
        db.session.add(category)
        db.session.commit()
        
        flash(f'Category "{name}" added successfully!', 'success')
        return redirect(url_for('admin.categories'))
    
    return render_template('admin/add_category.html')

@bp.route('/edit-category/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_category(id):
    """Edit an existing category"""
    from app.models import Category
    
    category = Category.query.get_or_404(id)
    
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        icon = request.form.get('icon', 'fa-folder')
        is_active = request.form.get('is_active') == 'on'  # Checkbox returns 'on' when checked
        
        if not name:
            flash('Category name is required.', 'danger')
            return redirect(url_for('admin.edit_category', id=id))
        
        # Check if another category has this name
        existing = Category.query.filter(Category.name == name, Category.id != id).first()
        if existing:
            flash('Another category with this name already exists.', 'danger')
            return redirect(url_for('admin.edit_category', id=id))
        
        category.name = name
        category.description = description
        category.icon = icon
        category.is_active = is_active
        db.session.commit()
        
        flash(f'Category "{name}" updated successfully!', 'success')
        return redirect(url_for('admin.categories'))
    
    return render_template('admin/edit_category.html', category=category)

@bp.route('/export-newsletter')
@login_required
@admin_required
def export_newsletter():
    """Export newsletter subscribers to CSV"""
    import csv
    from io import StringIO
    from flask import Response
    from app.models import Newsletter
    
    subscribers = Newsletter.query.filter_by(is_active=True).all()
    
    si = StringIO()
    cw = csv.writer(si)
    cw.writerow(['Email', 'Subscribed Date', 'Status'])
    
    for sub in subscribers:
        cw.writerow([
            sub.email,
            sub.subscribed_at.strftime('%Y-%m-%d %H:%M:%S'),
            'Active' if sub.is_active else 'Inactive'
        ])
    
    output = si.getvalue()
    return Response(output, mimetype='text/csv', headers={"Content-Disposition": "attachment; filename=newsletter_subscribers.csv"})

@bp.route('/delete-category/<int:id>')
@login_required
@admin_required
def delete_category(id):
    """Delete a category"""
    from app.models import Category
    
    category = Category.query.get_or_404(id)
    
    # Check if category has products
    if category.products and len(category.products) > 0:
        flash(f'Cannot delete "{category.name}" because it has {len(category.products)} products. Move or delete products first.', 'danger')
    else:
        category_name = category.name
        db.session.delete(category)
        db.session.commit()
        flash(f'Category "{category_name}" deleted successfully!', 'success')
    
    return redirect(url_for('admin.categories'))

@bp.route('/customers')
@login_required
@admin_required
def customers():
    """View all registered customers"""
    from sqlalchemy import func
    
    # Get filter parameters
    page = request.args.get('page', 1, type=int)
    per_page = 20
    search_query = request.args.get('search', '')
    status_filter = request.args.get('status', 'all')
    
    # Build query
    query = User.query.filter_by(is_admin=False)
    
    # Apply search filter
    if search_query:
        query = query.filter(
            db.or_(
                User.username.contains(search_query),
                User.email.contains(search_query)
            )
        )
    
    # Apply status filter
    if status_filter == 'verified':
        query = query.filter_by(is_verified=True)
    elif status_filter == 'unverified':
        query = query.filter_by(is_verified=False)
    
    # Paginate results
    paginated = query.order_by(User.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
    customers = paginated.items
    
    # Get statistics
    total_customers = User.query.filter_by(is_admin=False).count()
    verified_customers = User.query.filter_by(is_admin=False, is_verified=True).count()
    unverified_customers = total_customers - verified_customers
    
    # New customers this month
    first_day_of_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    new_this_month = User.query.filter(User.created_at >= first_day_of_month, User.is_admin == False).count()
    
    return render_template('admin/customers.html',
                         customers=customers,
                         total_customers=total_customers,
                         verified_customers=verified_customers,
                         unverified_customers=unverified_customers,
                         new_this_month=new_this_month,
                         page=page,
                         total_pages=paginated.pages,
                         search_query=search_query,
                         status_filter=status_filter)

@bp.route('/customer/<int:customer_id>/details')
@login_required
@admin_required
def customer_details(customer_id):
    """Get customer details for modal"""
    from app.models import Order, Review
    
    customer = User.query.get_or_404(customer_id)
    
    # Get recent orders
    recent_orders = Order.query.filter_by(user_id=customer.id).order_by(Order.order_date.desc()).limit(5).all()
    
    # Calculate total spent
    total_spent = db.session.query(db.func.sum(Order.total_amount)).filter_by(user_id=customer.id).scalar() or 0
    
    # Get last order date
    last_order = Order.query.filter_by(user_id=customer.id).order_by(Order.order_date.desc()).first()
    
    return jsonify({
        'id': customer.id,
        'username': customer.username,
        'email': customer.email,
        'is_verified': customer.is_verified,
        'is_admin': customer.is_admin,
        'created_at': customer.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        'total_orders': Order.query.filter_by(user_id=customer.id).count(),
        'total_spent': float(total_spent),
        'total_reviews': Review.query.filter_by(user_id=customer.id).count(),
        'last_order_date': last_order.order_date.strftime('%Y-%m-%d %H:%M:%S') if last_order else 'No orders',
        'recent_orders': [{
            'id': order.id,
            'date': order.order_date.strftime('%Y-%m-%d'),
            'total': order.total_amount,
            'status': order.status
        } for order in recent_orders]
    })

@bp.route('/customer/<int:customer_id>/verify', methods=['POST'])
@login_required
@admin_required
def verify_customer(customer_id):
    """Manually verify a customer"""
    customer = User.query.get_or_404(customer_id)
    customer.is_verified = True
    customer.verification_token = None
    db.session.commit()
    
    return jsonify({'status': 'success'})

@bp.route('/export-customers')
@login_required
@admin_required
def export_customers():
    """Export customers to CSV"""
    import csv
    from io import StringIO
    from flask import Response
    
    search_query = request.args.get('search', '')
    status_filter = request.args.get('status', 'all')
    
    query = User.query.filter_by(is_admin=False)
    
    if search_query:
        query = query.filter(
            db.or_(
                User.username.contains(search_query),
                User.email.contains(search_query)
            )
        )
    
    if status_filter == 'verified':
        query = query.filter_by(is_verified=True)
    elif status_filter == 'unverified':
        query = query.filter_by(is_verified=False)
    
    customers = query.all()
    
    # Create CSV
    si = StringIO()
    cw = csv.writer(si)
    cw.writerow(['ID', 'Username', 'Email', 'Verified', 'Joined Date', 'Total Orders', 'Total Spent'])
    
    for customer in customers:
        total_orders = len(customer.orders)
        total_spent = sum(order.total_amount for order in customer.orders)
        cw.writerow([
            customer.id,
            customer.username,
            customer.email,
            'Yes' if customer.is_verified else 'No',
            customer.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            total_orders,
            f"${total_spent:.2f}"
        ])
    
    output = si.getvalue()
    return Response(output, mimetype='text/csv', headers={"Content-Disposition": "attachment; filename=customers.csv"})

@bp.route('/newsletter')
@login_required
@admin_required
def newsletter():
    """View newsletter subscribers"""
    from app.models import Newsletter
    subscribers = Newsletter.query.order_by(Newsletter.subscribed_at.desc()).all()
    total_subscribers = Newsletter.query.count()
    active_subscribers = Newsletter.query.filter_by(is_active=True).count()
    inactive_subscribers = total_subscribers - active_subscribers
    
    return render_template('admin/newsletter.html', 
                         subscribers=subscribers,
                         total_subscribers=total_subscribers,
                         active_subscribers=active_subscribers,
                         inactive_subscribers=inactive_subscribers)

@bp.route('/send-newsletter', methods=['POST'])
@login_required
@admin_required
def send_newsletter():
    """Send newsletter to all active subscribers"""
    from app.models import Newsletter
    from app.utils.email_service import send_email
    
    subject = request.form.get('subject')
    message = request.form.get('message')
    
    if not subject or not message:
        flash('Subject and message are required.', 'danger')
        return redirect(url_for('admin.newsletter'))
    
    subscribers = Newsletter.query.filter_by(is_active=True).all()
    
    if not subscribers:
        flash('No active subscribers to send to.', 'warning')
        return redirect(url_for('admin.newsletter'))
    
    success_count = 0
    for subscriber in subscribers:
        try:
            send_email(subscriber.email, subject, message)
            success_count += 1
        except Exception as e:
            print(f"Failed to send to {subscriber.email}: {e}")
    
    flash(f'Newsletter sent to {success_count} out of {len(subscribers)} subscribers.', 'success')
    return redirect(url_for('admin.newsletter'))