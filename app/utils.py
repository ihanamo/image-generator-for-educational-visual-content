# app/utils.py
import hashlib

# hash user's password
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

# Password verification
def check_password(password: str, hashed: str) -> bool:
    return hash_password(password) == hashed
