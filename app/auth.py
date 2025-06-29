# auth.py

from werkzeug.security import generate_password_hash, check_password_hash

def hash_password(password):
    """Hash a plain text password."""
    return generate_password_hash(password)

def verify_password(hashed_password, plain_password):
    """Check if the plain password matches the hashed one."""
    return check_password_hash(hashed_password, plain_password)
