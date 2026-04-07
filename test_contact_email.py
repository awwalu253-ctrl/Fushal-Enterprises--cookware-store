from app import create_app
from app.utils.email_service import send_email
from datetime import datetime

app = create_app()
with app.app_context():
    test_subject = "Test Contact Form Message"
    test_body = """
    <h2>Test Message</h2>
    <p>This is a test email from the contact form.</p>
    <p>Time: {}</p>
    """.format(datetime.now())
    
    result = send_email('funshoinvestment01@gmail.com', test_subject, test_body)
    print(f"Email sent: {result}")