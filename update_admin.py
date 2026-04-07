from app import create_app, db
from app.models import User

app = create_app()
with app.app_context():
    # Delete any existing admin users
    User.query.delete()
    db.session.commit()
    
    # Create new admin with your credentials
    admin = User(
        username='Admin',
        email='funshoinvestment01@gmail.com',
        is_admin=True
    )
    admin.set_password('Admin123')
    db.session.add(admin)
    db.session.commit()
    
    # Verify the admin was created correctly
    verify_admin = User.query.filter_by(email='funshoinvestment01@gmail.com').first()
    
    print("\n" + "="*60)
    print("ADMIN USER UPDATED SUCCESSFULLY!")
    print("="*60)
    print(f"Username: {verify_admin.username}")
    print(f"Email: {verify_admin.email}")
    print(f"Is Admin: {verify_admin.is_admin}")
    print(f"Password check: {verify_admin.check_password('Admin123')}")
    print("="*60)
    print("\nLogin Credentials:")
    print("  Email: funshoinvestment01@gmail.com")
    print("  Password: Admin123")
    print("="*60)