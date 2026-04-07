# create_project.ps1
Write-Host "Creating project structure for Awwal Investment..." -ForegroundColor Green

# Create main directories
New-Item -ItemType Directory -Force -Path "app\routes"
New-Item -ItemType Directory -Force -Path "app\templates\auth"
New-Item -ItemType Directory -Force -Path "app\templates\admin"
New-Item -ItemType Directory -Force -Path "app\templates\customer"
New-Item -ItemType Directory -Force -Path "app\static\css"
New-Item -ItemType Directory -Force -Path "app\static\js"
New-Item -ItemType Directory -Force -Path "app\static\images"
New-Item -ItemType Directory -Force -Path "app\utils"
New-Item -ItemType Directory -Force -Path "instance"

Write-Host "Directories created successfully!" -ForegroundColor Green

# Create requirements.txt
@"
Flask==3.0.0
Flask-SQLAlchemy==3.1.1
Flask-Login==0.6.2
Flask-WTF==1.1.1
Werkzeug==3.0.1
email-validator==2.0.0
pillow==10.1.0
python-dotenv==1.0.0
"@ | Out-File -FilePath "requirements.txt" -Encoding UTF8

# Create config.py
@"
import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///database.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Email configuration (update with your email settings)
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('EMAIL_USER')
    MAIL_PASSWORD = os.environ.get('EMAIL_PASS')
    MAIL_DEFAULT_SENDER = os.environ.get('EMAIL_USER')
"@ | Out-File -FilePath "config.py" -Encoding UTF8

# Create run.py
@"
from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
"@ | Out-File -FilePath "run.py" -Encoding UTF8

# Create app/__init__.py
@"
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please log in to access this page.'

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    db.init_app(app)
    login_manager.init_app(app)
    
    # Register blueprints
    from app.routes import main, auth, admin, customer
    app.register_blueprint(main.bp)
    app.register_blueprint(auth.bp)
    app.register_blueprint(admin.bp)
    app.register_blueprint(customer.bp)
    
    with app.app_context():
        db.create_all()
    
    return app
"@ | Out-File -FilePath "app\__init__.py" -Encoding UTF8

# Create app/models.py
@"
from flask_login import UserMixin
from app import db, login_manager
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    orders = db.relationship('Order', backref='customer', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(100))
    stock = db.Column(db.Integer, default=0)
    image_url = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    order_items = db.relationship('OrderItem', backref='product', lazy=True)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    order_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(50), default='pending')
    total_amount = db.Column(db.Float, nullable=False)
    shipping_address = db.Column(db.Text)
    items = db.relationship('OrderItem', backref='order', lazy=True)

class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
"@ | Out-File -FilePath "app\models.py" -Encoding UTF8

# Create app/forms.py
@"
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, FloatField, IntegerField, SelectField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from app.models import User

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=80)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already taken.')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered.')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class ProductForm(FlaskForm):
    name = StringField('Product Name', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    price = FloatField('Price', validators=[DataRequired()])
    category = StringField('Category', validators=[DataRequired()])
    stock = IntegerField('Stock Quantity', validators=[DataRequired()])
    image_url = StringField('Image URL')
    submit = SubmitField('Add Product')
"@ | Out-File -FilePath "app\forms.py" -Encoding UTF8

# Create route files
@"
from flask import Blueprint, render_template
from app.models import Product

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    products = Product.query.limit(8).all()
    return render_template('index.html', products=products)
"@ | Out-File -FilePath "app\routes\__init__.py" -Encoding UTF8

@"
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import User
from app.forms import RegistrationForm, LoginForm
from app.utils.email_utils import send_welcome_email

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        
        # Send welcome email
        send_welcome_email(user.email, user.username)
        
        flash('Account created successfully! Please log in.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/signup.html', form=form)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for('admin.dashboard'))
        return redirect(url_for('customer.dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            if user.is_admin:
                return redirect(url_for('admin.dashboard'))
            return redirect(url_for('customer.dashboard'))
        flash('Invalid email or password.', 'danger')
    
    return render_template('auth/login.html', form=form)

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))
"@ | Out-File -FilePath "app\routes\auth.py" -Encoding UTF8

