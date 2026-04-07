from flask_mail import Mail, Message
from flask import current_app, render_template
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# Initialize mail
mail = Mail()

def init_mail(app):
    """Initialize mail with app"""
    mail.init_app(app)
    print(f"Email configured with: {app.config['MAIL_USERNAME']}")

def send_email(to_email, subject, template, **kwargs):
    """Send email using HTML templates"""
    try:
        html_body = render_template(f'email/{template}.html', **kwargs)
        msg = Message(
            subject=subject,
            recipients=[to_email],
            html=html_body,
            sender=current_app.config['MAIL_DEFAULT_SENDER']
        )
        mail.send(msg)
        print(f"✓ Email sent to {to_email}: {subject}")
        return True
    except Exception as e:
        print(f"✗ Email error to {to_email}: {e}")
        return False

def send_plain_email(to_email, subject, body):
    """Send plain text email without template (for contact form, admin notifications, etc.)"""
    try:
        msg = Message(
            subject=subject,
            recipients=[to_email],
            body=body,
            sender=current_app.config['MAIL_DEFAULT_SENDER']
        )
        mail.send(msg)
        print(f"✓ Plain email sent to {to_email}: {subject}")
        return True
    except Exception as e:
        print(f"✗ Plain email error to {to_email}: {e}")
        return False

def send_welcome_email(user_email, username, verification_link):
    """Send welcome email to new customer with verification link"""
    subject = f"Welcome to Awwal Investment, {username}! 🎉"
    return send_email(
        user_email, 
        subject, 
        'welcome',
        username=username,
        verification_link=verification_link
    )

def send_order_confirmation_email(user_email, username, order_id, total_amount, items, shipping_address=None):
    """Send order confirmation to customer"""
    subject = f"Order Confirmation #{order_id} ✅"
    
    order_date = datetime.now().strftime('%B %d, %Y')
    estimated_delivery = (datetime.now().replace(day=datetime.now().day + 5)).strftime('%B %d, %Y')
    track_url = "http://localhost:5000/customer/orders"
    
    return send_email(
        user_email,
        subject,
        'order_confirmation',
        username=username,
        order_id=order_id,
        total_amount=total_amount,
        items=items,
        shipping_address=shipping_address or 'Not provided',
        order_date=order_date,
        estimated_delivery=estimated_delivery,
        track_url=track_url
    )

def send_order_status_update_email(user_email, username, order_id, status, tracking_number=None):
    """Send order status update to customer"""
    subject = f"Order #{order_id} Status Update 🔄"
    
    status_messages = {
        'pending': 'Your order has been received and is pending processing.',
        'processing': 'Your order is being processed and prepared for shipment.',
        'shipped': 'Great news! Your order has been shipped and is on its way!',
        'delivered': 'Your order has been delivered. Enjoy your cooking utensils!',
        'cancelled': 'Your order has been cancelled.'
    }
    
    status_message = status_messages.get(status, f'Your order status has been updated to: {status}')
    track_url = "http://localhost:5000/customer/orders"
    review_url = f"http://localhost:5000/orders/{order_id}/review"
    
    return send_email(
        user_email,
        subject,
        'order_status_update',
        username=username,
        order_id=order_id,
        status=status,
        status_message=status_message,
        tracking_number=tracking_number,
        track_url=track_url,
        review_url=review_url
    )

def send_new_order_notification_to_admin(order_id, customer_name, customer_email, total_amount):
    """Notify admin about new order"""
    subject = f"🛒 New Order Received! - Order #{order_id}"
    
    body = f"""
{'='*60}
NEW ORDER ALERT!
{'='*60}

Order #{order_id} has been placed!

Customer: {customer_name}
Email: {customer_email}
Total Amount: ${total_amount}

Login to admin dashboard to process the order:
http://localhost:5000/admin/orders

{'='*60}
"""
    
    admin_email = current_app.config['ADMIN_EMAIL']
    return send_plain_email(admin_email, subject, body)

def send_product_added_notification(user_email, username, product_name, product_price=None, product_description=None, product_image=None):
    """Notify customer about new product"""
    subject = f"✨ New Product Alert: {product_name}"
    
    product_url = "http://localhost:5000/products"
    shop_url = "http://localhost:5000"
    
    return send_email(
        user_email,
        subject,
        'new_product',
        username=username,
        product_name=product_name,
        product_description=product_description or 'Check out our newest addition to the collection!',
        product_price=product_price or 'Check website for price',
        product_image=product_image or 'https://via.placeholder.com/200',
        product_url=product_url,
        shop_url=shop_url
    )

def send_verification_email(user_email, username, token):
    """Send email verification link to user"""
    subject = "Verify Your Email Address - Awwal Investment ✅"
    verification_link = f"http://localhost:5000/auth/verify-email/{token}"
    
    return send_email(
        user_email,
        subject,
        'welcome',
        username=username,
        verification_link=verification_link
    )

def send_password_reset_email(user_email, username, token):
    """Send password reset link to user"""
    subject = "Password Reset Request - Awwal Investment 🔐"
    reset_link = f"http://localhost:5000/auth/reset-password/{token}"
    
    return send_email(
        user_email,
        subject,
        'password_reset',
        username=username,
        reset_link=reset_link
    )

def send_contact_email(admin_email, customer_name, customer_email, subject, message):
    """Send contact form message to admin"""
    email_subject = f"📧 Contact Form: {subject}"
    
    body = f"""
{'='*60}
NEW CONTACT FORM MESSAGE
{'='*60}

Customer Information:
-------------------
Name: {customer_name}
Email: {customer_email}
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Message Details:
---------------
Subject: {subject}

Message:
{message}

{'='*60}
Reply to: {customer_email}
{'='*60}
"""
    
    return send_plain_email(admin_email, email_subject, body)