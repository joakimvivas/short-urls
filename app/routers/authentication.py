# app/routers/authentication.py
from fastapi import APIRouter, Form, Request, Depends, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.security import HTTPBasicCredentials
from ..auth import get_user, require_authentication
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="app/templates")

router = APIRouter()

# Home page
@router.get("/")
async def home(request: Request):
    if request.cookies.get("user"):
        return RedirectResponse(url="/shorten-url")
    return RedirectResponse(url="/login")

# Show the login form
@router.get("/login")
async def login(request: Request, error: str = None):
    return templates.TemplateResponse("login.html", {"request": request, "error": error})

# Login
@router.post("/login")
async def login_post(
    request: Request,
    username: str = Form(...),
    password: str = Form(...)
):
    credentials = HTTPBasicCredentials(username=username, password=password)
    try:
        user = get_user(credentials)
    except HTTPException:
        return RedirectResponse(url="/login?error=1", status_code=302)
    
    response = RedirectResponse(url="/shorten-url", status_code=302)
    response.set_cookie(key="user", value=user)
    return response

# Logout
@router.get("/logout")
async def logout():
    response = RedirectResponse(url="/login")
    response.delete_cookie(key="user")
    return response
