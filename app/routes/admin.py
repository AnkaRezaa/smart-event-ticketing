from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, Request, Form, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.database.models import User, Event, Ticket, CheckinLog, CheckinResult
from app.security.session import get_current_user_from_session
from app.ml.model_manager import model_manager
from app.ml.dataset import default_gallery

router = APIRouter(prefix="/admin", tags=["admin"])
templates = Jinja2Templates(directory="app/templates")

@router.get("/dashboard", response_class=HTMLResponse)
def admin_dashboard(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_from_session(request)
    if not user or user.get("role") != "admin":
        return RedirectResponse("/auth/login?next=/admin/dashboard", status_code=status.HTTP_302_FOUND)

    total_events = db.query(Event).count()
    total_users = db.query(User).count()
    total_tickets = db.query(Ticket).count()
    checkin_granted = db.query(CheckinLog).filter(CheckinLog.result == CheckinResult.GRANTED).count()

    recent_logs = db.query(CheckinLog).order_by(CheckinLog.created_at.desc()).limit(15).all()
    model_info = model_manager.get_active_model_info()

    return templates.TemplateResponse(
        request=request,
        name="admin/dashboard.html",
        context={
            "current_user": user,
            "total_events": total_events,
            "total_users": total_users,
            "total_tickets": total_tickets,
            "checkin_granted": checkin_granted,
            "logs": recent_logs,
            "model_info": model_info,
            "gallery_count": default_gallery.count()
        }
    )

@router.get("/events", response_class=HTMLResponse)
def admin_events_page(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_from_session(request)
    if not user or user.get("role") != "admin":
        return RedirectResponse("/auth/login", status_code=status.HTTP_302_FOUND)

    events = db.query(Event).order_by(Event.start_at.desc()).all()
    return templates.TemplateResponse(
        request=request,
        name="admin/events.html",
        context={"current_user": user, "events": events}
    )

@router.get("/events/new", response_class=HTMLResponse)
def new_event_page(request: Request):
    user = get_current_user_from_session(request)
    if not user or user.get("role") != "admin":
        return RedirectResponse("/auth/login", status_code=status.HTTP_302_FOUND)
    return templates.TemplateResponse(
        request=request,
        name="admin/events.html",
        context={"current_user": user, "events": []}
    )

@router.post("/events/new")
def create_event_action(
    request: Request,
    title: str = Form(...),
    location: str = Form(...),
    description: str = Form(None),
    start_at: str = Form(...),
    end_at: str = Form(...),
    capacity: int = Form(100),
    db: Session = Depends(get_db)
):
    user = get_current_user_from_session(request)
    if not user or user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin permissions required")

    start_dt = datetime.fromisoformat(start_at)
    end_dt = datetime.fromisoformat(end_at)

    ev = Event(
        title=title.strip(),
        description=description.strip() if description else "",
        location=location.strip(),
        start_at=start_dt,
        end_at=end_dt,
        registration_open_at=datetime.utcnow() - timedelta(days=1),
        registration_close_at=start_dt,
        checkin_open_at=start_dt - timedelta(hours=3),
        checkin_close_at=end_dt,
        capacity=capacity,
        status="ACTIVE"
    )
    db.add(ev)
    db.commit()
    return RedirectResponse("/admin/events", status_code=status.HTTP_302_FOUND)

