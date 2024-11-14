# app/routers/url_shortening.py
import re
from fastapi import APIRouter, Form, Depends, Request, HTTPException
from fastapi.responses import RedirectResponse
from ..database import read_urls, write_url
from ..models import URL
from ..auth import require_authentication
from fastapi.templating import Jinja2Templates
from datetime import datetime
from uuid import uuid4

templates = Jinja2Templates(directory="app/templates")

router = APIRouter(include_in_schema=False)

SHORT_NAME_REGEX = re.compile(r"^[A-Za-z0-9_]+$")

# Show the form to shorten a URL
@router.get("/shorten-url", dependencies=[Depends(require_authentication)])
async def shorten_url_form(request: Request):
    return templates.TemplateResponse("shorten_url.html", {"request": request})

# Create a new shorten a URL
@router.post("/shorten-url", dependencies=[Depends(require_authentication)])
async def shorten_url(
    original_url: str = Form(...),
    short_name: str = Form(...),
    description: str = Form(None),
    expirable: bool = Form(False)
):
    # Validation for short_name
    if not SHORT_NAME_REGEX.match(short_name):
        raise HTTPException(
            status_code=400,
            detail="Short name can only contain alphanumeric characters and underscores."
        )

    new_url = URL(
        id=str(uuid4()),
        original_url=original_url,
        short_name=short_name,
        description=description,
        created_by="admin",
        created_at=datetime.now(),
        expirable=expirable
    )
    write_url(new_url)
    return RedirectResponse(url=f"/result/{short_name}", status_code=302)
