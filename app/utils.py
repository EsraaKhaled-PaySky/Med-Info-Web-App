# utils.py

import re

def is_valid_email(email):
    """Validate email format."""
    regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(regex, email)

def is_strong_password(password):
    """
    Basic password strength check:
    At least 6 characters long.
    """
    return len(password) >= 6
