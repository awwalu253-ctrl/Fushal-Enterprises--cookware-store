from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from app.extensions import db
from app.models import Category, Coupon, Newsletter, Product, Order
from app.utils.email_service import send_email
from datetime import datetime, timedelta

bp = Blueprint('additional', __name__, url_prefix='/additional')

# Category Management
@bp.route('/admin/categories')
@login_required
def admin_categories():
    if not current_user.is_admin:
        return redirect(url_for('main.index'))
    categories = Category.query.all()
    return render_template('admin/categories.html', categories=categories)

# Coupon System
@bp.route('/apply-coupon', methods=['POST'])
@login_required
def apply_coupon():
    code = request.form.get('coupon_code')
    coupon = Coupon.query.filter_by(code=code, is_active=True).first()
    
    if coupon and coupon.expiry_date >= datetime.now().date():
        if coupon.usage_limit and coupon.used_count >= coupon.usage_limit:
            flash('Coupon usage limit reached', 'danger')
        else:
            session['coupon'] = coupon.code
            session['discount'] = coupon.discount_percent
            flash(f'Coupon applied! {coupon.discount_percent}% discount', 'success')
    else:
        flash('Invalid or expired coupon code', 'danger')
    
    return redirect(url_for('cart.checkout'))

# Newsletter System
@bp.route('/subscribe-newsletter', methods=['POST'])
def subscribe_newsletter():
    email = request.form.get('email')
    existing = Newsletter.query.filter_by(email=email).first()
    
    if not existing:
        newsletter = Newsletter(email=email)
        db.session.add(newsletter)
        db.session.commit()
        flash('Subscribed to newsletter successfully!', 'success')
    else:
        flash('Email already subscribed', 'info')
    
    return redirect(url_for('main.index'))

# Bulk Product Import (CSV)
@bp.route('/admin/bulk-import', methods=['GET', 'POST'])
@login_required
def bulk_import():
    if not current_user.is_admin:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        file = request.files['csv_file']
        if file:
            import csv
            import io
            stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
            csv_input = csv.reader(stream)
            next(csv_input)  # Skip header
            
            for row in csv_input:
                product = Product(
                    name=row[0],
                    description=row[1],
                    price=float(row[2]),
                    category=row[3],
                    stock=int(row[4])
                )
                db.session.add(product)
            db.session.commit()
            flash('Products imported successfully!', 'success')
    
    return render_template('admin/bulk_import.html')

# Sales Report
@bp.route('/admin/sales-report')
@login_required
def sales_report():
    if not current_user.is_admin:
        return redirect(url_for('main.index'))
    
    # Last 30 days sales
    thirty_days_ago = datetime.now() - timedelta(days=30)
    recent_orders = Order.query.filter(Order.order_date >= thirty_days_ago).all()
    
    total_revenue = sum(order.total_amount for order in recent_orders)
    total_orders = len(recent_orders)
    
    return render_template('admin/sales_report.html', 
                         total_revenue=total_revenue, 
                         total_orders=total_orders,
                         orders=recent_orders)

# Live Chat Support (using Tawk.to or similar)
@bp.route('/support')
def support():
    return render_template('support.html')

# FAQ Page
@bp.route('/faq')
def faq():
    faqs = [
        {'question': 'How do I track my order?', 'answer': 'Go to My Orders section and click Track Order'},
        {'question': 'What is your return policy?', 'answer': '30-day return policy for unused items'},
        {'question': 'Do you ship internationally?', 'answer': 'Currently shipping within Nigeria only'},
    ]
    return render_template('faq.html', faqs=faqs)

# Google Analytics Integration
@bp.context_processor
def inject_analytics():
    return {'ga_tracking_id': 'UA-XXXXX-X'}  # Replace with your ID