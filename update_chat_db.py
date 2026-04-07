from app import create_app, db
from app.models import ChatSession
import sqlite3
import os

def update_database():
    app = create_app()
    with app.app_context():
        db_path = 'instance/database.db'
        
        if os.path.exists(db_path):
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Check if column exists and add if not
            cursor.execute("PRAGMA table_info(chat_session)")
            columns = [column[1] for column in cursor.fetchall()]
            
            if 'auto_reply_sent' not in columns:
                cursor.execute('ALTER TABLE chat_session ADD COLUMN auto_reply_sent BOOLEAN DEFAULT 0')
                print("✓ Added auto_reply_sent column")
            else:
                print("• auto_reply_sent column already exists")
            
            if 'last_notification_sent' not in columns:
                cursor.execute('ALTER TABLE chat_session ADD COLUMN last_notification_sent TIMESTAMP')
                print("✓ Added last_notification_sent column")
            else:
                print("• last_notification_sent column already exists")
            
            conn.commit()
            conn.close()
            print("\nDatabase update completed successfully!")
        else:
            print("Database not found. Creating new database...")
            db.create_all()
            print("New database created with all tables!")

if __name__ == '__main__':
    update_database()y