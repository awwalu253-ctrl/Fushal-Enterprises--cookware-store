from app import create_app, db
from app.models import User

def fix_admin():
    app = create_app()
    with app.app_context():
        # Delete any existing admin
        User.query.filter_by(email='funshoinvestment01@gmail.com').delete()
        User.query.filter_by(username='funshoinvestment').delete()
        db.session.commit()
        
        # Create fresh admin
        admin = User(
            username='funshoinvestment',
            email='funshoinvestment01@gmail.com',
            is_admin=True,
            is_verified=True
        )
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        
        print("=" * 50)
        print("ADMIN USER CREATED SUCCESSFULLY!")
        print("=" * 50)
        print("Email: funshoinvestment01@gmail.com")
        print("Password: admin123")
        print("=" * 50)
        
        # Verify
        verify = User.query.filter_by(email='funshoinvestment01@gmail.com').first()
        if verify and verify.check_password('admin123'):
            print("✓ Password verification: SUCCESS")
        else:
            print("✗ Password verification: FAILED")

if __name__ == '__main__':
    fix_admin()