from fastapi import APIRouter, Depends, Request, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.database.models import Event, CheckinLog, UserRole
from app.security.session import get_current_user_from_session, require_role
from app.schemas.schemas import ValidateQRRequest, FaceVerificationRequest
from app.services.checkin_service import validate_qr_and_create_session, verify_face_and_consume_ticket

router = APIRouter(tags=["checkin"])
templates = Jinja2Templates(directory="app/templates")

@router.get("/operator/dashboard", response_class=HTMLResponse)
def operator_dashboard(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_from_session(request)
    if not user or user.get("role") not in ["operator", "admin"]:
        return RedirectResponse("/auth/login?next=/operator/dashboard", status_code=status.HTTP_302_FOUND)

    events = db.query(Event).order_by(Event.start_at.asc()).all()
    recent_logs = db.query(CheckinLog).order_by(CheckinLog.created_at.desc()).limit(15).all()

    return templates.TemplateResponse(
        request=request,
        name="operator/dashboard.html",
        context={
            "current_user": user,
            "events": events,
            "recent_logs": recent_logs
        }
    )

@router.get("/operator/scanner", response_class=HTMLResponse)
def operator_scanner_page(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_from_session(request)
    if not user or user.get("role") not in ["operator", "admin"]:
        return RedirectResponse("/auth/login?next=/operator/scanner", status_code=status.HTTP_302_FOUND)

    return templates.TemplateResponse(
        request=request,
        name="operator/scanner.html",
        context={"current_user": user}
    )

@router.post("/api/checkin/validate-qr")
def validate_qr_api(
    req: ValidateQRRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    user = get_current_user_from_session(request)
    if not user or user.get("role") not in ["operator", "admin"]:
        raise HTTPException(status_code=403, detail="Operator authorization required")

    result = validate_qr_and_create_session(
        db=db,
        raw_token=req.qr_token,
        operator_id=user["user_id"]
    )
    return JSONResponse(content=result)

@router.post("/api/checkin/verify-face")
def verify_face_api(
    req: FaceVerificationRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    user = get_current_user_from_session(request)
    if not user or user.get("role") not in ["operator", "admin"]:
        raise HTTPException(status_code=403, detail="Operator authorization required")

    result = verify_face_and_consume_ticket(
        db=db,
        session_id=req.session_id,
        image_base64=req.image_base64,
        operator_id=user["user_id"]
    )
    return JSONResponse(content=result)

