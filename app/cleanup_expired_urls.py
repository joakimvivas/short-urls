import schedule
import time
import json
import os
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
from dotenv import load_dotenv
import logging

# Configuración de logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Load environment variables
load_dotenv()
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")
DATA_FILE = "/app/storage/urls.json"
SETTINGS_FILE = "/app/storage/settings.json"

# Load the encryption key
try:
    cipher = Fernet(ENCRYPTION_KEY.encode())
except Exception as e:
    logging.error(f"Failed to initialize encryption cipher: {e}")
    raise

def decrypt_data(encrypted_data):
    try:
        json_data = cipher.decrypt(encrypted_data)
        return json.loads(json_data.decode())
    except Exception as e:
        logging.error(f"Error decrypting data: {e}")
        return []

def encrypt_data(data):
    try:
        json_data = json.dumps(data).encode()
        return cipher.encrypt(json_data)
    except Exception as e:
        logging.error(f"Error encrypting data: {e}")
        return b""

def read_settings():
    # Default settings
    default_settings = {
        "expiration_days": 90,
        "schedule_interval": 0.25  # Default interval in hours (every 15 minutes)
    }

    try:
        logging.info("Attempting to read settings from settings.json...")
        with open(SETTINGS_FILE, "r") as f:
            settings = json.load(f)
            logging.info(f"Settings loaded successfully: {settings}")
    except FileNotFoundError:
        logging.warning("Settings file not found. Writing default settings.")
        write_settings(default_settings)
        return default_settings
    except json.JSONDecodeError as e:
        logging.error(f"Settings file is not a valid JSON. Error: {e}")
        write_settings(default_settings)
        return default_settings

    # Add missing keys if any
    updated = False
    for key, value in default_settings.items():
        if key not in settings:
            logging.warning(f"Missing key in settings: {key}. Adding default value: {value}")
            settings[key] = value
            updated = True

    if updated:
        logging.info("Updating settings file with new default keys.")
        write_settings(settings)

    return settings

def write_settings(settings):
    try:
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(settings, f)
    except Exception as e:
        logging.error(f"Error writing settings: {e}")

def read_urls():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'rb') as f:
                encrypted_data = f.read()
                if encrypted_data:
                    return decrypt_data(encrypted_data)
        except Exception as e:
            logging.error(f"Error reading URLs: {e}")
    return []

def write_urls(data):
    try:
        with open(DATA_FILE, 'wb') as f:
            f.write(encrypt_data(data))
    except Exception as e:
        logging.error(f"Error writing URLs: {e}")

def cleanup_expired_urls():
    try:
        settings = read_settings()
        expiration_days = settings.get("expiration_days", 90)
        urls = read_urls()
        cutoff_date = datetime.now() - timedelta(days=expiration_days)

        # Filter URLs expirables
        active_urls = [
            url for url in urls
            if not url.get("expirable") or datetime.fromisoformat(url["created_at"]) > cutoff_date
        ]

        # Save the updated URLs
        write_urls(active_urls)
        logging.info(f"Expired URLs cleaned up. {len(urls) - len(active_urls)} URLs removed.")
    except Exception as e:
        logging.error(f"Error during cleanup: {e}")

def schedule_cleanup():
    try:
        settings = read_settings()
        schedule_interval = settings.get("schedule_interval", 24)
        logging.info(f"Scheduling cleanup every {schedule_interval} hours.")
        schedule.every(schedule_interval).hours.do(cleanup_expired_urls)
    except Exception as e:
        logging.error(f"Error scheduling cleanup: {e}")

if __name__ == "__main__":
    logging.info("Starting URL cleanup scheduler...")
    cleanup_expired_urls()  # Run once at startup
    schedule_cleanup()
    while True:
        schedule.run_pending()
        time.sleep(1)
