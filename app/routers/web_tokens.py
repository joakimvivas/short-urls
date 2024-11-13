# app/routers/web_tokens.py
from fastapi import APIRouter, Form, Depends, Request
from fastapi.responses import RedirectResponse
from ..database import generate_token, read_tokens
from ..auth import require_authentication
from fastapi.templating import Jinja2Templates
import logging

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

templates = Jinja2Templates(directory="app/templates")
router = APIRouter(include_in_schema=False)

# Managing tokens
@router.get("/", dependencies=[Depends(require_authentication)])
async def manage_tokens(request: Request):
    logger.info("Accessing /tokens endpoint")  # Log inicial para verificar acceso

    # Leer tokens y verificar el resultado
    tokens = read_tokens()
    logger.info(f"Tokens read from file: {tokens}")

    # Renderizar la plantilla tokens.html
    response = templates.TemplateResponse("tokens.html", {"request": request, "tokens": tokens})
    logger.info("Rendering tokens.html template with tokens data")

    return response

# Endpoint to create a new token
@router.post("/create", dependencies=[Depends(require_authentication)])
async def create_token(description: str = Form(...)):
    logger.info(f"Creating a new token with description: {description}")
    token = generate_token(description)
    logger.info(f"Generated token: {token}")
    return RedirectResponse(url="/tokens/", status_code=302)
