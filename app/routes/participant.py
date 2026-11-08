from fastapi import APIRouter, Depends, Request, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.database.models import User, Registration, Ticket, FaceProfile, FaceSample, EnrollmentStatus
from app.security.session import require_auth, get_current_user_from_session
from app.schemas.schemas import FacialSampleUpload, CompleteEnrollmentRequest
from app.services.enrollment_service import save_sample_and_extract_feature, complete_user_enrollment
from app.services.ticket_service import generate_qr_code_image_base64, issue_ticket_for_registration

router = APIRouter(tags=["participant"])
templates = Jinja2Templates(directory="app/templates")

@router.get("/participant/dashboard", response_class=HTMLResponse)
def participant_dashboard(request: Request, db: Session = Depends(get_db)):
    user_payload = get_current_user_from_session(request)
    if not user_payload:
        return RedirectResponse("/auth/login", status_code=status.HTTP_302_FOUND)

    user = db.query(User).filter(User.id == user_payload["user_id"]).first()
    face_prof = db.query(FaceProfile).filter(FaceProfile.user_id == user.id).first()
    sample_count = 0
    if face_prof:
        sample_count = db.query(FaceSample).filter(FaceSample.profile_id == face_prof.id).count()

    registrations = db.query(Registration).filter(Registration.user_id == user.id).all()
    tickets = db.query(Ticket).filter(Ticket.user_id == user.id).all()

    return templates.TemplateResponse(
        request=request,
        name="participant/dashboard.html",
        context={
            "current_user": user_payload,
            "user": user,
            "face_profile": face_prof,
            "sample_count": sample_count,
            "registrations": registrations,
            "tickets": tickets
        }
    )

@router.get("/participant/enrollment", response_class=HTMLResponse)
def enrollment_page(request: Request, db: Session = Depends(get_db)):
    user_payload = get_current_user_from_session(request)
    if not user_payload:
        return RedirectResponse("/auth/login", status_code=status.HTTP_302_FOUND)

    return templates.TemplateResponse(
        request=request,
        name="participant/enrollment.html",
        context={"current_user": user_payload}
    )

@router.post("/api/enrollment/sample")
def upload_sample_endpoint(
    req: FacialSampleUpload,
    request: Request,
    db: Session = Depends(get_db)
):
    user_payload = get_current_user_from_session(request)
    if not user_payload:
        raise HTTPException(status_code=401, detail="Authentication required")

    result = save_sample_and_extract_feature(
        db=db,
        user_id=user_payload["user_id"],
        image_b64=req.image_base64,
        pose_label=req.pose_label
    )
    return JSONResponse(content=result)

@router.post("/api/enrollment/complete")
def complete_enrollment_endpoint(
    req: CompleteEnrollmentRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    user_payload = get_current_user_from_session(request)
    if not user_payload:
        raise HTTPException(status_code=401, detail="Authentication required")

    try:
        profile = complete_user_enrollment(db, user_payload["user_id"], req.consent)

        # Issue tickets for any existing registrations of this user
        registrations = db.query(Registration).filter(Registration.user_id == user_payload["user_id"]).all()
        for reg in registrations:
            issue_ticket_for_registration(db, reg.id)

        return JSONResponse(content={"success": True, "message": "Biometric enrollment confirmed"})
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/participant/tickets", response_class=HTMLResponse)
def my_tickets_page(request: Request, db: Session = Depends(get_db)):
    user_payload = get_current_user_from_session(request)
    if not user_payload:
        return RedirectResponse("/auth/login", status_code=status.HTTP_302_FOUND)

    tickets = db.query(Ticket).filter(Ticket.user_id == user_payload["user_id"]).all()
    return templates.TemplateResponse(
        request=request,
        name="participant/tickets.html",
        context={"current_user": user_payload, "tickets": tickets}
    )

@router.get("/participant/tickets/{ticket_id}", response_class=HTMLResponse)
def ticket_details_page(ticket_id: str, request: Request, db: Session = Depends(get_db)):
    user_payload = get_current_user_from_session(request)
    if not user_payload:
        return RedirectResponse("/auth/login", status_code=status.HTTP_302_FOUND)

    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket or (ticket.user_id != user_payload["user_id"] and user_payload.get("role") != "admin"):
        raise HTTPException(status_code=404, detail="Ticket not found")

    # Generate QR Code image for the raw token
    qr_b64 = generate_qr_code_image_base64(ticket.token_hash)

    return templates.TemplateResponse(
        request=request,
        name="participant/ticket_details.html",
        context={
            "current_user": user_payload,
            "ticket": ticket,
            "qr_image_b64": qr_b64,
            "raw_token": ticket.token_hash
        }
    )

