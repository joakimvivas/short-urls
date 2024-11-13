import json
import os
import secrets
from cryptography.fernet import Fernet
from dotenv import load_dotenv
from .models import URL
from typing import List, Dict

load_dotenv()
DATA_FILE = "app/storage/urls.json"
TOKENS_FILE = "app/storage/tokens.json"
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")

if not ENCRYPTION_KEY:
    raise ValueError("ENCRYPTION_KEY is missing from the environment variables")

cipher = Fernet(ENCRYPTION_KEY.encode())

def encrypt_data(data):
    """Encrypt JSON data."""
    json_data = json.dumps(data).encode()  # Convert data to JSON bytes
    return cipher.encrypt(json_data)

def decrypt_data(encrypted_data):
    """Decrypt JSON data."""
    json_data = cipher.decrypt(encrypted_data)
    return json.loads(json_data.decode())

def read_urls():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'rb') as f:
                encrypted_data = f.read()
                if encrypted_data:
                    return decrypt_data(encrypted_data)
                else:
                    return []
        except (json.JSONDecodeError, ValueError):
            with open(DATA_FILE, 'wb') as f:
                f.write(encrypt_data([]))
            return []
    else:
        with open(DATA_FILE, 'wb') as f:
            f.write(encrypt_data([]))
        return []

def write_url(new_url: URL):
    data = read_urls()
    
    # Find the index of the existing URL with the same id
    for i, url_data in enumerate(data):
        if url_data["id"] == new_url.id:  # Comparing the id
            data[i] = new_url.dict()  # Replace the existing URL with the new one
            break
    else:
        data.append(new_url.dict())  # Adding a new URL if it doesn't exist

    # Save the updated data
    with open(DATA_FILE, 'wb') as f:
        encrypted_data = encrypt_data(data)
        f.write(encrypted_data)

# Read tokens
def read_tokens() -> List[Dict]:
    if os.path.exists(TOKENS_FILE):
        with open(TOKENS_FILE, 'rb') as f:
            encrypted_data = f.read()
            if encrypted_data:
                return decrypt_data(encrypted_data)
            else:
                return []
    else:
        # If the file doesn't exist, create an empty list and encrypt it
        with open(TOKENS_FILE, 'wb') as f:
            f.write(encrypt_data([]))
        return []

# Save tokens
def write_token(token_info: Dict):
    tokens = read_tokens()
    tokens.append(token_info)
    with open(TOKENS_FILE, 'wb') as f:
        encrypted_data = encrypt_data(tokens)
        f.write(encrypted_data)

# Generate a new token
def generate_token(description: str) -> str:
    token = secrets.token_hex(16)
    token_info = {"token": token, "description": description}
    write_token(token_info)
    return token

# Validate a token
def validate_token(token: str) -> bool:
    tokens = read_tokens()
    return any(t["token"] == token for t in tokens)