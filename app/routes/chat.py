from flask import Blueprint, render_template, request, jsonify, session, current_app, redirect, url_for, flash
from flask_login import login_required, current_user
from app.extensions import db
from app.models import ChatSession, ChatMessage, User
from app.utils.email_service import send_email
import secrets
from datetime import datetime

bp = Blueprint('chat', __name__, url_prefix='/chat')

# Auto-reply message
AUTO_REPLY_MESSAGE = """Thank you for reaching out to Awwal Investment! 🎉

We have received your message and our support team will get back to you shortly. 

Our typical response time is within 1-2 hours during business hours (9 AM - 6 PM, Monday - Saturday).

In the meantime, you can:
• Browse our products: http://localhost:5000
• Check your orders: http://localhost:5000/customer/orders
• Visit our FAQ page

Thank you for your patience!

Best regards,
Awwal Investment Support Team
"""

def send_admin_chat_notification(chat_session, message_text):
    """Send email notification to admin about new chat message"""
    subject = f"🔔 New Chat Message from {chat_session.user_name or 'Guest'}"
    
    admin_email = current_app.config.get('ADMIN_EMAIL', 'funshoinvestment01@gmail.com')
    
    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: 'Segoe UI', Arial, sans-serif; }}
            .container {{ max-width: 600px; margin: auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; text-align: center; border-radius: 10px 10px 0 0; }}
            .content {{ padding: 20px; background: #f8f9fa; }}
            .info-box {{ background: white; padding: 15px; border-radius: 8px; margin: 10px 0; border-left: 4px solid #667eea; }}
            .message-box {{ background: #e9ecef; padding: 15px; border-radius: 8px; margin: 15px 0; }}
            .button {{ display: inline-block; padding: 12px 25px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; text-decoration: none; border-radius: 25px; margin: 10px 0; }}
            .footer {{ text-align: center; padding: 15px; font-size: 12px; color: #666; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h2>💬 New Chat Message</h2>
                <p>Customer Support Alert</p>
            </div>
            <div class="content">
                <div class="info-box">
                    <strong>👤 Customer Information:</strong><br>
                    Name: {chat_session.user_name or 'Guest'}<br>
                    Email: {chat_session.user_email or 'Not provided'}<br>
                    Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                </div>
                
                <div class="message-box">
                    <strong>💬 Message:</strong><br>
                    {message_text}
                </div>
                
                <div style="text-align: center;">
                    <a href="http://localhost:5000/chat/admin/session/{chat_session.id}" class="button">
                        📨 Reply to Customer
                    </a>
                </div>
                
                <div class="info-box">
                    <strong>📌 Quick Actions:</strong><br>
                    • View all chats: http://localhost:5000/chat/admin/dashboard<br>
                    • Customer orders: http://localhost:5000/admin/orders
                </div>
            </div>
            <div class="footer">
                <p>This is an automated notification from Awwal Investment.</p>
                <p>&copy; 2025 Awwal Investment - Premium Cooking Utensils Store</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    send_email(admin_email, subject, html_body)

@bp.route('/widget')
def chat_widget():
    """Chat widget for frontend"""
    return render_template('chat/widget.html')

@bp.route('/api/mark-read', methods=['POST'])
def mark_messages_read():
    """Mark all unread messages as read for current user"""
    session_id = session.get('chat_session_id')
    if session_id:
        chat_session = ChatSession.query.filter_by(session_id=session_id).first()
        if chat_session:
            # Mark all non-admin messages as read
            ChatMessage.query.filter_by(
                chat_session_id=chat_session.id,
                is_admin=False,
                is_read=False
            ).update({'is_read': True})
            db.session.commit()
    return jsonify({'status': 'success'})

@bp.route('/api/messages', methods=['GET', 'POST'])
def chat_messages():
    """Get or send messages"""
    if request.method == 'POST':
        # Send message
        data = request.json
        message_text = data.get('message')
        
        if not message_text:
            return jsonify({'error': 'Message is required'}), 400
        
        # Get or create session
        session_id = session.get('chat_session_id')
        if not session_id:
            session_id = secrets.token_urlsafe(32)
            session['chat_session_id'] = session_id
        
        # Get or create chat session
        chat_session = ChatSession.query.filter_by(session_id=session_id).first()
        if not chat_session:
            chat_session = ChatSession(
                session_id=session_id,
                user_id=current_user.id if current_user.is_authenticated else None,
                user_email=current_user.email if current_user.is_authenticated else None,
                user_name=current_user.username if current_user.is_authenticated else 'Guest'
            )
            db.session.add(chat_session)
            db.session.commit()
        
        # Save user message
        user_message = ChatMessage(
            chat_session_id=chat_session.id,
            user_id=current_user.id if current_user.is_authenticated else None,
            message=message_text,
            is_admin=False
        )
        db.session.add(user_message)
        
        # Send email notification to admin (only for new messages)
        try:
            send_admin_chat_notification(chat_session, message_text)
            print(f"✓ Admin notification sent for chat from {chat_session.user_name or 'Guest'}")
        except Exception as e:
            print(f"✗ Admin notification error: {e}")
        
        # Send auto-reply if not sent before
        auto_reply_sent = False
        if not chat_session.auto_reply_sent:
            auto_reply = ChatMessage(
                chat_session_id=chat_session.id,
                message=AUTO_REPLY_MESSAGE,
                is_admin=True
            )
            db.session.add(auto_reply)
            chat_session.auto_reply_sent = True
            auto_reply_sent = True
        
        # Update session timestamp
        chat_session.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'status': 'success', 
            'message': 'Message sent',
            'auto_reply_sent': auto_reply_sent
        })
    
    else:
        # Get messages
        session_id = session.get('chat_session_id')
        if not session_id:
            return jsonify({'messages': []})
        
        chat_session = ChatSession.query.filter_by(session_id=session_id).first()
        if not chat_session:
            return jsonify({'messages': []})
        
        messages = ChatMessage.query.filter_by(chat_session_id=chat_session.id).order_by(ChatMessage.created_at).all()
        
        return jsonify({
            'messages': [{
                'id': m.id,
                'text': m.message,
                'is_admin': m.is_admin,
                'time': m.created_at.strftime('%I:%M %p'),
                'timestamp': m.created_at.isoformat(),
                'sender': 'Support' if m.is_admin else 'You'
            } for m in messages]
        })

@bp.route('/admin/dashboard')
@login_required
def admin_dashboard():
    """Admin dashboard for chat"""
    if not current_user.is_admin:
        return redirect(url_for('main.index'))
    
    # Get all active sessions
    active_sessions = ChatSession.query.filter_by(status='active').order_by(ChatSession.updated_at.desc()).all()
    
    # Get session counts
    total_sessions = ChatSession.query.count()
    active_count = ChatSession.query.filter_by(status='active').count()
    
    return render_template('chat/admin_dashboard.html', 
                         sessions=active_sessions,
                         total_sessions=total_sessions,
                         active_count=active_count)

@bp.route('/admin/session/<int:session_id>')
@login_required
def admin_session(session_id):
    """View individual chat session by ID"""
    if not current_user.is_admin:
        return redirect(url_for('main.index'))
    
    chat_session = ChatSession.query.get_or_404(session_id)
    messages = ChatMessage.query.filter_by(chat_session_id=session_id).order_by(ChatMessage.created_at).all()
    
    # Mark messages as read
    for msg in messages:
        if not msg.is_admin and not msg.is_read:
            msg.is_read = True
    db.session.commit()
    
    return render_template('chat/admin_session.html', session=chat_session, messages=messages)

@bp.route('/admin/send', methods=['POST'])
@login_required
def admin_send():
    """Send message as admin"""
    if not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.json
    session_id = data.get('session_id')
    message_text = data.get('message')
    
    if not message_text:
        return jsonify({'error': 'Message is required'}), 400
    
    # Get chat session by ID
    chat_session = ChatSession.query.get(session_id)
    if not chat_session:
        return jsonify({'error': 'Session not found'}), 404
    
    # Save admin message
    chat_message = ChatMessage(
        chat_session_id=chat_session.id,
        message=message_text,
        is_admin=True
    )
    db.session.add(chat_message)
    
    # Update session timestamp
    chat_session.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({'status': 'success'})

@bp.route('/admin/close-session/<int:session_id>', methods=['POST'])
@login_required
def close_session(session_id):
    """Close a chat session"""
    if not current_user.is_admin:
        return redirect(url_for('main.index'))
    
    chat_session = ChatSession.query.get_or_404(session_id)
    chat_session.status = 'closed'
    db.session.commit()
    
    flash('Chat session closed successfully.', 'success')
    return redirect(url_for('chat.admin_dashboard'))

@bp.route('/admin/send-email-reply/<int:session_id>', methods=['POST'])
@login_required
def send_email_reply(session_id):
    """Send reply via email to customer"""
    if not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 401
    
    chat_session = ChatSession.query.get_or_404(session_id)
    data = request.json
    message_text = data.get('message')
    
    if not chat_session.user_email:
        return jsonify({'error': 'No email address available'}), 400
    
    # Send email to customer
    subject = f"Reply from Awwal Investment Support"
    
    body = f"""
    <html>
    <head>
        <style>
            body {{ font-family: 'Segoe UI', Arial, sans-serif; }}
            .container {{ max-width: 600px; margin: auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 15px; text-align: center; }}
            .content {{ padding: 20px; }}
            .message {{ background: #f8f9fa; padding: 15px; border-radius: 8px; margin: 10px 0; border-left: 4px solid #667eea; }}
            .button {{ background: #667eea; color: white; padding: 10px 20px; text-decoration: none; border-radius: 25px; display: inline-block; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h2>Awwal Investment Support</h2>
            </div>
            <div class="content">
                <p>Hello {chat_session.user_name or 'Customer'},</p>
                <p>Thank you for contacting us. Here's our response to your inquiry:</p>
                <div class="message">
                    {message_text}
                </div>
                <p>You can continue this conversation by replying to this email or visiting our live chat:</p>
                <div style="text-align: center;">
                    <a href="http://localhost:5000" class="button">Visit Our Store</a>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    
    send_email(chat_session.user_email, subject, body)
    
    # Also save as chat message
    chat_message = ChatMessage(
        chat_session_id=chat_session.id,
        message=f"[Email Reply] {message_text}",
        is_admin=True
    )
    db.session.add(chat_message)
    db.session.commit()
    
    return jsonify({'status': 'success'})

@bp.route('/admin/customer-chat/<int:customer_id>')
@login_required
def customer_chat(customer_id):
    """Start or get chat session for a specific customer"""
    if not current_user.is_admin:
        return redirect(url_for('main.index'))
    
    customer = User.query.get_or_404(customer_id)
    
    # Check if there's an existing chat session for this customer
    chat_session = ChatSession.query.filter_by(user_id=customer_id, status='active').first()
    
    if not chat_session:
        # Create a new session for this customer
        session_id = secrets.token_urlsafe(32)
        chat_session = ChatSession(
            session_id=session_id,
            user_id=customer.id,
            user_email=customer.email,
            user_name=customer.username,
            status='active'
        )
        db.session.add(chat_session)
        db.session.commit()
    
    return redirect(url_for('chat.admin_session', session_id=chat_session.id))