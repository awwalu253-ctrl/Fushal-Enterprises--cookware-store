from flask import Flask, jsonify
from supabase_client import supabase

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({"message": "Supabase is connected!"})

@app.route('/products')
def get_products():
    # Fetch all products from Supabase
    response = supabase.table('products').select('*').execute()
    return jsonify(response.data)

@app.route('/users')
def get_users():
    # Fetch all users from Supabase
    response = supabase.table('users').select('*').execute()
    return jsonify(response.data)

if __name__ == '__main__':
    app.run(debug=True)