from flask import Flask, jsonify
from supabase_simple import supabase

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({
        "message": "Awwal Investment API is running!",
        "status": "connected"
    })

@app.route('/products')
def get_products():
    try:
        products = supabase.get_products()
        return jsonify(products)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/test-db')
def test_db():
    try:
        # Test connection
        products = supabase.get_products()
        return jsonify({
            "connected": True,
            "message": "Successfully connected to Supabase!",
            "product_count": len(products)
        })
    except Exception as e:
        return jsonify({
            "connected": False,
            "error": str(e)
        }), 500

if __name__ == '__main__':
    print("Starting server...")
    print("Test your connection at: http://127.0.0.1:5000/test-db")
    app.run(debug=True)