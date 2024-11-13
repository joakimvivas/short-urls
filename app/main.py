# app/main.py
from fastapi import FastAPI
from app.routers import authentication, url_shortening, url_management, redirection, web_tokens, api_urls

app = FastAPI()

# Web router
app.include_router(authentication.router)
app.include_router(url_shortening.router)
app.include_router(url_management.router)
app.include_router(redirection.router)
app.include_router(web_tokens.router, prefix="/tokens")

# API router
app.include_router(api_urls.router)