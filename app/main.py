# app/main.py
from fastapi import FastAPI
from .routers import authentication, url_shortening, url_management, redirection

app = FastAPI()

# Registrar los routers
app.include_router(authentication.router)
app.include_router(url_shortening.router)
app.include_router(url_management.router)
app.include_router(redirection.router)
