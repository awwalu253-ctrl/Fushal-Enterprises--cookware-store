from flask import Flask, jsonify, render_template_string
import requests
import os

app = Flask(__name__)

# Supabase configuration from environment variables
SUPABASE_URL = os.environ.get('SUPABASE_URL', 'https://uvvyiwwifchrafragfxd.supabase.co')
SUPABASE_KEY = os.environ.get('SUPABASE_KEY', 'sb_publishable_yv9DSJQ5pdqHdlloOQ6lPQ_qu0yN1iw')

# HTML Template
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Awwal Investment - Premium Cooking Utensils</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #FFF8F0; }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        header { background: linear-gradient(135deg, #E67E22, #F39C12); color: white; padding: 60px 20px; text-align: center; }
        h1 { font-size: 3rem; margin-bottom: 10px; }
        .products { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 30px; margin-top: 40px; }
        .product-card { background: white; border-radius: 15px; overflow: hidden; box-shadow: 0 5px 15px rgba(0,0,0,0.1); transition: transform 0.3s; }
        .product-card:hover { transform: translateY(-5px); }
        .product-info { padding: 20px; }
        .product-name { font-size: 1.2rem; font-weight: bold; color: #2C3E50; margin-bottom: 10px; }
        .product-price { color: #E67E22; font-size: 1.5rem; font-weight: bold; margin: 10px 0; }
        .product-stock { color: #27ae60; font-size: 0.9rem; }
        .btn { display: inline-block; background: linear-gradient(135deg, #E67E22, #F39C12); color: white; padding: 10px 20px; text-decoration: none; border-radius: 25px; margin-top: 10px; transition: all 0.3s; }
        .btn:hover { transform: translateY(-2px); box-shadow: 0 5px 15px rgba(230,126,34,0.3); }
        footer { text-align: center; padding: 30px; background: #2C3E50; color: white; margin-top: 50px; }
        .status { background: #27ae60; color: white; padding: 10px; text-align: center; border-radius: 10px; margin: 20px 0; }
    </style>
</head>
<body>
    <header>
        <h1>🏺 Awwal Investment</h1>
        <p>Premium Cooking Utensils for Your Kitchen</p>
    </header>
    
    <div class="container">
        <div class="status">
            ✅ Connected to Database | {{ product_count }} Products Available
        </div>
        
        <div class="products">
            {% for product in products %}
            <div class="product-card">
                <div class="product-info">
                    <div class="product-name">{{ product.name }}</div>
                    <div class="product-price">${{ "%.2f"|format(product.price) }}</div>
                    <div class="product-stock">📦 {{ product.stock }} units in stock</div>
                    <a href="#" class="btn">Add to Cart</a>
                </div>
            </div>
            {% endfor %}
        </div>
    </div>
    
    <footer>
        <p>&copy; 2025 Awwal Investment - Premium Cooking Utensils. All rights reserved.</p>
    </footer>
</body>
</html>
'''

@app.route('/')
def home():
    try:
        headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
        url = f"{SUPABASE_URL}/rest/v1/products?select=*"
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            products = response.json()
            return render_template_string(HTML_TEMPLATE, products=products, product_count=len(products))
        else:
            return f"Error fetching products: {response.status_code}"
    except Exception as e:
        return f"Error: {str(e)}"

@app.route('/api/products')
def api_products():
    headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
    url = f"{SUPABASE_URL}/rest/v1/products?select=*"
    response = requests.get(url, headers=headers)
    return response.json()

@app.route('/health')
def health():
    return {"status": "healthy", "database": "connected"}

# This is required for Vercel
app.debug = False

if __name__ == '__main__':
    app.run()