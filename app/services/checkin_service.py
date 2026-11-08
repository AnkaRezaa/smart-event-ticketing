from datetime import datetime, timedelta
from typing import Dict, Any, Tuple, Optional
from sqlalchemy.orm import Session
from sqlalchemy import update
from app.database.models import (
    Ticket, TicketStatus, CheckinSession, SessionStatus,
    CheckinLog, CheckinResult, Event, User, FaceProfile
)
from app.security.token import hash_token
from app.ml.inference import inference_engine

def validate_qr_and_create_session(
    db: Session,
    raw_token: str,
    operator_id: str
) -> Dict[str, Any]:
    """
    Step 1 of check-in: validates QR token and creates a short-lived verification session.
    Supports raw token, pre-hashed token, or ticket UUID.
    """
    clean_token = (raw_token or "").strip()
    token_hashed = hash_token(clean_token)
    ticket = db.query(Ticket).filter(
        (Ticket.token_hash == token_hashed) |
        (Ticket.token_hash == clean_token) |
        (Ticket.id == clean_token)
    ).first()

    if not ticket:
        return {
            "valid": False,
            "message": "Invalid QR Code: ticket not found",
            "failure_code": "TICKET_NOT_FOUND"
        }

    if ticket.status == TicketStatus.USED:
        return {
            "valid": False,
            "message": f"Ticket has already been used on {ticket.used_at.strftime('%Y-%m-%d %H:%M') if ticket.used_at else 'previous entry'}",
            "failure_code": "TICKET_ALREADY_USED",
            "ticket_id": ticket.id
        }

    if ticket.status == TicketStatus.CANCELLED:
        return {
            "valid": False,
            "message": "Ticket has been cancelled",
            "failure_code": "TICKET_CANCELLED",
            "ticket_id": ticket.id
        }

    event = db.query(Event).filter(Event.id == ticket.event_id).first()
    owner = db.query(User).filter(User.id == ticket.user_id).first()

    # Expire any old pending sessions for this ticket
    db.query(CheckinSession).filter(
        CheckinSession.ticket_id == ticket.id,
        CheckinSession.status == SessionStatus.PENDING
    ).update({"status": SessionStatus.EXPIRED})

    # Create new 3-minute session
    session = CheckinSession(
        ticket_id=ticket.id,
        operator_id=operator_id,
        event_id=ticket.event_id,
        expires_at=datetime.utcnow() + timedelta(minutes=3),
        status=SessionStatus.PENDING
    )
    db.add(session)
    db.commit()
    db.refresh(session)

    return {
        "valid": True,
        "session_id": session.id,
        "ticket_id": ticket.id,
        "event_title": event.title if event else "Event",
        "owner_name": owner.name if owner else "Participant",
        "owner_id": owner.id if owner else None,
        "expires_at": session.expires_at.isoformat()
    }

def verify_face_and_consume_ticket(
    db: Session,
    session_id: str,
    image_base64: str,
    operator_id: str
) -> Dict[str, Any]:
    """
    Step 2 of check-in: verifies face against ticket owner and atomically consumes the ticket.
    """
    session = db.query(CheckinSession).filter(CheckinSession.id == session_id).first()
    if not session:
        return {
            "authorized": False,
            "message": "Check-in session not found",
            "failure_code": "SESSION_NOT_FOUND"
        }

    if session.status != SessionStatus.PENDING or datetime.utcnow() > session.expires_at:
        session.status = SessionStatus.EXPIRED
        db.commit()
        return {
            "authorized": False,
            "message": "Verification session has expired. Please rescan QR code.",
            "failure_code": "SESSION_EXPIRED"
        }

    ticket = db.query(Ticket).filter(Ticket.id == session.ticket_id).first()
    if not ticket or ticket.status != TicketStatus.ACTIVE:
        return {
            "authorized": False,
            "message": "Ticket is no longer active",
            "failure_code": "TICKET_NOT_ACTIVE"
        }

    # Run biometric inference against claimed ticket owner
    verdict = inference_engine.verify_claimed_identity(image_base64, claimed_user_id=ticket.user_id)

    if not verdict["verified"]:
        # Record failure log - Ticket remains ACTIVE!
        log = CheckinLog(
            ticket_id=ticket.id,
            operator_id=operator_id,
            result=CheckinResult.DENIED,
            failure_reason=verdict["reason"],
            created_at=datetime.utcnow()
        )
        db.add(log)
        db.commit()

        return {
            "authorized": False,
            "verdict": "ACCESS DENIED",
            "message": verdict["reason"],
            "failure_code": verdict.get("failure_code"),
            "owner_distance": verdict.get("owner_distance"),
            "threshold": verdict.get("threshold"),
            "confidence": verdict.get("confidence")
        }

    # Biometric match succeeded! Now atomically consume ticket
    # Conditional atomic update prevents double-spending / race conditions
    now = datetime.utcnow()
    stmt = (
        update(Ticket)
        .where(Ticket.id == ticket.id)
        .where(Ticket.status == TicketStatus.ACTIVE)
        .values(status=TicketStatus.USED, used_at=now)
    )
    result = db.execute(stmt)

    if result.rowcount == 0:
        # Another concurrent checkin consumed it first!
        db.rollback()
        return {
            "authorized": False,
            "verdict": "ACCESS DENIED",
            "message": "Concurrent check-in detected: ticket was already consumed",
            "failure_code": "CONCURRENT_USAGE"
        }

    # Mark session completed and record success log
    session.status = SessionStatus.COMPLETED
    log = CheckinLog(
        ticket_id=ticket.id,
        operator_id=operator_id,
        result=CheckinResult.GRANTED,
        created_at=now
    )
    db.add(log)
    db.commit()

    owner = db.query(User).filter(User.id == ticket.user_id).first()
    event = db.query(Event).filter(Event.id == ticket.event_id).first()

    return {
        "authorized": True,
        "verdict": "ACCESS GRANTED",
        "message": "Face verified successfully. Welcome to the venue!",
        "owner_name": owner.name if owner else "Participant",
        "event_title": event.title if event else "Event",
        "checkin_time": now.strftime("%Y-%m-%d %H:%M:%S"),
        "owner_distance": verdict.get("owner_distance"),
        "threshold": verdict.get("threshold"),
        "confidence": verdict.get("confidence")
    }

