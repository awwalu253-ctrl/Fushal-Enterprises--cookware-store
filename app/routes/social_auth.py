from flask import Blueprint, redirect, url_for, session, flash
from authlib.integrations.flask_client import OAuth
from flask_login import login_user
from app.extensions import db
from app.models import User
import secrets

bp = Blueprint('social_auth', __name__, url_prefix='/social')
oauth = OAuth()

def init_oauth(app):
    oauth.init_app(app)
    
    # Google OAuth configuration
    oauth.register(
        name='google',
        client_id='YOUR_GOOGLE_CLIENT_ID',
        client_secret='YOUR_GOOGLE_CLIENT_SECRET',
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_kwargs={'scope': 'openid email profile'}
    )

@bp.route('/login/google')
def login_google():
    redirect_uri = url_for('social_auth.google_callback', _external=True)
    return oauth.google.authorize_redirect(redirect_uri)

@bp.route('/google-callback')
def google_callback():
    token = oauth.google.authorize_access_token()
    user_info = oauth.google.parse_id_token(token)
    
    email = user_info.get('email')
    name = user_info.get('name')
    
    user = User.query.filter_by(email=email).first()
    if not user:
        user = User(
            username=name.replace(' ', '_').lower(),
            email=email,
            is_verified=True,
            is_admin=False
        )
        user.set_password(secrets.token_urlsafe(16))
        db.session.add(user)
        db.session.commit()
        flash('Account created successfully with Google!', 'success')
    
    login_user(user)
    flash(f'Welcome back, {user.username}!', 'success')
    return redirect(url_for('customer.dashboard'))