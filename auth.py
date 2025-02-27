from functools import wraps
from flask import request, jsonify
import os

# Load the API key from environment variables
API_KEY = os.environ.get("API_KEY")

def require_api_key(func):
    """
    Decorator to enforce API key authentication for Flask routes.
    """
    @wraps(func)
    def decorated(*args, **kwargs):
        # Get the API key from the request headers
        provided_key = request.headers.get("X-API-Key")

        # Validate the API key
        if provided_key and provided_key == API_KEY:
            return func(*args, **kwargs)
        else:
            return jsonify({"error": "Unauthorized"}), 401
    return decorated