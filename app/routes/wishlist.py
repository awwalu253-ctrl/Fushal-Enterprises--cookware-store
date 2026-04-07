from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app.extensions import db
from app.models import Wishlist, Product

bp = Blueprint('wishlist', __name__, url_prefix='/wishlist')

@bp.route('/add/<int:product_id>', methods=['GET', 'POST'])
@login_required
def add_to_wishlist(product_id):
    """Add product to wishlist"""
    product = Product.query.get_or_404(product_id)
    
    # Check if already in wishlist
    existing = Wishlist.query.filter_by(user_id=current_user.id, product_id=product_id).first()
    
    if existing:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'message': 'Product already in wishlist'})
        flash('Product already in wishlist!', 'info')
    else:
        wishlist_item = Wishlist(user_id=current_user.id, product_id=product_id)
        db.session.add(wishlist_item)
        db.session.commit()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': True, 'message': 'Product added to wishlist!'})
        flash('Product added to wishlist!', 'success')
    
    return redirect(request.referrer or url_for('wishlist.view_wishlist'))

@bp.route('/')
@login_required
def view_wishlist():
    """View wishlist"""
    items = Wishlist.query.filter_by(user_id=current_user.id).all()
    return render_template('wishlist.html', items=items)

@bp.route('/remove/<int:item_id>')
@login_required
def remove_from_wishlist(item_id):
    """Remove item from wishlist"""
    item = Wishlist.query.get_or_404(item_id)
    
    if item.user_id != current_user.id:
        flash('Unauthorized action.', 'danger')
        return redirect(url_for('wishlist.view_wishlist'))
    
    db.session.delete(item)
    db.session.commit()
    flash('Product removed from wishlist!', 'success')
    return redirect(url_for('wishlist.view_wishlist'))

@bp.route('/clear')
@login_required
def clear_wishlist():
    """Clear all items from wishlist"""
    Wishlist.query.filter_by(user_id=current_user.id).delete()
    db.session.commit()
    flash('Your wishlist has been cleared!', 'success')
    return redirect(url_for('wishlist.view_wishlist'))