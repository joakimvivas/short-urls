import os
from cryptography.fernet import Fernet
from dotenv import load_dotenv
import json

# Cargar el archivo .env
load_dotenv()

# Obtener la clave de cifrado
encryption_key = os.getenv("ENCRYPTION_KEY")
if not encryption_key:
    raise ValueError("ENCRYPTION_KEY is missing from the environment variables")

# Crear el cifrador
cipher = Fernet(encryption_key.encode())

# Cifrar y escribir un array vacío en urls.json
with open("app/urls.json", "wb") as f:
    encrypted_data = cipher.encrypt(json.dumps([]).encode())
    f.write(encrypted_data)
