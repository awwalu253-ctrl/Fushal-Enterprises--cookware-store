from supabase import create_client
import os

# Your Supabase credentials
SUPABASE_URL = "https://uvvyiwwifchrafragfxd.supabase.co"
SUPABASE_KEY = "sb_publishable_yv9DSJQ5pdqHdlloOQ6lPQ_qu0yN1iw"

# Create Supabase client
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)