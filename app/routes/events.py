from datetime import datetime
from fastapi import APIRouter, Depends, Request, Form, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.database.models import Event, Registration, Ticket, FaceProfile, EnrollmentStatus
from app.security.session import get_current_user_from_session
from app.services.ticket_service import issue_ticket_for_registration

router = APIRouter(prefix="/events", tags=["events"])
templates = Jinja2Templates(directory="app/templates")

@router.get("", response_class=HTMLResponse)
def list_events_page(request: Request, db: Session = Depends(get_db)):
    events = db.query(Event).order_by(Event.start_at.asc()).all()
    user = get_current_user_from_session(request)
    return templates.TemplateResponse(
        request=request,
        name="public/events.html",
        context={"events": events, "current_user": user}
    )

@router.get("/{event_id}", response_class=HTMLResponse)
def event_details_page(event_id: str, request: Request, db: Session = Depends(get_db)):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    user = get_current_user_from_session(request)
    is_registered = False
    has_ticket = False
    ticket_id = None

    if user:
        reg = db.query(Registration).filter(
            Registration.event_id == event_id,
            Registration.user_id == user["user_id"]
        ).first()
        if reg:
            is_registered = True
            ticket = db.query(Ticket).filter(Ticket.registration_id == reg.id).first()
            if ticket:
                has_ticket = True
                ticket_id = ticket.id

    return templates.TemplateResponse(
        request=request,
        name="public/event_details.html",
        context={
            "event": event,
            "current_user": user,
            "is_registered": is_registered,
            "has_ticket": has_ticket,
            "ticket_id": ticket_id
        }
    )

@router.post("/{event_id}/register")
def register_for_event(event_id: str, request: Request, db: Session = Depends(get_db)):
    user = get_current_user_from_session(request)
    if not user:
        return RedirectResponse(f"/auth/login?next=/events/{event_id}", status_code=status.HTTP_302_FOUND)

    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    # Check capacity
    count = db.query(Registration).filter(Registration.event_id == event_id).count()
    if count >= event.capacity:
        raise HTTPException(status_code=400, detail="Event has reached maximum capacity")

    # Check duplicate
    existing = db.query(Registration).filter(
        Registration.event_id == event_id,
        Registration.user_id == user["user_id"]
    ).first()
    if existing:
        return RedirectResponse(f"/events/{event_id}", status_code=status.HTTP_302_FOUND)

    reg = Registration(
        event_id=event_id,
        user_id=user["user_id"],
        status="CONFIRMED"
    )
    db.add(reg)
    db.commit()
    db.refresh(reg)

    # Check if face profile is already completed; if so, issue ticket immediately!
    face_profile = db.query(FaceProfile).filter(FaceProfile.user_id == user["user_id"]).first()
    if face_profile and face_profile.enrollment_status == EnrollmentStatus.COMPLETED:
        issue_ticket_for_registration(db, reg.id)
        return RedirectResponse("/participant/tickets", status_code=status.HTTP_302_FOUND)
    else:
        # Prompt to complete face enrollment
        return RedirectResponse("/participant/enrollment", status_code=status.HTTP_302_FOUND)

