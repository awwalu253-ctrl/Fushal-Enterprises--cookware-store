# app.py - Root level entry point for Vercel
from app import create_app

# Create the Flask application from your actual app package
app = create_app()

# Vercel requires this exact variable name
application = app

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)