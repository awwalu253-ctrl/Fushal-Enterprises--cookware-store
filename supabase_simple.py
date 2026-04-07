import requests
import json

SUPABASE_URL = "https://uvvyiwwifchrafragfxd.supabase.co"
SUPABASE_KEY = "sb_publishable_yv9DSJQ5pdqHdlloOQ6lPQ_qu0yN1iw"

class SupabaseClient:
    def __init__(self):
        self.headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "application/json"
        }
    
    def get_products(self):
        url = f"{SUPABASE_URL}/rest/v1/products?select=*"
        response = requests.get(url, headers=self.headers)
        return response.json()
    
    def add_product(self, name, price, stock):
        url = f"{SUPABASE_URL}/rest/v1/products"
        data = {
            "name": name,
            "price": price,
            "stock": stock
        }
        response = requests.post(url, headers=self.headers, json=data)
        return response.json()

# Create client
supabase = SupabaseClient()