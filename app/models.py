from flask_login import UserMixin
from app.extensions import db, login_manager
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import os
from PIL import Image

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def save_image(self, image_file):
    """Save uploaded image and create thumbnail"""
    from flask import current_app
    
    # Generate unique filename
    import secrets
    _, f_ext = os.path.splitext(image_file.filename)
    filename = secrets.token_hex(16) + f_ext
    
    # Save original image
    image_path = os.path.join(current_app.root_path, 'static/uploads/products', filename)
    image_file.save(image_path)
    
    # Create thumbnail
    img = Image.open(image_path)
    img.thumbnail((300, 300))
    thumb_filename = 'thumb_' + filename
    thumb_path = os.path.join(current_app.root_path, 'static/uploads/products/thumbnails', thumb_filename)
    img.save(thumb_path)
    
    # Save to database
    self.image_url = f'/static/uploads/products/{filename}'
    self.thumbnail_url = f'/static/uploads/products/thumbnails/{thumb_filename}'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean, default=False)
    is_verified = db.Column(db.Boolean, default=False)
    verification_token = db.Column(db.String(100), unique=True)
    reset_token = db.Column(db.String(100), unique=True)
    reset_token_expiry = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    orders = db.relationship('Order', backref='customer', lazy=True)
    reviews = db.relationship('Review', backref='user', lazy=True)
    wishlist_items = db.relationship('Wishlist', backref='user', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    stock = db.Column(db.Integer, default=0)
    status = db.Column(db.String(20), default='in_stock')
    image_url = db.Column(db.String(500))
    thumbnail_url = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    order_items = db.relationship('OrderItem', backref='product', lazy=True)
    reviews = db.relationship('Review', backref='product', lazy=True)
    wishlisted_by = db.relationship('Wishlist', backref='product', lazy=True)
    
    def update_status(self):
        if self.stock <= 0:
            self.status = 'out_of_stock'
        elif self.stock <= 10:
            self.status = 'low_stock'
        else:
            self.status = 'in_stock'
        db.session.commit()

class Category(db.Model):
    __tablename__ = 'category'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)
    image_url = db.Column(db.String(500))
    icon = db.Column(db.String(50), default='fa-folder')
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    products = db.relationship('Product', backref='category', lazy=True)
    
    @property
    def product_count(self):
        return len(self.products)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    order_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(50), default='pending')
    total_amount = db.Column(db.Float, nullable=False)
    shipping_address = db.Column(db.Text)
    tracking_number = db.Column(db.String(100))
    estimated_delivery = db.Column(db.DateTime)
    items = db.relationship('OrderItem', backref='order', lazy=True)

class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_approved = db.Column(db.Boolean, default=True)

class Wishlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Coupon(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), unique=True, nullable=False)
    discount_percent = db.Column(db.Integer, nullable=False)
    expiry_date = db.Column(db.Date, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    usage_limit = db.Column(db.Integer)
    used_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Newsletter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    subscribed_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

class PasswordReset(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    token = db.Column(db.String(100), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)
    is_used = db.Column(db.Boolean, default=False)

class ProductVariant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    variant_name = db.Column(db.String(100))
    variant_value = db.Column(db.String(100))
    additional_price = db.Column(db.Float, default=0)
    stock = db.Column(db.Integer, default=0)
    sku = db.Column(db.String(100), unique=True)
    
    product = db.relationship('Product', backref=db.backref('variants', lazy=True))

class AbandonedCart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    cart_data = db.Column(db.Text)
    email = db.Column(db.String(120))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_recovered = db.Column(db.Boolean, default=False)
    
    user = db.relationship('User', backref=db.backref('abandoned_carts', lazy=True))

class ChatSession(db.Model):
    __tablename__ = 'chat_session'
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(100), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    user_email = db.Column(db.String(120))
    user_name = db.Column(db.String(80))
    status = db.Column(db.String(20), default='active')
    auto_reply_sent = db.Column(db.Boolean, default=False)
    last_notification_sent = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    messages = db.relationship('ChatMessage', backref='chat_session_ref', lazy=True, cascade='all, delete-orphan')

class ChatMessage(db.Model):
    __tablename__ = 'chat_message'
    id = db.Column(db.Integer, primary_key=True)
    chat_session_id = db.Column(db.Integer, db.ForeignKey('chat_session.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    message = db.Column(db.Text, nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='user_chat_messages')