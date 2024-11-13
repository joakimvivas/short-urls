# app/routers/redirection.py
from fastapi import APIRouter, HTTPException
from fastapi.responses import RedirectResponse
from ..database import read_urls

router = APIRouter(include_in_schema=False)

# Endpoint to redirect to a URL (Public Endpoint)
@router.get("/{short_name}")
async def redirect_to_url(short_name: str):
    data = read_urls()
    url_data = next((item for item in data if item["short_name"] == short_name), None)
    if url_data:
        return RedirectResponse(url=url_data["original_url"])
    else:
        raise HTTPException(status_code=404, detail="Not Found")
