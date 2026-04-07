from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask_login import login_required, current_user
from app import db
from app.models import Order, OrderItem, Product, User
from app.utils.email_service import (
    send_order_confirmation_email, 
    send_order_status_update_email,
    send_new_order_notification_to_admin
)

bp = Blueprint('orders', __name__, url_prefix='/orders')

@bp.route('/checkout', methods=['POST'])
@login_required
def checkout():
    """Process checkout and create order"""
    # This is simplified - in real app, you'd have a cart system
    cart_items = request.form.getlist('cart_items')  # Simplified
    
    if not cart_items:
        flash('Your cart is empty.', 'warning')
        return redirect(url_for('main.index'))
    
    total_amount = 0
    items = []
    
    # Calculate total and create order items
    for item_id in cart_items:
        product = Product.query.get(item_id)
        if product:
            total_amount += product.price
            items.append({
                'name': product.name,
                'price': product.price,
                'quantity': 1
            })
    
    # Create order
    order = Order(
        user_id=current_user.id,
        total_amount=total_amount,
        status='pending',
        shipping_address='Customer address here'  # Get from form
    )
    db.session.add(order)
    db.session.commit()
    
    # Add order items
    for item in items:
        product = Product.query.filter_by(name=item['name']).first()
        order_item = OrderItem(
            order_id=order.id,
            product_id=product.id,
            quantity=1,
            price=item['price']
        )
        db.session.add(order_item)
    
    db.session.commit()
    
    # Send email confirmation to customer
    send_order_confirmation_email(
        current_user.email,
        current_user.username,
        order.id,
        total_amount,
        items
    )
    
    # Send notification to admin
    send_new_order_notification_to_admin(
        order.id,
        current_user.username,
        current_user.email,
        total_amount
    )
    
    flash(f'Order #{order.id} placed successfully! Check your email for confirmation.', 'success')
    return redirect(url_for('customer.orders'))

@bp.route('/update-status/<int:order_id>', methods=['POST'])
@login_required
def update_order_status(order_id):
    """Update order status (admin only)"""
    if not current_user.is_admin:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('main.index'))
    
    order = Order.query.get_or_404(order_id)
    new_status = request.form.get('status')
    
    if new_status:
        old_status = order.status
        order.status = new_status
        db.session.commit()
        
        # Get customer info
        customer = User.query.get(order.user_id)
        
        # Send status update email to customer
        send_order_status_update_email(
            customer.email,
            customer.username,
            order.id,
            new_status
        )
        
        flash(f'Order #{order_id} status updated from {old_status} to {new_status}. Customer notified.', 'success')
    
    return redirect(url_for('admin.orders'))