from app import create_app, db
from app.models import Product
import sqlite3
import os

def migrate_database():
    """Add new columns to product table for inventory management"""
    
    app = create_app()
    with app.app_context():
        db_path = 'instance/database.db'
        
        if not os.path.exists(db_path):
            print("Database file not found. Creating new database...")
            db.create_all()
            print("Database created successfully!")
            return
        
        print("Migrating database...")
        
        # Connect to SQLite database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check and add low_stock_threshold column
        try:
            cursor.execute('ALTER TABLE product ADD COLUMN low_stock_threshold INTEGER DEFAULT 10')
            print("✓ Added low_stock_threshold column")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print("✓ low_stock_threshold column already exists")
            else:
                print(f"! {e}")
        
        # Check and add sku column
        try:
            cursor.execute('ALTER TABLE product ADD COLUMN sku VARCHAR(50)')
            print("✓ Added sku column")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print("✓ sku column already exists")
            else:
                print(f"! {e}")
        
        # Check and add updated_at column
        try:
            cursor.execute('ALTER TABLE product ADD COLUMN updated_at DATETIME')
            print("✓ Added updated_at column")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print("✓ updated_at column already exists")
            else:
                print(f"! {e}")
        
        # Check and add is_active column
        try:
            cursor.execute('ALTER TABLE product ADD COLUMN is_active BOOLEAN DEFAULT 1')
            print("✓ Added is_active column")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print("✓ is_active column already exists")
            else:
                print(f"! {e}")
        
        # Update existing products with default SKU if needed
        cursor.execute("UPDATE product SET sku = 'SKU_' || id WHERE sku IS NULL")
        cursor.execute("UPDATE product SET updated_at = created_at WHERE updated_at IS NULL")
        
        conn.commit()
        conn.close()
        
        print("\n" + "="*50)
        print("Database migration completed successfully!")
        print("="*50)

if __name__ == '__main__':
    migrate_database()