# app/routers/web_tokens.py
from fastapi import APIRouter, Form, Depends, Request, HTTPException
from fastapi.responses import RedirectResponse
from ..database import generate_token, read_tokens, renew_token_by_id, delete_token_by_id
from ..auth import require_authentication
from fastapi.templating import Jinja2Templates
import logging

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

templates = Jinja2Templates(directory="app/templates")
router = APIRouter(include_in_schema=False)

# Managing tokens (GET /tokens)
@router.get("/", dependencies=[Depends(require_authentication)])
async def manage_tokens(request: Request):
    logger.info("Accessing /tokens endpoint")
    tokens = read_tokens()
    return templates.TemplateResponse("tokens.html", {"request": request, "tokens": tokens})

# Endpoint to create a new token (POST /tokens/create)
@router.post("/create", dependencies=[Depends(require_authentication)])
async def create_token(description: str = Form(...)):
    logger.info(f"Creating a new token with description: {description}")
    token = generate_token(description)
    logger.info(f"Generated token: {token}")
    return RedirectResponse(url="/tokens/", status_code=302)

# Endpoint to renew a token (POST /tokens/renew/{token_id})
@router.post("/renew/{token_id}", dependencies=[Depends(require_authentication)])
async def renew_token(token_id: str):
    logger.info(f"Renewing token with ID: {token_id}")
    if not renew_token_by_id(token_id):
        raise HTTPException(status_code=404, detail="Token not found")
    return RedirectResponse(url="/tokens/", status_code=302)

# Endpoint to delete a token (POST /tokens/delete/{token_id})
@router.post("/delete/{token_id}", dependencies=[Depends(require_authentication)])
async def delete_token(token_id: str):
    logger.info(f"Deleting token with ID: {token_id}")
    if not delete_token_by_id(token_id):
        raise HTTPException(status_code=404, detail="Token not found")
    return RedirectResponse(url="/tokens/", status_code=302)