from flask import Flask
from config import Config
from app.extensions import db, login_manager
from app.utils.email_service import init_mail

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    db.init_app(app)
    login_manager.init_app(app)
    
    # Initialize email
    init_mail(app)
    
    # Register blueprints
    from app.routes import main, auth, admin, customer, cart, wishlist, search, analytics, chat, newsletter
    
    app.register_blueprint(main.bp)
    app.register_blueprint(auth.bp)
    app.register_blueprint(admin.bp)
    app.register_blueprint(customer.bp)
    app.register_blueprint(cart.bp)
    app.register_blueprint(wishlist.bp)
    app.register_blueprint(search.bp)
    app.register_blueprint(analytics.bp)
    app.register_blueprint(chat.bp)
    app.register_blueprint(newsletter.bp)
    
    with app.app_context():
        db.create_all()
        
        # Create permanent admin user
        from app.utils.admin_setup import create_permanent_admin
        create_permanent_admin()
    
    return app