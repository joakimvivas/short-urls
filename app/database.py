import json
import os
import secrets
from cryptography.fernet import Fernet
from dotenv import load_dotenv
from .models import URL
from typing import List, Dict
import uuid
from datetime import datetime
from uuid import uuid4

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

# Returns the next available ID based on the current data
def get_next_id(data):
    """Returns the next available ID based on the current data."""
    if not data:
        return 1
    max_id = max(item['id'] for item in data)
    return max_id + 1

# Writes a new URL to the data file
def write_url(new_url: URL):
    data = read_urls()
    url_data = new_url.dict()
    if isinstance(url_data.get("created_at"), datetime):
        url_data["created_at"] = url_data["created_at"].isoformat()

    if not url_data.get("id"):
        url_data["id"] = str(uuid4())
    else:
        url_data["id"] = str(url_data["id"])

    for i, existing_url in enumerate(data):
        if str(existing_url["id"]) == url_data["id"]:
            data[i] = url_data
            break
    else:
        data.append(url_data)

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
    token_info = {"id": str(uuid.uuid4()), "token": token, "description": description}  # Adding the UUID for the token
    write_token(token_info)
    return token

# Validate a token
def validate_token(token: str) -> bool:
    tokens = read_tokens()
    return any(t["token"] == token for t in tokens)

# Renew an existing token
def renew_token_by_id(token_id: str) -> bool:
    tokens = read_tokens()
    for token in tokens:
        if token["id"] == token_id:
            token["token"] = secrets.token_hex(16)  # Generate a new token
            with open(TOKENS_FILE, 'wb') as f:
                f.write(encrypt_data(tokens))
            return True
    return False

# Delete an existing token
def delete_token_by_id(token_id: str) -> bool:
    tokens = read_tokens()
    updated_tokens = [token for token in tokens if token["id"] != token_id]
    if len(updated_tokens) == len(tokens):  # If not deleted the token
        return False
    with open(TOKENS_FILE, 'wb') as f:
        f.write(encrypt_data(updated_tokens))
    return True