from app import create_app, db
from app.models import User, Category, Coupon, Product
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash

def setup_database():
    app = create_app()
    with app.app_context():
        print("Setting up database...")
        
        # Create categories if they don't exist
        categories = [
            'Knives', 'Pans', 'Pots', 'Utensils', 
            'Measuring Tools', 'Cutting Boards', 'Bakeware', 'Gadgets'
        ]
        
        for cat_name in categories:
            existing = Category.query.filter_by(name=cat_name).first()
            if not existing:
                category = Category(name=cat_name)
                db.session.add(category)
                print(f"Added category: {cat_name}")
        
        db.session.commit()
        print("Categories created successfully!")
        
        # Create coupon if it doesn't exist
        existing_coupon = Coupon.query.filter_by(code='WELCOME10').first()
        if not existing_coupon:
            coupon = Coupon(
                code='WELCOME10',
                discount_percent=10,
                expiry_date=datetime.now().date() + timedelta(days=30),
                usage_limit=100,
                is_active=True
            )
            db.session.add(coupon)
            print("Added coupon: WELCOME10 for 10% off")
            db.session.commit()
        else:
            print("Coupon already exists")
        
        # Create sample products if none exist
        if Product.query.count() == 0:
            # Get category IDs
            knives_cat = Category.query.filter_by(name='Knives').first()
            pans_cat = Category.query.filter_by(name='Pans').first()
            pots_cat = Category.query.filter_by(name='Pots').first()
            utensils_cat = Category.query.filter_by(name='Utensils').first()
            
            products = [
                Product(
                    name="Premium Chef Knife",
                    description="High-quality stainless steel chef knife for professional cooking",
                    price=49.99,
                    category_id=knives_cat.id if knives_cat else None,
                    stock=50,
                    image_url="https://via.placeholder.com/300x200/667eea/white?text=Chef+Knife"
                ),
                Product(
                    name="Non-Stick Frying Pan",
                    description="Durable non-stick frying pan with even heat distribution",
                    price=39.99,
                    category_id=pans_cat.id if pans_cat else None,
                    stock=30,
                    image_url="https://via.placeholder.com/300x200/28a745/white?text=Frying+Pan"
                ),
                Product(
                    name="Stainless Steel Pot Set",
                    description="3-piece stainless steel pot set with glass lids",
                    price=89.99,
                    category_id=pots_cat.id if pots_cat else None,
                    stock=20,
                    image_url="https://via.placeholder.com/300x200/ff9800/white?text=Pot+Set"
                ),
                Product(
                    name="Silicone Spatula Set",
                    description="Heat-resistant silicone spatula set for non-stick cookware",
                    price=19.99,
                    category_id=utensils_cat.id if utensils_cat else None,
                    stock=100,
                    image_url="https://via.placeholder.com/300x200/17a2b8/white?text=Spatula"
                )
            ]
            
            for product in products:
                db.session.add(product)
            
            db.session.commit()
            print(f"Added {len(products)} sample products")
        
        print("\n" + "="*50)
        print("DATABASE SETUP COMPLETE!")
        print("="*50)
        print("\nCategories added: 8")
        print("Coupon added: WELCOME10 (10% off)")
        print("Sample products added: 4")
        print("\nYou can now use the following coupon code at checkout: WELCOME10")
        print("="*50)

if __name__ == '__main__':
    setup_database()