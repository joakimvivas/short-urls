import json
import os
from cryptography.fernet import Fernet
from dotenv import load_dotenv
from .models import URL

load_dotenv()
DATA_FILE = "app/urls.json"
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
    
    # Buscar si el id ya existe y reemplazar la URL en lugar de añadirla
    for i, url_data in enumerate(data):
        if url_data["id"] == new_url.id:  # Comparación basada en id
            data[i] = new_url.dict()  # Reemplazar la entrada existente
            break
    else:
        data.append(new_url.dict())  # Añadir una nueva entrada si no existe

    # Guardar los datos actualizados, cifrados, en el archivo
    with open(DATA_FILE, 'wb') as f:
        encrypted_data = encrypt_data(data)
        f.write(encrypted_data)

