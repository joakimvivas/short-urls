# app/routers/api_urls.py
from fastapi import APIRouter, HTTPException, Header, Depends, Form
from ..database import read_urls, write_url, validate_token, DATA_FILE, encrypt_data
from ..models import URL
from typing import Optional

router = APIRouter(tags=["API V1"])

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
    description: str = Form(None)
):
    new_url = URL(id=len(read_urls()) + 1, original_url=original_url, short_name=short_name, description=description, created_by="api_user")
    write_url(new_url)
    return {"message": "URL created", "url": new_url}

# Edit a URL
@router.put("/api/v1/urls/{url_id}", dependencies=[Depends(api_token_dependency)])
async def update_url(
    url_id: int,
    original_url: Optional[str] = Form(None),
    short_name: Optional[str] = Form(None),
    description: Optional[str] = Form(None)
):
    data = read_urls()
    for url_data in data:
        if url_data["id"] == url_id:
            # Only update the fields that are not None
            if original_url is not None:
                url_data["original_url"] = original_url
            if short_name is not None:
                url_data["short_name"] = short_name
            if description is not None:
                url_data["description"] = description

            # Guardar los cambios
            write_url(URL(**url_data))
            return {"message": "URL updated", "url": url_data}
    
    raise HTTPException(status_code=404, detail="URL not found")

# Delete a URL
@router.delete("/api/v1/urls/{url_id}", dependencies=[Depends(api_token_dependency)])
async def delete_url(url_id: int):
    data = read_urls()
    updated_data = [url_data for url_data in data if url_data["id"] != url_id]
    if len(data) == len(updated_data):
        raise HTTPException(status_code=404, detail="URL not found")
    with open(DATA_FILE, 'wb') as f:
        encrypted_data = encrypt_data(updated_data)
        f.write(encrypted_data)
    return {"message": "URL deleted"}
