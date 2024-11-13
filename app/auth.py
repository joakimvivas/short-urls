# app/auth.py
from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import secrets
from dotenv import load_dotenv
import os

# Cargar variables de entorno desde .env
load_dotenv()

# Usuario y contraseña desde el archivo .env
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")

security = HTTPBasic()

def get_user(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, ADMIN_USERNAME)
    correct_password = secrets.compare_digest(credentials.password, ADMIN_PASSWORD)
    if not (correct_username and correct_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return credentials.username

def require_authentication(request: Request):
    user = request.cookies.get("user")
    if user != ADMIN_USERNAME:
        raise HTTPException(status_code=403, detail="Not authenticated")
    return user
