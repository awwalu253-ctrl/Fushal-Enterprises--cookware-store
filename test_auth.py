from app import create_app, db
from app.models import User

def test_auth():
    app = create_app()
    with app.app_context():
        print("=" * 50)
        print("Testing Authentication System")
        print("=" * 50)
        
        # Check existing users
        users = User.query.all()
        print(f"\nExisting users: {len(users)}")
        for user in users:
            print(f"  - {user.email} (Admin: {user.is_admin}, Verified: {user.is_verified})")
        
        # Create a test user if none exists
        if not users:
            print("\nCreating test user...")
            test_user = User(
                username='testuser',
                email='test@example.com',
                is_verified=True,
                is_admin=False
            )
            test_user.set_password('test123')
            db.session.add(test_user)
            db.session.commit()
            print("Test user created: test@example.com / test123")
        
        # Test login
        print("\n" + "=" * 50)
        print("Testing Login")
        print("=" * 50)
        
        test_email = 'test@example.com'
        test_password = 'test123'
        
        user = User.query.filter_by(email=test_email).first()
        
        if user:
            print(f"✓ User found: {user.email}")
            print(f"  Username: {user.username}")
            print(f"  Is Admin: {user.is_admin}")
            print(f"  Is Verified: {user.is_verified}")
            
            if user.check_password(test_password):
                print(f"✓ Password correct!")
            else:
                print(f"✗ Password incorrect!")
        else:
            print(f"✗ User not found: {test_email}")
        
        # Test admin login
        print("\n" + "=" * 50)
        print("Testing Admin Login")
        print("=" * 50)
        
        admin = User.query.filter_by(email='admin@example.com').first()
        if not admin:
            print("Creating admin user...")
            admin = User(
                username='admin',
                email='admin@example.com',
                is_admin=True,
                is_verified=True
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print("Admin created: admin@example.com / admin123")
        else:
            print(f"Admin found: {admin.email}")
            if admin.check_password('admin123'):
                print("✓ Admin password correct!")
            else:
                print("✗ Admin password incorrect!")
        
        print("\n" + "=" * 50)
        print("Test Complete")
        print("=" * 50)

if __name__ == '__main__':
    test_auth()