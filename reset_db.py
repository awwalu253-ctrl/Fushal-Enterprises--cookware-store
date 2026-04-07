from app import create_app, db
from app.models import User, Product, Order, OrderItem

def reset_database():
    app = create_app()
    with app.app_context():
        print("Creating fresh tables...")
        db.create_all()
        
        print("Creating admin user...")
        admin = User(
            username='admin', 
            email='admin@example.com', 
            is_admin=True,
            email_verified=True  # Admin is pre-verified
        )
        admin.set_password('admin123')
        db.session.add(admin)
        
        print("Creating sample customer...")
        customer = User(
            username='customer',
            email='customer@example.com',
            is_admin=False,
            email_verified=True
        )
        customer.set_password('customer123')
        db.session.add(customer)
        
        print("Creating sample products...")
        products = [
            Product(name="Premium Chef Knife", description="High-quality stainless steel chef knife", price=49.99, category="Knives", stock=50),
            Product(name="Non-Stick Frying Pan", description="Durable non-stick frying pan", price=39.99, category="Pans", stock=30),
            Product(name="Stainless Steel Pot Set", description="3-piece pot set with lids", price=89.99, category="Pots", stock=20),
            Product(name="Silicone Spatula Set", description="Heat-resistant silicone spatulas", price=19.99, category="Utensils", stock=100),
            Product(name="Measuring Cups Set", description="Stainless steel measuring cups", price=15.99, category="Measuring Tools", stock=75),
            Product(name="Wooden Cutting Board", description="Premium bamboo cutting board", price=29.99, category="Cutting Boards", stock=45)
        ]
        
        for product in products:
            db.session.add(product)
        
        db.session.commit()
        
        print("\n" + "="*50)
        print("DATABASE RESET COMPLETE!")
        print("="*50)
        print("\nLogin Credentials:")
        print("  Admin: admin@example.com / admin123")
        print("  Customer: customer@example.com / customer123")
        print(f"\nProducts added: {len(products)}")
        print("="*50)

if __name__ == '__main__':
    reset_database()