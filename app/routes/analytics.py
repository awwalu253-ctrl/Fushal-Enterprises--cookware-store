from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from app.models import Order, Product, User, OrderItem, Review, Category
from app.extensions import db
from datetime import datetime, timedelta
from sqlalchemy import func

bp = Blueprint('analytics', __name__, url_prefix='/analytics')

@bp.route('/dashboard')
@login_required
def dashboard():
    if not current_user.is_admin:
        return redirect(url_for('main.index'))
    
    # Date ranges
    today = datetime.now()
    thirty_days_ago = today - timedelta(days=30)
    sixty_days_ago = today - timedelta(days=60)
    
    # ========== CURRENT PERIOD (last 30 days) ==========
    current_orders = Order.query.filter(Order.order_date >= thirty_days_ago).all()
    current_revenue = sum(order.total_amount for order in current_orders)
    current_order_count = len(current_orders)
    
    # ========== PREVIOUS PERIOD (30-60 days ago) ==========
    previous_orders = Order.query.filter(
        Order.order_date >= sixty_days_ago,
        Order.order_date < thirty_days_ago
    ).all()
    previous_revenue = sum(order.total_amount for order in previous_orders)
    previous_order_count = len(previous_orders)
    
    # ========== TRENDS ==========
    revenue_trend = ((current_revenue - previous_revenue) / previous_revenue * 100) if previous_revenue > 0 else 0
    orders_trend = ((current_order_count - previous_order_count) / previous_order_count * 100) if previous_order_count > 0 else 0
    
    # Average Order Value
    avg_order_value = current_revenue / current_order_count if current_order_count > 0 else 0
    previous_aov = previous_revenue / previous_order_count if previous_order_count > 0 else 0
    aov_trend = ((avg_order_value - previous_aov) / previous_aov * 100) if previous_aov > 0 else 0
    
    # ========== CUSTOMER STATISTICS ==========
    total_customers = User.query.filter_by(is_admin=False).count()
    
    # New customers trends
    new_customers_current = User.query.filter(
        User.created_at >= thirty_days_ago,
        User.is_admin == False
    ).count()
    new_customers_previous = User.query.filter(
        User.created_at >= sixty_days_ago,
        User.created_at < thirty_days_ago,
        User.is_admin == False
    ).count()
    customers_trend = ((new_customers_current - new_customers_previous) / new_customers_previous * 100) if new_customers_previous > 0 else 0
    
    # ========== TOP PRODUCTS ==========
    top_products = db.session.query(
        Product.name,
        func.sum(OrderItem.quantity).label('total_sold'),
        func.sum(OrderItem.price * OrderItem.quantity).label('total_revenue')
    ).join(OrderItem).join(Order)\
     .filter(Order.order_date >= thirty_days_ago)\
     .group_by(Product.id)\
     .order_by(func.sum(OrderItem.quantity).desc())\
     .limit(5).all()
    
    top_products_list = [{
        'name': p.name,
        'total_sold': int(p.total_sold),
        'total_revenue': float(p.total_revenue)
    } for p in top_products]
    
    # ========== DAILY SALES FOR CHART ==========
    daily_sales = db.session.query(
        func.date(Order.order_date).label('date'),
        func.sum(Order.total_amount).label('revenue')
    ).filter(Order.order_date >= thirty_days_ago)\
     .group_by(func.date(Order.order_date))\
     .order_by(func.date(Order.order_date)).all()
    
    daily_sales_list = [{'date': d.date.strftime('%m/%d'), 'revenue': float(d.revenue)} for d in daily_sales]
    
    # ========== CATEGORY SALES DISTRIBUTION ==========
    category_sales = db.session.query(
        Category.name,
        func.sum(OrderItem.price * OrderItem.quantity).label('total')
    ).join(OrderItem, Category.id == OrderItem.product_id)\
     .join(Order, OrderItem.order_id == Order.id)\
     .filter(Order.order_date >= thirty_days_ago)\
     .group_by(Category.name).all()
    
    category_sales_list = [{'name': c.name, 'total': float(c.total)} for c in category_sales]
    
    # ========== REVIEW ANALYTICS ==========
    avg_rating = db.session.query(func.avg(Review.rating)).scalar() or 0
    total_reviews = Review.query.count()
    
    # ========== KEY METRICS ==========
    # Conversion rate (simplified - would need visitor tracking)
    total_visitors = 1000  # Placeholder for actual analytics
    conversion_rate = (current_order_count / total_visitors * 100) if total_visitors > 0 else 0
    
    # Average cart value (same as AOV)
    avg_cart_value = avg_order_value
    
    # Repeat customers (customers with more than 1 order)
    repeat_customers_count = db.session.query(Order.user_id).group_by(Order.user_id).having(func.count(Order.id) > 1).count()
    repeat_customers = (repeat_customers_count / total_customers * 100) if total_customers > 0 else 0
    
    # Abandoned carts (placeholder)
    abandoned_carts = 0
    recovered_carts = 0
    
    return render_template('admin/analytics_dashboard.html',
                         # Revenue stats
                         total_revenue=current_revenue,
                         total_orders=current_order_count,
                         avg_order_value=avg_order_value,
                         
                         # Trends
                         revenue_trend=revenue_trend,
                         orders_trend=orders_trend,
                         aov_trend=aov_trend,
                         customers_trend=customers_trend,
                         
                         # Customer stats
                         total_customers=total_customers,
                         new_customers=new_customers_current,
                         
                         # Product stats
                         top_products=top_products_list,
                         
                         # Chart data
                         daily_sales=daily_sales_list,
                         category_sales=category_sales_list,
                         
                         # Review stats
                         avg_rating=avg_rating,
                         total_reviews=total_reviews,
                         
                         # Key metrics
                         conversion_rate=conversion_rate,
                         avg_cart_value=avg_cart_value,
                         repeat_customers=repeat_customers,
                         abandoned_carts=abandoned_carts)