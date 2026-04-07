from itsdangerous import URLSafeTimedSerializer
from flask import current_app

def generate_token(email):
    """Generate a secure token for email verification or password reset"""
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return serializer.dumps(email, salt='email-verification')

def verify_token(token, expiration=3600):
    """Verify token and return email if valid"""
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        email = serializer.loads(
            token,
            salt='email-verification',
            max_age=expiration
        )
        return email
    except:
        return None

def generate_reset_token(email):
    """Generate password reset token"""
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return serializer.dumps(email, salt='password-reset')

def verify_reset_token(token, expiration=3600):
    """Verify password reset token"""
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        email = serializer.loads(
            token,
            salt='password-reset',
            max_age=expiration
        )
        return email
    except:
        return None