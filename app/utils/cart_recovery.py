from app.extensions import db
from app.models import AbandonedCart, User
from app.utils.email_service import send_email
from datetime import datetime, timedelta
import json

def check_abandoned_carts():
    """Check for abandoned carts and send recovery emails"""
    # Carts abandoned for more than 1 hour
    cutoff_time = datetime.utcnow() - timedelta(hours=1)
    
    abandoned_carts = AbandonedCart.query.filter(
        AbandonedCart.updated_at <= cutoff_time,
        AbandonedCart.is_recovered == False
    ).all()
    
    for cart in abandoned_carts:
        user = User.query.get(cart.user_id)
        if user and user.email:
            cart_data = json.loads(cart.cart_data)
            item_count = len(cart_data)
            
            subject = "🛒 You left items in your cart!"
            body = f"""
            <html>
            <head><style>
                body {{ font-family: Arial, sans-serif; }}
                .container {{ max-width: 600px; margin: auto; padding: 20px; }}
                .header {{ background: #667eea; color: white; padding: 20px; text-align: center; }}
                .button {{ background: #667eea; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; }}
            </style></head>
            <body>
                <div class="container">
                    <div class="header">
                        <h2>Don't Forget Your Items!</h2>
                    </div>
                    <div class="content">
                        <p>Hello {user.username},</p>
                        <p>You have <strong>{item_count} item(s)</strong> waiting in your cart.</p>
                        <p>Complete your purchase now before they're gone!</p>
                        <div style="text-align: center;">
                            <a href="http://localhost:5000/cart/view" class="button">View My Cart</a>
                        </div>
                    </div>
                </div>
            </body>
            </html>
            """
            send_email(user.email, subject, body)
            cart.is_recovered = True
            db.session.commit()