from flask import Blueprint, render_template, request, jsonify
from app.models import Product, Category
from app.extensions import db
from sqlalchemy import or_

bp = Blueprint('search', __name__, url_prefix='/search')

@bp.route('/advanced_search')
def advanced_search():
    """Advanced search with filters"""
    query = request.args.get('q', '')
    category_id = request.args.get('category', '')
    min_price = request.args.get('min_price', '')
    max_price = request.args.get('max_price', '')
    sort_by = request.args.get('sort', 'newest')
    
    # Base query
    products_query = Product.query
    
    # Search by name or description
    if query:
        products_query = products_query.filter(
            or_(
                Product.name.contains(query),
                Product.description.contains(query)
            )
        )
    
    # Filter by category
    if category_id and category_id.isdigit():
        products_query = products_query.filter_by(category_id=int(category_id))
    
    # Filter by price range
    if min_price and min_price.isdigit():
        products_query = products_query.filter(Product.price >= float(min_price))
    if max_price and max_price.isdigit():
        products_query = products_query.filter(Product.price <= float(max_price))
    
    # Sort results
    if sort_by == 'price_asc':
        products_query = products_query.order_by(Product.price.asc())
    elif sort_by == 'price_desc':
        products_query = products_query.order_by(Product.price.desc())
    elif sort_by == 'name_asc':
        products_query = products_query.order_by(Product.name.asc())
    elif sort_by == 'oldest':
        products_query = products_query.order_by(Product.created_at.asc())
    else:  # newest
        products_query = products_query.order_by(Product.created_at.desc())
    
    products = products_query.all()
    categories = Category.query.all()
    
    # Get price range for filter display
    price_range = db.session.query(
        db.func.min(Product.price),
        db.func.max(Product.price)
    ).first()
    
    return render_template('search/advanced_search.html',
                         products=products,
                         categories=categories,
                         query=query,
                         selected_category=category_id,
                         min_price=min_price,
                         max_price=max_price,
                         sort_by=sort_by,
                         min_possible=price_range[0] or 0,
                         max_possible=price_range[1] or 1000)

@bp.route('/autocomplete')
def autocomplete():
    """Search suggestions for autocomplete"""
    query = request.args.get('q', '')
    if len(query) < 2:
        return jsonify([])
    
    products = Product.query.filter(
        or_(
            Product.name.contains(query),
            Product.description.contains(query)
        )
    ).limit(10).all()
    
    # Simple suggestions with just names
    suggestions = [{'id': p.id, 'name': p.name} for p in products]
    
    return jsonify(suggestions)