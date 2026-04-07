from app import create_app, db
from app.models import User

app = create_app()
with app.app_context():
    # Check for existing admin
    admin = User.query.filter_by(email='admin@example.com').first()
    
    if admin:
        print(f"Admin user found:")
        print(f"  Username: {admin.username}")
        print(f"  Email: {admin.email}")
        print(f"  Is Admin: {admin.is_admin}")
        print(f"  Is Verified: {admin.is_verified}")
        
        # Test password
        if admin.check_password('admin123'):
            print("  Password 'admin123' is CORRECT ✓")
        else:
            print("  Password 'admin123' is INCORRECT ✗")
    else:
        print("No admin user found. Creating one...")
        
        # Create admin user
        admin = User(
            username='admin',
            email='admin@example.com',
            is_admin=True,
            is_verified=True  # Mark as verified so they can login
        )
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print("Admin user created successfully!")
        print("  Email: admin@example.com")
        print("  Password: admin123")