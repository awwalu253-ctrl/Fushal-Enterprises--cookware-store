from app import create_app

app = create_app()

# This is required for Vercel's serverless environment
if __name__ == "__main__":
    app.run()