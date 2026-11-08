import io
import base64
from datetime import datetime
from typing import Optional, Tuple
import qrcode
from sqlalchemy.orm import Session
from app.database.models import Ticket, TicketStatus, Registration, Event, User, FaceProfile, EnrollmentStatus
from app.security.token import generate_qr_token, hash_token

def generate_qr_code_image_base64(raw_token: str) -> str:
    """Generates a base64 encoded PNG QR code image for a raw token."""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=8,
        border=3,
    )
    qr.add_data(raw_token)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    b64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return f"data:image/png;base64,{b64}"

def issue_ticket_for_registration(
    db: Session,
    registration_id: str,
    raw_token_override: Optional[str] = None
) -> Tuple[Ticket, str]:
    """
    Issues a new single-use ticket for an enrolled user and registration.
    Returns (Ticket, raw_qr_token).
    """
    reg = db.query(Registration).filter(Registration.id == registration_id).first()
    if not reg:
        raise ValueError("Registration record not found")

    # Verify facial profile enrollment status
    face_prof = db.query(FaceProfile).filter(FaceProfile.user_id == reg.user_id).first()
    if not face_prof or face_prof.enrollment_status != EnrollmentStatus.COMPLETED:
        raise ValueError("Facial enrollment must be completed before ticket issuance")

    # Check if ticket already exists
    existing_ticket = db.query(Ticket).filter(Ticket.registration_id == registration_id).first()
    if existing_ticket:
        return existing_ticket, ""

    raw_token = raw_token_override or generate_qr_token()
    token_hashed = hash_token(raw_token)

    ticket = Ticket(
        event_id=reg.event_id,
        registration_id=reg.id,
        user_id=reg.user_id,
        token_hash=token_hashed,
        status=TicketStatus.ACTIVE,
        issued_at=datetime.utcnow()
    )
    db.add(ticket)
    db.commit()
    db.refresh(ticket)

    return ticket, raw_token

