# app/routers/url_shortening.py
from fastapi import APIRouter, Form, Depends, Request
from fastapi.responses import RedirectResponse
from ..database import read_urls, write_url
from ..models import URL
from ..auth import require_authentication
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="app/templates")

router = APIRouter(include_in_schema=False)

# Show the form to shorten a URL
@router.get("/shorten-url", dependencies=[Depends(require_authentication)])
async def shorten_url_form(request: Request):
    return templates.TemplateResponse("shorten_url.html", {"request": request})

# Shorten a URL
@router.post("/shorten-url", dependencies=[Depends(require_authentication)])
async def shorten_url(
    original_url: str = Form(...),
    short_name: str = Form(...),
    description: str = Form(None),
):
    new_url = URL(id=len(read_urls()) + 1, original_url=original_url, short_name=short_name, description=description, created_by="admin")
    write_url(new_url)
    return RedirectResponse(url=f"/result/{short_name}", status_code=302)