@"
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import Product, Order, User
from app.forms import ProductForm
from app.utils.decorators import admin_required
from app.utils.email_utils import send_product_added_email

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
    form = ProductForm()
    if form.validate_on_submit():
        product = Product(
            name=form.name.data,
            description=form.description.data,
            price=form.price.data,
            category=form.category.data,
            stock=form.stock.data,
            image_url=form.image_url.data
        )
        db.session.add(product)
        db.session.commit()
        
        # Notify all customers about new product
        customers = User.query.filter_by(is_admin=False).all()
        for customer in customers:
            send_product_added_email(customer.email, customer.username, product.name)
        
        flash('Product added successfully!', 'success')
        return redirect(url_for('admin.products'))
    
    return render_template('admin/add_product.html', form=form)

@bp.route('/edit-product/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_product(id):
    product = Product.query.get_or_404(id)
    form = ProductForm(obj=product)
    
    if form.validate_on_submit():
        product.name = form.name.data
        product.description = form.description.data
        product.price = form.price.data
        product.category = form.category.data
        product.stock = form.stock.data
        product.image_url = form.image_url.data
        
        db.session.commit()
        flash('Product updated successfully!', 'success')
        return redirect(url_for('admin.products'))
    
    return render_template('admin/edit_product.html', form=form, product=product)

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
"@ | Out-File -FilePath "app\routes\admin.py" -Encoding UTF8

@"
from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask_login import login_required, current_user
from app.models import Order, Product
from app.utils.email_utils import send_order_confirmation

bp = Blueprint('customer', __name__, url_prefix='/customer')

@bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.is_admin:
        return redirect(url_for('admin.dashboard'))
    
    recent_orders = Order.query.filter_by(user_id=current_user.id)\
                               .order_by(Order.order_date.desc())\
                               .limit(5).all()
    
    return render_template('customer/dashboard.html', recent_orders=recent_orders)

@bp.route('/orders')
@login_required
def orders():
    orders = Order.query.filter_by(user_id=current_user.id)\
                       .order_by(Order.order_date.desc()).all()
    return render_template('customer/orders.html', orders=orders)

@bp.route('/add-to-cart/<int:product_id>')
@login_required
def add_to_cart(product_id):
    # Simplified cart - you can implement session-based cart
    flash('Product added to cart! (Implement cart functionality)', 'info')
    return redirect(url_for('main.index'))
"@ | Out-File -FilePath "app\routes\customer.py" -Encoding UTF8

# Create utils files
@"
from flask import current_app
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_email(to_email, subject, body):
    \"\"\"Simple email sending function\"\"\"
    try:
        msg = MIMEMultipart()
        msg['From'] = current_app.config['MAIL_DEFAULT_SENDER']
        msg['To'] = to_email
        msg['Subject'] = subject
        
        msg.attach(MIMEText(body, 'html'))
        
        server = smtplib.SMTP(current_app.config['MAIL_SERVER'], current_app.config['MAIL_PORT'])
        server.starttls()
        server.login(current_app.config['MAIL_USERNAME'], current_app.config['MAIL_PASSWORD'])
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"Email error: {e}")
        return False

def send_welcome_email(user_email, username):
    subject = "Welcome to Awwal Investment - Cooking Utensils Store"
    body = f"""
    <h2>Welcome {username}!</h2>
    <p>Thank you for registering with Awwal Investment.</p>
    <p>We're excited to have you as a customer. Browse our collection of premium cooking utensils!</p>
    <p>Best regards,<br>Awwal Investment Team</p>
    """
    return send_email(user_email, subject, body)

def send_product_added_email(user_email, username, product_name):
    subject = f"New Product Added: {product_name}"
    body = f"""
    <h2>New Product Alert!</h2>
    <p>Dear {username},</p>
    <p>We've just added a new product to our store: <strong>{product_name}</strong></p>
    <p>Check it out on our website!</p>
    <p>Best regards,<br>Awwal Investment Team</p>
    """
    return send_email(user_email, subject, body)

def send_order_confirmation(user_email, username, order_id, total_amount):
    subject = f"Order Confirmation #{order_id}"
    body = f"""
    <h2>Order Confirmed!</h2>
    <p>Dear {username},</p>
    <p>Thank you for your order. Your order #{order_id} has been confirmed.</p>
    <p>Total Amount: ${total_amount}</p>
    <p>We'll notify you once your order ships.</p>
    <p>Best regards,<br>Awwal Investment Team</p>
    """
    return send_email(user_email, subject, body)
"@ | Out-File -FilePath "app\utils\__init__.py" -Encoding UTF8

