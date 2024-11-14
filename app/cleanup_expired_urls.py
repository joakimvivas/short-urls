# cleanup_expired_urls.py
import json
import os
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
from dotenv import load_dotenv

load_dotenv()
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")
DATA_FILE = "app/storage/urls.json"
SETTINGS_FILE = "app/storage/settings.json"

# Load the encryption key from the .env file
cipher = Fernet(ENCRYPTION_KEY.encode())

def decrypt_data(encrypted_data):
    json_data = cipher.decrypt(encrypted_data)
    return json.loads(json_data.decode())

def encrypt_data(data):
    json_data = json.dumps(data).encode()
    return cipher.encrypt(json_data)

def read_settings():
    # Default settings
    default_settings = {"expiration_days": 90}

    # Try to load settings from the file
    try:
        with open(SETTINGS_FILE, "r") as f:
            settings = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # If the file doesn't exist or has errors, write and return the default settings
        write_settings(default_settings)
        return default_settings

    # Check if there are missing keys in the settings file
    updated = False
    for key, value in default_settings.items():
        if key not in settings:
            settings[key] = value
            updated = True

    # Update the file if keys were added
    if updated:
        write_settings(settings)

    return settings

# Write settings to the file
def write_settings(settings):
    with open(SETTINGS_FILE, 'w') as f:
        json.dump(settings, f)

def read_urls():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'rb') as f:
            encrypted_data = f.read()
            if encrypted_data:
                return decrypt_data(encrypted_data)
    return []

def write_urls(data):
    with open(DATA_FILE, 'wb') as f:
        f.write(encrypt_data(data))

def cleanup_expired_urls():
    expiration_days = read_settings().get("expiration_days", 90)
    urls = read_urls()
    cutoff_date = datetime.now() - timedelta(days=expiration_days)

    # Filter URLs expirables
    active_urls = [
        url for url in urls
        if not url.get("expirable") or datetime.fromisoformat(url["created_at"]) > cutoff_date
    ]

    # Save the updated URLs
    write_urls(active_urls)
    print(f"Expired URLs cleaned up. {len(urls) - len(active_urls)} URLs removed.")
