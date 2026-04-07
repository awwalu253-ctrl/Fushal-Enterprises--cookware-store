from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask_login import login_required, current_user
from app.extensions import db
from app.models import User, Order, OrderItem, Product
from app.utils.decorators import verification_required
from app.utils.email_service import send_order_status_update_email

bp = Blueprint('customer', __name__, url_prefix='/customer')

@bp.route('/dashboard')
@login_required
@verification_required
def dashboard():
    if current_user.is_admin:
        return redirect(url_for('admin.dashboard'))
    
    recent_orders = Order.query.filter_by(user_id=current_user.id)\
                               .order_by(Order.order_date.desc())\
                               .limit(5).all()
    
    return render_template('customer/dashboard.html', recent_orders=recent_orders)

@bp.route('/orders')
@login_required
@verification_required
def orders():
    orders = Order.query.filter_by(user_id=current_user.id)\
                       .order_by(Order.order_date.desc()).all()
    return render_template('customer/orders.html', orders=orders)

@bp.route('/order/<int:order_id>')
@login_required
@verification_required
def order_detail(order_id):
    """View specific order details"""
    order = Order.query.get_or_404(order_id)
    
    # Check if the order belongs to the current user
    if order.user_id != current_user.id and not current_user.is_admin:
        flash('You do not have permission to view this order.', 'danger')
        return redirect(url_for('customer.orders'))
    
    # Get order items with product details
    order_items = OrderItem.query.filter_by(order_id=order.id).all()
    items = []
    for item in order_items:
        product = Product.query.get(item.product_id)
        items.append({
            'product': product,
            'quantity': item.quantity,
            'price': item.price,
            'subtotal': item.price * item.quantity
        })
    
    return render_template('customer/order_detail.html', order=order, items=items)

@bp.route('/profile')
@login_required
@verification_required
def profile():
    """User profile page"""
    return render_template('customer/profile.html', user=current_user)

@bp.route('/profile/edit', methods=['GET', 'POST'])
@login_required
@verification_required
def edit_profile():
    """Edit user profile"""
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        
        # Check if email is already taken by another user
        existing_user = User.query.filter_by(email=email).first()
        if existing_user and existing_user.id != current_user.id:
            flash('Email already taken by another user.', 'danger')
            return redirect(url_for('customer.edit_profile'))
        
        # Check if username is already taken by another user
        existing_username = User.query.filter_by(username=username).first()
        if existing_username and existing_username.id != current_user.id:
            flash('Username already taken by another user.', 'danger')
            return redirect(url_for('customer.edit_profile'))
        
        current_user.username = username
        current_user.email = email
        db.session.commit()
        
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('customer.profile'))
    
    return render_template('customer/edit_profile.html', user=current_user)

@bp.route('/cancel-order/<int:order_id>', methods=['POST'])
@login_required
@verification_required
def cancel_order(order_id):
    """Cancel an order if it's still pending"""
    order = Order.query.get_or_404(order_id)
    
    # Check if order belongs to user
    if order.user_id != current_user.id:
        flash('You do not have permission to cancel this order.', 'danger')
        return redirect(url_for('customer.orders'))
    
    # Only allow cancellation of pending orders
    if order.status == 'pending':
        order.status = 'cancelled'
        db.session.commit()
        
        # Restore product stock
        for item in order.items:
            product = Product.query.get(item.product_id)
            if product:
                product.stock += item.quantity
                product.update_status()
        db.session.commit()
        
        flash(f'Order #{order_id} has been cancelled successfully.', 'success')
    else:
        flash('This order cannot be cancelled as it has already been processed.', 'warning')
    
    return redirect(url_for('customer.orders'))

@bp.route('/add-to-cart/<int:product_id>')
@login_required
@verification_required
def add_to_cart(product_id):
    """Add product to cart (redirects to cart system)"""
    return redirect(url_for('cart.add_to_cart', product_id=product_id))