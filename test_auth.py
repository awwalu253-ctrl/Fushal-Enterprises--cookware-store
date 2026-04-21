from flask import Flask, jsonify

test_app = Flask(__name__)

@test_app.route('/')
def home():
    return jsonify({
        "status": "success",
        "message": "Test app is working!",
        "timestamp": "2025-04-21"
    })

@test_app.route('/health')
def health():
    return jsonify({"status": "healthy"})

# For Vercel
app = test_app
application = test_app

if __name__ == "__main__":
    test_app.run()