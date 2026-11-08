import uuid
from datetime import datetime, timedelta
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.connection import Base
from app.database.models import User, UserRole, Event, Registration, Ticket, TicketStatus, FaceProfile, EnrollmentStatus
from app.security.password import hash_password, verify_password
from app.security.token import generate_qr_token, hash_token
from app.services.ticket_service import issue_ticket_for_registration
from app.services.checkin_service import validate_qr_and_create_session

# In-memory SQLite session for isolated database tests
@pytest.fixture
def db_session():
    test_engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=test_engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

def test_password_argon2():
    pwd = "superSecretPassword123!"
    hashed = hash_password(pwd)
    assert hashed != pwd
    assert verify_password(pwd, hashed) is True
    assert verify_password("wrongPassword", hashed) is False

def test_qr_token_unpredictability():
    token1 = generate_qr_token()
    token2 = generate_qr_token()
    assert token1 != token2
    assert len(token1) >= 40

    hash1 = hash_token(token1)
    hash2 = hash_token(token2)
    assert len(hash1) == 64  # SHA-256 hex string
    assert hash1 != hash2

def test_ticket_issuance_and_single_use(db_session):
    # 1. Create User
    user = User(
        name="Alice Test",
        email="alice@example.com",
        password_hash=hash_password("password123"),
        role=UserRole.PARTICIPANT
    )
    db_session.add(user)
    db_session.commit()

    # 2. Create Event
    now = datetime.utcnow()
    event = Event(
        title="Rock Arena Fest",
        location="Stadium A",
        start_at=now + timedelta(days=5),
        end_at=now + timedelta(days=5, hours=4),
        registration_open_at=now - timedelta(days=1),
        registration_close_at=now + timedelta(days=4),
        checkin_open_at=now + timedelta(days=5, hours=-2),
        checkin_close_at=now + timedelta(days=5, hours=4),
        capacity=200,
        status="ACTIVE"
    )
    db_session.add(event)
    db_session.commit()

    # 3. Create Registration
    reg = Registration(event_id=event.id, user_id=user.id, status="CONFIRMED")
    db_session.add(reg)
    db_session.commit()

    # 4. Attempt ticket issuance before face enrollment -> Must raise error
    with pytest.raises(ValueError, match="Facial enrollment must be completed"):
        issue_ticket_for_registration(db_session, reg.id)

    # 5. Complete face enrollment
    face_prof = FaceProfile(
        user_id=user.id,
        enrollment_status=EnrollmentStatus.COMPLETED,
        consent_timestamp=now
    )
    db_session.add(face_prof)
    db_session.commit()

    # 6. Issue ticket
    raw_token = "secure-test-token-string-12345"
    ticket, issued_token = issue_ticket_for_registration(db_session, reg.id, raw_token_override=raw_token)
    assert ticket.status == TicketStatus.ACTIVE
    assert ticket.token_hash == hash_token(raw_token)

    # 7. Operator validates QR Token
    operator = User(
        name="Operator Bob",
        email="operator@example.com",
        password_hash=hash_password("operator123"),
        role=UserRole.OPERATOR
    )
    db_session.add(operator)
    db_session.commit()

    val_res = validate_qr_and_create_session(db_session, raw_token, operator.id)
    assert val_res["valid"] is True
    assert "session_id" in val_res

    # 8. Mark ticket as USED
    ticket.status = TicketStatus.USED
    ticket.used_at = datetime.utcnow()
    db_session.commit()

    # 9. Rescan of used ticket MUST be rejected
    rescan_res = validate_qr_and_create_session(db_session, raw_token, operator.id)
    assert rescan_res["valid"] is False
    assert rescan_res["failure_code"] == "TICKET_ALREADY_USED"

