from app import create_app
from app.utils.email_service import send_email

def test_email():
    app = create_app()
    with app.app_context():
        print("Testing email configuration...")
        
        # Test sending email to yourself
        result = send_email(
            'funshoinvestment01@gmail.com',  # Your email
            'Test Email from Awwal Investment',
            'This is a test email to verify your email configuration is working!'
        )
        
        if result:
            print("✓ Email sent successfully!")
        else:
            print("✗ Email failed. Check your credentials.")

if __name__ == '__main__':
    test_email()