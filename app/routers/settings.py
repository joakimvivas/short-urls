# app/routers/settings.py
from fastapi import APIRouter, Form, Request, Depends
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from ..auth import require_authentication
import logging
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(include_in_schema=False)
templates = Jinja2Templates(directory="app/templates")

SETTINGS_FILE = "app/storage/settings.json"

# Read settings file
def read_settings():
    default_settings = {"expiration_days": 90}
    try:
        with open(SETTINGS_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        write_settings(default_settings)
        return default_settings

# Write settings to file
def write_settings(settings):
    with open(SETTINGS_FILE, 'w') as f:
        json.dump(settings, f)

# Display settings page
@router.get("/", dependencies=[Depends(require_authentication)])
async def settings_page(request: Request):
    settings = read_settings()
    return templates.TemplateResponse("settings.html", {"request": request, "settings": settings})

# Update settings
@router.post("/", dependencies=[Depends(require_authentication)])
async def update_settings(expiration_days: int = Form(...)):
    settings = {"expiration_days": expiration_days}
    write_settings(settings)
    logger.info(f"Settings updated successfully to {settings['expiration_days']} days.")
    return RedirectResponse(url="/settings/", status_code=302)
