import os

API_PORT = os.getenv("API_PORT", "8000")
API_HOST = os.getenv("API_HOST", f"http://localhost:{API_PORT}")
