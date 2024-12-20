# app/routers/url_management.py
import re
from fastapi import APIRouter, HTTPException, Depends, Request, Form
from fastapi.responses import RedirectResponse
from ..database import read_urls, write_url, encrypt_data, DATA_FILE
from ..models import URL
from ..auth import require_authentication
from fastapi.templating import Jinja2Templates
from datetime import datetime
from typing import Optional

templates = Jinja2Templates(directory="app/templates")

router = APIRouter(include_in_schema=False)

SHORT_NAME_REGEX = re.compile(r"^[A-Za-z0-9_]+$")

# Show the result of the shortened URL
@router.get("/result/{short_name}", dependencies=[Depends(require_authentication)])
async def result(short_name: str, request: Request):
    data = read_urls()
    url = next((item for item in data if item['short_name'] == short_name), None)
    if not url:
        raise HTTPException(status_code=404, detail="URL not found")
    return templates.TemplateResponse("result.html", {"request": request, "url": url})

# List the URLs
@router.get("/urls", dependencies=[Depends(require_authentication)])
async def list_urls(request: Request):
    data = read_urls()
    return templates.TemplateResponse("urls.html", {"request": request, "urls": data})

# Edit form for a specific short URL
@router.get("/edit-url/{short_name}")
async def edit_url_form(short_name: str, request: Request, user: str = Depends(require_authentication)):
    data = read_urls()
    url_data = next((item for item in data if item["short_name"] == short_name), None)
    if not url_data:
        raise HTTPException(status_code=404, detail="URL not found")
    return templates.TemplateResponse("edit_url.html", {"request": request, "url": url_data})

# Save edited URL
@router.post("/edit-url/{url_id}")
async def edit_url(
    url_id: str,
    original_url: str = Form(...),
    new_short_name: str = Form(...),
    description: str = Form(None),
    expirable: bool = Form(False),
    user: str = Depends(require_authentication)
):
    # Validación de short_name para evitar caracteres no permitidos
    if not SHORT_NAME_REGEX.match(new_short_name):
        raise HTTPException(
            status_code=400,
            detail="Short name can only contain alphanumeric characters and underscores."
        )

    data = read_urls()
    for url_data in data:
        if url_data["id"] == url_id:
            url_data["original_url"] = original_url
            url_data["short_name"] = new_short_name
            url_data["description"] = description
            url_data["expirable"] = expirable
            write_url(URL(**url_data))
            return RedirectResponse(url="/urls", status_code=302)

    raise HTTPException(status_code=404, detail="URL not found")

# Delete a URL
@router.get("/delete-url/{url_id}")
async def delete_url(url_id: str, user: str = Depends(require_authentication)):
    data = read_urls()
    
    data = [url_data for url_data in data if url_data["id"] != url_id]

    with open(DATA_FILE, 'wb') as f:
        encrypted_data = encrypt_data(data)
        f.write(encrypted_data)

    return RedirectResponse(url="/urls", status_code=302)
