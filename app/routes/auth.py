from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.extensions import db
from app.models import User
from app.utils.admin_setup import create_permanent_admin
from app.forms import RegistrationForm, LoginForm
from app.utils.email_service import send_verification_email, send_password_reset_email, send_welcome_email
import secrets
from datetime import datetime, timedelta

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        # Check if terms were accepted
        terms_accepted = request.form.get('terms')
        if not terms_accepted:
            flash('You must agree to the Terms of Service and Privacy Policy.', 'danger')
            return render_template('auth/signup.html', form=form)
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash('Email already registered. Please login instead.', 'warning')
            return redirect(url_for('auth.login'))
        
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        user.is_verified = False
        user.verification_token = secrets.token_urlsafe(32)
        db.session.add(user)
        db.session.commit()
        
        # Send verification email
        try:
            send_verification_email(user.email, user.username, user.verification_token)
            flash('Account created! Please check your email to verify your account.', 'success')
        except Exception as e:
            print(f"Email error: {e}")
            flash('Account created! However, we could not send verification email. Please contact support.', 'warning')
        
        # Auto-login the user and redirect to verification page
        login_user(user)
        return redirect(url_for('auth.verification_required_page'))
    
    return render_template('auth/signup.html', form=form)

@bp.route('/verify-email/<token>')
def verify_email(token):
    print(f"Verifying token: {token}")  # Debug print
    user = User.query.filter_by(verification_token=token).first()
    
    if user:
        print(f"User found: {user.email}")  # Debug print
        user.is_verified = True
        user.verification_token = None
        db.session.commit()
        flash('Email verified successfully! You can now log in.', 'success')
    else:
        print(f"No user found with token: {token}")  # Debug print
        flash('Invalid verification token.', 'danger')
    
    return redirect(url_for('auth.login'))



@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for('admin.dashboard'))
        return redirect(url_for('customer.dashboard'))
    
    # Ensure admin exists
    create_permanent_admin()
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            # Only check verification for unverified users
            if not user.is_verified and not user.is_admin:
                flash('Please verify your email before logging in. Check your inbox for the verification link.', 'warning')
                return redirect(url_for('auth.login'))
            
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

@bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        if user:
            # Generate reset token
            user.reset_token = secrets.token_urlsafe(32)
            user.reset_token_expiry = datetime.utcnow() + timedelta(hours=1)
            db.session.commit()
            
            # Send reset email
            try:
                send_password_reset_email(user.email, user.username, user.reset_token)
                flash('Password reset link sent to your email!', 'success')
            except Exception as e:
                print(f"Password reset email error: {e}")
                flash('Error sending password reset email. Please try again.', 'danger')
        else:
            flash('No account found with that email.', 'danger')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/forgot_password.html')

@bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    user = User.query.filter_by(reset_token=token).first()
    if not user or user.reset_token_expiry < datetime.utcnow():
        flash('Invalid or expired reset token.', 'danger')
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        new_password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if new_password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return redirect(url_for('auth.reset_password', token=token))
        
        if len(new_password) < 6:
            flash('Password must be at least 6 characters.', 'danger')
            return redirect(url_for('auth.reset_password', token=token))
        
        user.set_password(new_password)
        user.reset_token = None
        user.reset_token_expiry = None
        db.session.commit()
        
        flash('Password reset successfully! Please log in.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/reset_password.html', token=token)

@bp.route('/verification-required')
def verification_required_page():
    """Page shown to users who need to verify their email"""
    return render_template('auth/verification_required.html')

@bp.route('/resend-verification-code', methods=['POST'])
@login_required
def resend_verification_code():
    """Resend verification email to current user"""
    if current_user.is_verified:
        flash('Your email is already verified.', 'info')
        return redirect(url_for('customer.dashboard'))
    
    # Generate new verification token
    current_user.verification_token = secrets.token_urlsafe(32)
    db.session.commit()
    
    # Send new verification email
    try:
        send_verification_email(current_user.email, current_user.username, current_user.verification_token)
        flash('A new verification link has been sent to your email.', 'success')
    except Exception as e:
        print(f"Resend verification error: {e}")
        flash('Error sending verification email. Please try again.', 'danger')
    
    return redirect(url_for('auth.verification_required_page'))

@bp.route('/resend-verification', methods=['GET', 'POST'])
def resend_verification():
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        
        if user and not user.is_verified:
            # Generate new verification token
            user.verification_token = secrets.token_urlsafe(32)
            db.session.commit()
            
            # Send new verification email
            try:
                send_verification_email(user.email, user.username, user.verification_token)
                flash('A new verification link has been sent to your email.', 'success')
            except Exception as e:
                print(f"Resend verification email error: {e}")
                flash('Error sending verification email. Please try again.', 'danger')
        else:
            flash('Email not found or already verified.', 'warning')
        
        return redirect(url_for('auth.login'))
    
    return render_template('auth/resend_verification.html')