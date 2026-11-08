from fastapi import APIRouter, Depends, Request, Form, Response, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.services.auth_service import register_user, authenticate_user
from app.security.session import create_session_token, get_current_user_from_session
from app.config import settings

router = APIRouter(prefix="/auth", tags=["auth"])
templates = Jinja2Templates(directory="app/templates")

@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    user = get_current_user_from_session(request)
    if user:
        if user.get("role") == "admin":
            return RedirectResponse("/admin/dashboard", status_code=status.HTTP_302_FOUND)
        elif user.get("role") == "operator":
            return RedirectResponse("/operator/dashboard", status_code=status.HTTP_302_FOUND)
        return RedirectResponse("/participant/dashboard", status_code=status.HTTP_302_FOUND)
    return templates.TemplateResponse(request=request, name="public/login.html", context={"current_user": None})

@router.post("/login")
def login_action(
    request: Request,
    response: Response,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    user = authenticate_user(db, email, password)
    if not user:
        return templates.TemplateResponse(
            request=request,
            name="public/login.html",
            context={"error_msg": "Invalid email or password", "current_user": None},
            status_code=status.HTTP_401_UNAUTHORIZED
        )

    session_token = create_session_token({
        "user_id": user.id,
        "name": user.name,
        "email": user.email,
        "role": user.role.value
    })

    redirect_url = "/participant/dashboard"
    if user.role.value == "admin":
        redirect_url = "/admin/dashboard"
    elif user.role.value == "operator":
        redirect_url = "/operator/dashboard"

    res = RedirectResponse(redirect_url, status_code=status.HTTP_302_FOUND)
    res.set_cookie(
        key=settings.SESSION_COOKIE_NAME,
        value=session_token,
        max_age=settings.SESSION_MAX_AGE_SECONDS,
        httponly=True,
        secure=settings.SECURE_COOKIE,
        samesite="lax"
    )
    return res

@router.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    user = get_current_user_from_session(request)
    if user:
        return RedirectResponse("/participant/dashboard", status_code=status.HTTP_302_FOUND)
    return templates.TemplateResponse(request=request, name="public/register.html", context={"current_user": None})

@router.post("/register")
def register_action(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    role: str = Form("participant"),
    db: Session = Depends(get_db)
):
    try:
        user = register_user(db, name, email, password, role)
        session_token = create_session_token({
            "user_id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role.value
        })

        redirect_url = "/participant/dashboard"
        if user.role.value == "admin":
            redirect_url = "/admin/dashboard"
        elif user.role.value == "operator":
            redirect_url = "/operator/dashboard"

        res = RedirectResponse(redirect_url, status_code=status.HTTP_302_FOUND)
        res.set_cookie(
            key=settings.SESSION_COOKIE_NAME,
            value=session_token,
            max_age=settings.SESSION_MAX_AGE_SECONDS,
            httponly=True,
            secure=settings.SECURE_COOKIE,
            samesite="lax"
        )
        return res
    except ValueError as e:
        return templates.TemplateResponse(
            request=request,
            name="public/register.html",
            context={"error_msg": str(e), "current_user": None},
            status_code=status.HTTP_400_BAD_REQUEST
        )

@router.get("/logout")
def logout_action():
    res = RedirectResponse("/", status_code=status.HTTP_302_FOUND)
    res.delete_cookie(settings.SESSION_COOKIE_NAME)
    return res

