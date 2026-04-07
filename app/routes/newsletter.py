from flask import Blueprint, request, redirect, url_for, flash
from app.extensions import db
from app.models import Newsletter
from datetime import datetime

bp = Blueprint('newsletter', __name__, url_prefix='/newsletter')

@bp.route('/subscribe', methods=['POST'])
def subscribe():
    email = request.form.get('email')
    
    if not email:
        flash('Please provide an email address.', 'danger')
        return redirect(request.referrer or url_for('main.index'))
    
    # Check if email already exists
    existing = Newsletter.query.filter_by(email=email).first()
    if existing:
        flash('This email is already subscribed to our newsletter.', 'info')
        return redirect(request.referrer or url_for('main.index'))
    
    # Add new subscriber
    subscriber = Newsletter(
        email=email,
        subscribed_at=datetime.utcnow(),
        is_active=True
    )
    db.session.add(subscriber)
    db.session.commit()
    
    flash('Successfully subscribed to our newsletter!', 'success')
    return redirect(request.referrer or url_for('main.index'))

@bp.route('/unsubscribe/<string:email>')
def unsubscribe(email):
    subscriber = Newsletter.query.filter_by(email=email).first()
    if subscriber:
        subscriber.is_active = False
        db.session.commit()
        flash('You have been unsubscribed from our newsletter.', 'success')
    else:
        flash('Email not found in our newsletter list.', 'danger')
    
    return redirect(url_for('main.index'))