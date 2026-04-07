from app import create_app, db
from app.models import User, Product

app = create_app()
with app.app_context():
    db.drop_all()
    db.create_all()
    
    # Create admin
    admin = User(username='admin', email='admin@example.com', is_admin=True)
    admin.set_password('admin123')
    db.session.add(admin)
    
    # Create sample products with inventory fields
    products = [
        Product(name="Premium Chef Knife", description="High-quality stainless steel chef knife", price=49.99, category="Knives", stock=50, sku="KNIFE001", low_stock_threshold=10),
        Product(name="Non-Stick Frying Pan", description="Durable non-stick frying pan", price=39.99, category="Pans", stock=5, sku="PAN001", low_stock_threshold=10),
        Product(name="Stainless Steel Pot Set", description="3-piece pot set with glass lids", price=89.99, category="Pots", stock=3, sku="POT001", low_stock_threshold=10),
        Product(name="Silicone Spatula Set", description="Heat-resistant silicone spatulas", price=19.99, category="Utensils", stock=100, sku="SPAT001", low_stock_threshold=20),
        Product(name="Measuring Cups Set", description="Stainless steel measuring cups", price=15.99, category="Measuring Tools", stock=0, sku="MEASURE001", low_stock_threshold=15),
        Product(name="Wooden Cutting Board", description="Premium bamboo cutting board", price=29.99, category="Cutting Boards", stock=8, sku="BOARD001", low_stock_threshold=10),
    ]
    
    for product in products:
        db.session.add(product)
    
    db.session.commit()
    
    print("=" * 50)
    print("DATABASE RESET COMPLETE!")
    print("=" * 50)
    print("\nAdmin Login:")
    print("  Email: admin@example.com")
    print("  Password: admin123")
    print(f"\nProducts Added: {len(products)}")
    print("\nInventory Status:")
    print(f"  - Low stock products: {sum(1 for p in products if p.is_low_stock())}")
    print(f"  - Out of stock products: {sum(1 for p in products if p.is_out_of_stock())}")
    print("=" * 50)