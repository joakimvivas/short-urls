from fastapi import APIRouter, HTTPException, Header, Depends, Form
from ..database import read_urls, write_url, validate_token, DATA_FILE, encrypt_data
from ..models import URL
from ..routers.settings import read_settings
from typing import Optional
from datetime import datetime
from uuid import uuid4, UUID
import re
import logging

# Configuration of logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(tags=["API V1"])

SHORT_NAME_REGEX = re.compile(r"^[A-Za-z0-9_]+$")

def api_token_dependency(api_token: str = Header(None)):
    if not validate_token(api_token):
        raise HTTPException(status_code=403, detail="Invalid API token")

# List of URLs
@router.get("/api/v1/urls", dependencies=[Depends(api_token_dependency)])
async def list_urls():
    return read_urls()

# Create a new URL
@router.post("/api/v1/urls", dependencies=[Depends(api_token_dependency)])
async def create_url(
    original_url: str = Form(...),
    short_name: str = Form(...),
    description: Optional[str] = Form(None),
    expirable: Optional[bool] = Form(True)
):
    # Validation of the short_name
    if not SHORT_NAME_REGEX.match(short_name):
        raise HTTPException(
            status_code=400,
            detail="Short name can only contain alphanumeric characters and underscores."
        )

    settings = read_settings()
    domain = settings.get("domain", "https://www.example.com")
    
    new_url = URL(
        id=str(uuid4()),
        original_url=original_url,
        short_name=short_name,
        description=description,
        created_by="api_user",
        created_at=datetime.now(),
        expirable=expirable
    )
    write_url(new_url)
    short_url = f"{domain}/{short_name}"
    return {
        "message": "URL created",
        "url": {
            "id": new_url.id,
            "original_url": original_url,
            "short_url": short_url,
            "short_name": short_name,
            "description": description,
            "created_by": "api_user",
            "expirable": expirable,
            "created_at": new_url.created_at
        }
    }

# Edit a URL
@router.put("/api/v1/urls/{url_id}", dependencies=[Depends(api_token_dependency)])
async def update_url(
    url_id: str,
    original_url: Optional[str] = Form(None),
    short_name: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    expirable: Optional[bool] = Form(None)
):
    logger.info(f"Received request to update URL with id: {url_id}")
    
    try:
        uuid_obj = UUID(url_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid URL ID format.")

    data = read_urls()
    for url_data in data:
        logger.info(f"Checking URL with id: {url_data['id']}")
        
        if url_data["id"] == str(uuid_obj):
            if original_url is not None:
                url_data["original_url"] = original_url
            if short_name is not None:
                # Validation of the short_name
                if not SHORT_NAME_REGEX.match(short_name):
                    raise HTTPException(
                        status_code=400,
                        detail="Short name can only contain alphanumeric characters and underscores."
                    )
                url_data["short_name"] = short_name
            if description is not None:
                url_data["description"] = description
            if expirable is not None:
                url_data["expirable"] = expirable
            write_url(URL(**url_data))
            logger.info(f"URL with id: {url_id} updated successfully.")
            return {"message": "URL updated", "url": url_data}
    
    logger.warning(f"URL with id: {url_id} not found.")
    raise HTTPException(status_code=404, detail="URL not found")

# Delete a URL
@router.delete("/api/v1/urls/{url_id}", dependencies=[Depends(api_token_dependency)])
async def delete_url(url_id: str):
    data = read_urls()
    updated_data = [url_data for url_data in data if url_data["id"] != url_id]
    if len(data) == len(updated_data):
        raise HTTPException(status_code=404, detail="URL not found")
    with open(DATA_FILE, 'wb') as f:
        encrypted_data = encrypt_data(updated_data)
        f.write(encrypted_data)
    return {"message": "URL deleted"}
