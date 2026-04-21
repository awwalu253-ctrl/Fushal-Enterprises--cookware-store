import sys
import traceback
from app import create_app

try:
    print("Starting app creation...")
    app = create_app()
    application = app
    print("App created successfully!")
except Exception as e:
    print(f"ERROR: {e}")
    print(traceback.format_exc())
    
    # Create a fallback app that shows the error
    from flask import Flask
    app = Flask(__name__)
    application = app
    
    @app.route('/')
    def error_page():
        error_msg = f"""
        <html>
        <head><title>Startup Error</title></head>
        <body style="font-family: monospace; padding: 20px;">
            <h1>Application Startup Error</h1>
            <pre>{traceback.format_exc()}</pre>
        </body>
        </html>
        """
        return error_msg

if __name__ == "__main__":
    app.run()