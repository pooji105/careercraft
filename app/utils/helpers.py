import os
from datetime import datetime

def get_openrouter_api_key():
    """Get the OpenRouter API key from environment variables."""
    return os.getenv('OPENROUTER_API_KEY')

def format_date(date_obj):
    """Format a date object to a readable string."""
    if date_obj:
        return date_obj.strftime('%B %d, %Y')
    return ''

def get_file_extension(filename):
    """Get the file extension from a filename."""
    if filename:
        return filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
    return '' 