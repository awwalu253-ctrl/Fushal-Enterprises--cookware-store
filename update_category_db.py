from app import create_app, db
import sqlite3
import os

def update_category_table():
    app = create_app()
    with app.app_context():
        db_path = 'instance/database.db'
        
        if os.path.exists(db_path):
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Check if is_active column exists
            cursor.execute("PRAGMA table_info(category)")
            columns = [column[1] for column in cursor.fetchall()]
            
            if 'is_active' not in columns:
                cursor.execute('ALTER TABLE category ADD COLUMN is_active BOOLEAN DEFAULT 1')
                print("✓ Added is_active column")
            else:
                print("• is_active column already exists")
            
            if 'icon' not in columns:
                cursor.execute('ALTER TABLE category ADD COLUMN icon VARCHAR(50) DEFAULT "fa-folder"')
                print("✓ Added icon column")
            else:
                print("• icon column already exists")
            
            # Set all existing categories to active
            cursor.execute('UPDATE category SET is_active = 1 WHERE is_active IS NULL')
            print("✓ Set all existing categories to active")
            
            # Set default icon for categories without one
            cursor.execute('UPDATE category SET icon = "fa-folder" WHERE icon IS NULL')
            print("✓ Set default icons for all categories")
            
            conn.commit()
            conn.close()
            print("\n✅ Database update completed successfully!")
        else:
            print("Database not found. Please run the app first.")

if __name__ == '__main__':
    update_category_table()