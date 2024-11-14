# app/main.py
from fastapi import FastAPI
from app.routers import authentication, url_shortening, url_management, redirection, web_tokens, api_urls, settings
import os
import json

app = FastAPI()

# Validation of the initialization of the application
@app.on_event("startup")
async def startup_event():
    files_with_defaults = {
        "app/storage/settings.json": {"expiration_days": 90}
    }

    # Creating each file
    for filepath, default_content in files_with_defaults.items():
        if not os.path.exists(filepath):
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, 'w') as f:
                json.dump(default_content, f)

# Routes
app.include_router(authentication.router)
app.include_router(url_shortening.router)
app.include_router(url_management.router)
app.include_router(redirection.router)
app.include_router(web_tokens.router, prefix="/tokens")
app.include_router(settings.router, prefix="/settings")
app.include_router(api_urls.router)
