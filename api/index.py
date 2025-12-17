"""
Vercel serverless function entry point.
This wraps the Flask app for Vercel's serverless environment.
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app import app

# Vercel serverless function handler
def handler(request, context):
    return app(request.environ, context)

# For Vercel
app = app
