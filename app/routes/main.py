from flask import Blueprint, render_template, request, session, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from app.models import Product, Category
from app.extensions import db
from app.utils.email_service import send_email
from datetime import datetime

bp = Blueprint('main', __name__, url_prefix='/')

@bp.route('/')
def index():
    products = Product.query.limit(8).all()
    return render_template('index.html', products=products)

@bp.route('/product/<int:product_id>')
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    return render_template('product_detail.html', product=product)

@bp.route('/products')
def all_products():
    # Get all products with optional category filter
    category = request.args.get('category')
    if category:
        products = Product.query.filter_by(category_id=category).all()
    else:
        products = Product.query.all()
    
    # Get all unique categories for filter
    categories = Category.query.all()
    
    return render_template('all_products.html', products=products, categories=categories)

@bp.route('/search')
def search():
    query = request.args.get('q', '')
    if query:
        from sqlalchemy import or_
        products = Product.query.filter(
            or_(
                Product.name.contains(query),
                Product.description.contains(query)
            )
        ).all()
    else:
        products = []
    return render_template('search_results.html', products=products, query=query)

@bp.route('/faq')
def faq():
    return render_template('faq.html')

@bp.route('/contact')
def contact():
    return render_template('contact.html')

@bp.route('/terms')
def terms():
    """Terms of Service page"""
    return render_template('terms.html')

@bp.route('/privacy')
def privacy():
    """Privacy Policy page"""
    return render_template('privacy.html')

@bp.route('/submit-contact', methods=['POST'])
@login_required
def submit_contact():
    """Submit contact form message"""
    from app.utils.email_service import send_contact_email
    from flask import current_app
    
    subject = request.form.get('subject')
    message = request.form.get('message')
    
    if not subject or not message:
        flash('Please fill in all fields.', 'danger')
        return redirect(url_for('main.contact'))
    
    admin_email = current_app.config.get('ADMIN_EMAIL', 'funshoinvestment01@gmail.com')
    
    try:
        result = send_contact_email(
            admin_email,
            current_user.username,
            current_user.email,
            subject,
            message
        )
        
        if result:
            flash('Your message has been sent successfully! We\'ll get back to you soon.', 'success')
        else:
            flash('Could not send message. Please try again later.', 'danger')
    except Exception as e:
        print(f"Contact form error: {e}")
        flash('There was an error sending your message. Please try again later.', 'danger')
    
    return redirect(url_for('main.contact'))