from flask import current_app
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_email(to_email, subject, body):
    '''Simple email sending function'''
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
    <p>Total Amount: </p>
    <p>We'll notify you once your order ships.</p>
    <p>Best regards,<br>Awwal Investment Team</p>
    """
    return send_email(user_email, subject, body)
