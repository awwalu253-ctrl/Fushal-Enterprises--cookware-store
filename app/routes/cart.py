from flask import Blueprint, render_template, session, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.extensions import db
from app.models import Product, Order, OrderItem
from app.utils.email_service import send_order_confirmation_email, send_new_order_notification_to_admin
from app.utils.decorators import verification_required
from app.models import AbandonedCart
import json
from datetime import datetime, timedelta

def track_abandoned_cart():
    """Track when user leaves items in cart"""
    if current_user.is_authenticated:
        cart = session.get('cart', {})
        if cart:
            existing = AbandonedCart.query.filter_by(
                user_id=current_user.id, 
                is_recovered=False
            ).first()
            
            if existing:
                existing.cart_data = json.dumps(cart)
                existing.updated_at = datetime.utcnow()
            else:
                abandoned = AbandonedCart(
                    user_id=current_user.id,
                    cart_data=json.dumps(cart),
                    email=current_user.email
                )
                db.session.add(abandoned)
            db.session.commit()

# Call this function when user leaves cart page

bp = Blueprint('cart', __name__, url_prefix='/cart')

@bp.route('/clear')
@login_required
def clear_cart():
    """Clear all items from cart"""
    session.pop('cart', None)
    flash('Cart cleared successfully!', 'success')
    return redirect(url_for('cart.view_cart'))

@bp.route('/remove-all')
@login_required
def remove_all():
    """Remove all items from cart"""
    session['cart'] = {}
    flash('All items removed from cart!', 'success')
    return redirect(url_for('cart.view_cart'))

@bp.route('/add/<int:product_id>', methods=['GET', 'POST'])
@login_required
def add_to_cart(product_id):
    """Add product to cart"""
    product = Product.query.get_or_404(product_id)
    
    # Get quantity from form if POST, else default to 1
    quantity = 1
    if request.method == 'POST':
        quantity = int(request.form.get('quantity', 1))
    
    # Get cart from session
    cart = session.get('cart', {})
    
    # Add or update quantity
    product_id_str = str(product_id)
    if product_id_str in cart:
        cart[product_id_str] += quantity
    else:
        cart[product_id_str] = quantity
    
    # Save to session
    session['cart'] = cart
    
    flash(f'{quantity} x {product.name} added to cart!', 'success')
    return redirect(url_for('cart.view_cart'))

@bp.route('/view')
@login_required
def view_cart():
    """View shopping cart"""
    cart = session.get('cart', {})
    items = []
    total = 0
    
    for product_id, quantity in cart.items():
        product = Product.query.get(int(product_id))
        if product:
            subtotal = product.price * quantity
            total += subtotal
            items.append({
                'product': product,
                'quantity': quantity,
                'subtotal': subtotal
            })
    
    return render_template('cart.html', items=items, total=total)

@bp.route('/update/<int:product_id>', methods=['POST'])
@login_required
def update_quantity(product_id):
    """Update item quantity in cart"""
    quantity = int(request.form.get('quantity', 0))
    cart = session.get('cart', {})
    
    if quantity <= 0:
        cart.pop(str(product_id), None)
    else:
        cart[str(product_id)] = quantity
    
    session['cart'] = cart
    flash('Cart updated!', 'success')
    return redirect(url_for('cart.view_cart'))

@bp.route('/remove/<int:product_id>')
@login_required
def remove_item(product_id):
    """Remove item from cart"""
    cart = session.get('cart', {})
    cart.pop(str(product_id), None)
    session['cart'] = cart
    flash('Item removed from cart', 'success')
    return redirect(url_for('cart.view_cart'))

@bp.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    """Checkout process"""
    cart = session.get('cart', {})
    
    if not cart:
        flash('Your cart is empty', 'warning')
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        # Get shipping info
        shipping_address = f"{request.form.get('address')}, {request.form.get('city')}, {request.form.get('zipcode')}"
        
        # Calculate total
        total = 0
        items = []
        for product_id, quantity in cart.items():
            product = Product.query.get(int(product_id))
            if product:
                subtotal = product.price * quantity
                total += subtotal
                items.append({
                    'name': product.name,
                    'price': product.price,
                    'quantity': quantity
                })
        
        # Create order
        order = Order(
            user_id=current_user.id,
            total_amount=total,
            status='pending',
            shipping_address=shipping_address
        )
        db.session.add(order)
        db.session.commit()
        
        # Create order items
        for product_id, quantity in cart.items():
            product = Product.query.get(int(product_id))
            order_item = OrderItem(
                order_id=order.id,
                product_id=product.id,
                quantity=quantity,
                price=product.price
            )
            db.session.add(order_item)
            
            # Update stock
            product.stock -= quantity
        
        db.session.commit()
        
        # Send emails
        send_order_confirmation_email(current_user.email, current_user.username, order.id, total, items)
        send_new_order_notification_to_admin(order.id, current_user.username, current_user.email, total)
        
        # Clear cart
        session.pop('cart', None)
        
        flash(f'Order #{order.id} placed successfully! Check your email.', 'success')
        return redirect(url_for('customer.orders'))
    
    # Calculate total for display
    total = 0
    items = []
    for product_id, quantity in cart.items():
        product = Product.query.get(int(product_id))
        if product:
            subtotal = product.price * quantity
            total += subtotal
            items.append({
                'product': product,
                'quantity': quantity,
                'subtotal': subtotal
            })
    
    return render_template('checkout.html', items=items, total=total)