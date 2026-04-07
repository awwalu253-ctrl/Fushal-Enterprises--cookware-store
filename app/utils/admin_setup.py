from app.extensions import db
from app.models import User

def create_permanent_admin():
    """Create or ensure admin user exists"""
    try:
        admin = User.query.filter_by(email='funshoinvestment01@gmail.com').first()
        
        if not admin:
            admin = User(
                username='funshoinvestment',
                email='funshoinvestment01@gmail.com',
                is_admin=True,
                is_verified=True
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print("✓ Permanent admin user created!")
        else:
            admin.is_admin = True
            admin.is_verified = True
            db.session.commit()
            print("✓ Admin user verified")
    except Exception as e:
        print(f"Admin setup error: {e}")