@"
from functools import wraps
from flask import flash, redirect, url_for
from flask_login import current_user

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('You need admin privileges to access this page.', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function
"@ | Out-File -FilePath "app\utils\decorators.py" -Encoding UTF8

# Create base template
@"
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Awwal Investment - Cooking Utensils</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        .navbar-brand {
            font-weight: bold;
        }
        .hero-section {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 100px 0;
        }
        .product-card {
            transition: transform 0.3s;
            margin-bottom: 20px;
        }
        .product-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        footer {
            background-color: #333;
            color: white;
            padding: 30px 0;
            margin-top: 50px;
        }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
        <div class="container">
            <a class="navbar-brand" href="{{ url_for('main.index') }}">Awwal Investment</a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav ms-auto">
                    <li class="nav-item">
                        <a class="nav-link" href="{{ url_for('main.index') }}">Home</a>
                    </li>
                    {% if current_user.is_authenticated %}
                        {% if current_user.is_admin %}
                            <li class="nav-item">
                                <a class="nav-link" href="{{ url_for('admin.dashboard') }}">Admin Dashboard</a>
                            </li>
                        {% else %}
                            <li class="nav-item">
                                <a class="nav-link" href="{{ url_for('customer.dashboard') }}">My Dashboard</a>
                            </li>
                        {% endif %}
                        <li class="nav-item">
                            <a class="nav-link" href="{{ url_for('auth.logout') }}">Logout</a>
                        </li>
                    {% else %}
                        <li class="nav-item">
                            <a class="nav-link" href="{{ url_for('auth.login') }}">Login</a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="{{ url_for('auth.signup') }}">Sign Up</a>
                        </li>
                    {% endif %}
                </ul>
            </div>
        </div>
    </nav>

    {% with messages = get_flashed_messages(with_categories=true) %}
        {% if messages %}
            {% for category, message in messages %}
                <div class="alert alert-{{ category }} alert-dismissible fade show m-3" role="alert">
                    {{ message }}
                    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                </div>
            {% endfor %}
        {% endif %}
    {% endwith %}

    {% block content %}{% endblock %}

    <footer>
        <div class="container text-center">
            <p>&copy; 2024 Awwal Investment - Premium Cooking Utensils. All rights reserved.</p>
        </div>
    </footer>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
"@ | Out-File -FilePath "app\templates\base.html" -Encoding UTF8

# Create index.html
@"
{% extends "base.html" %}

{% block content %}
<div class="hero-section">
    <div class="container text-center">
        <h1>Welcome to Awwal Investment</h1>
        <p class="lead">Premium Cooking Utensils for Your Kitchen</p>
        <a href="#products" class="btn btn-light btn-lg">Shop Now</a>
    </div>
</div>

<div class="container my-5" id="products">
    <h2 class="text-center mb-4">Our Products</h2>
    <div class="row">
        {% for product in products %}
        <div class="col-md-3">
            <div class="card product-card">
                {% if product.image_url %}
                <img src="{{ product.image_url }}" class="card-img-top" alt="{{ product.name }}" style="height: 200px; object-fit: cover;">
                {% else %}
                <div class="card-img-top bg-secondary text-white d-flex align-items-center justify-content-center" style="height: 200px;">
                    No Image
                </div>
                {% endif %}
                <div class="card-body">
                    <h5 class="card-title">{{ product.name }}</h5>
                    <p class="card-text">{{ product.description[:100] }}...</p>
                    <p class="card-text"><strong>${{ product.price }}</strong></p>
                    {% if current_user.is_authenticated and not current_user.is_admin %}
                    <a href="{{ url_for('customer.add_to_cart', product_id=product.id) }}" class="btn btn-primary">Add to Cart</a>
                    {% endif %}
                </div>
            </div>
        </div>
        {% endfor %}
    </div>
</div>
{% endblock %}
"@ | Out-File -FilePath "app\templates\index.html" -Encoding UTF8

Write-Host "All files created successfully!" -ForegroundColor Green
Write-Host "`nNext steps:" -ForegroundColor Yellow
Write-Host "1. Run: python -m venv venv" -ForegroundColor Cyan
Write-Host "2. Run: venv\Scripts\activate" -ForegroundColor Cyan
Write-Host "3. Run: pip install -r requirements.txt" -ForegroundColor Cyan
Write-Host "4. Run: python run.py" -ForegroundColor Cyan