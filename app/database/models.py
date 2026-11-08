import enum
import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Integer, Float, Text, Boolean, DateTime,
    ForeignKey, Enum, Index, UniqueConstraint
)
from sqlalchemy.orm import relationship
from app.database.connection import Base

class UserRole(str, enum.Enum):
    PARTICIPANT = "participant"
    OPERATOR = "operator"
    ADMIN = "admin"

class TicketStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    USED = "USED"
    CANCELLED = "CANCELLED"

class CheckinResult(str, enum.Enum):
    GRANTED = "GRANTED"
    DENIED = "DENIED"

class EnrollmentStatus(str, enum.Enum):
    NOT_STARTED = "NOT_STARTED"
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class SessionStatus(str, enum.Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    EXPIRED = "EXPIRED"
    FAILED = "FAILED"

class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False)
    email = Column(String(120), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.PARTICIPANT, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    registrations = relationship("Registration", back_populates="user", cascade="all, delete-orphan")
    face_profile = relationship("FaceProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    tickets = relationship("Ticket", back_populates="user", cascade="all, delete-orphan")
    operator_assignments = relationship("OperatorAssignment", back_populates="operator", cascade="all, delete-orphan")

class Event(Base):
    __tablename__ = "events"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    location = Column(String(200), nullable=False)
    start_at = Column(DateTime, nullable=False)
    end_at = Column(DateTime, nullable=False)
    registration_open_at = Column(DateTime, nullable=False)
    registration_close_at = Column(DateTime, nullable=False)
    checkin_open_at = Column(DateTime, nullable=False)
    checkin_close_at = Column(DateTime, nullable=False)
    capacity = Column(Integer, default=100, nullable=False)
    status = Column(String(30), default="UPCOMING", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    registrations = relationship("Registration", back_populates="event", cascade="all, delete-orphan")
    tickets = relationship("Ticket", back_populates="event", cascade="all, delete-orphan")
    operator_assignments = relationship("OperatorAssignment", back_populates="event", cascade="all, delete-orphan")

class Registration(Base):
    __tablename__ = "registrations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    event_id = Column(String(36), ForeignKey("events.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    status = Column(String(30), default="CONFIRMED", nullable=False)
    registered_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    event = relationship("Event", back_populates="registrations")
    user = relationship("User", back_populates="registrations")
    ticket = relationship("Ticket", back_populates="registration", uselist=False, cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint("event_id", "user_id", name="uq_user_event_registration"),
    )

class FaceProfile(Base):
    __tablename__ = "face_profiles"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    enrollment_status = Column(Enum(EnrollmentStatus), default=EnrollmentStatus.NOT_STARTED, nullable=False)
    consent_timestamp = Column(DateTime, nullable=True)
    feature_version = Column(String(50), default="v1.0", nullable=False)

    user = relationship("User", back_populates="face_profile")
    samples = relationship("FaceSample", back_populates="profile", cascade="all, delete-orphan")

class FaceSample(Base):
    __tablename__ = "face_samples"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    profile_id = Column(String(36), ForeignKey("face_profiles.id", ondelete="CASCADE"), nullable=False)
    image_reference = Column(String(255), nullable=False)
    pose_label = Column(String(50), nullable=False)
    quality_status = Column(String(50), default="PASSED", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    profile = relationship("FaceProfile", back_populates="samples")
    feature = relationship("FaceFeature", back_populates="sample", uselist=False, cascade="all, delete-orphan")

class FaceFeature(Base):
    __tablename__ = "face_features"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    sample_id = Column(String(36), ForeignKey("face_samples.id", ondelete="CASCADE"), nullable=False)
    feature_reference = Column(String(255), nullable=False)
    feature_version = Column(String(50), default="v1.0", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    sample = relationship("FaceSample", back_populates="feature")

class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    event_id = Column(String(36), ForeignKey("events.id", ondelete="CASCADE"), nullable=False)
    registration_id = Column(String(36), ForeignKey("registrations.id", ondelete="CASCADE"), unique=True, nullable=False)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    token_hash = Column(String(64), unique=True, index=True, nullable=False)
    status = Column(Enum(TicketStatus), default=TicketStatus.ACTIVE, nullable=False)
    issued_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    used_at = Column(DateTime, nullable=True)

    event = relationship("Event", back_populates="tickets")
    registration = relationship("Registration", back_populates="ticket")
    user = relationship("User", back_populates="tickets")
    sessions = relationship("CheckinSession", back_populates="ticket", cascade="all, delete-orphan")
    logs = relationship("CheckinLog", back_populates="ticket", cascade="all, delete-orphan")

class CheckinSession(Base):
    __tablename__ = "checkin_sessions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    ticket_id = Column(String(36), ForeignKey("tickets.id", ondelete="CASCADE"), nullable=False)
    operator_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    event_id = Column(String(36), ForeignKey("events.id", ondelete="CASCADE"), nullable=False)
    expires_at = Column(DateTime, nullable=False)
    status = Column(Enum(SessionStatus), default=SessionStatus.PENDING, nullable=False)

    ticket = relationship("Ticket", back_populates="sessions")
    operator = relationship("User")

class CheckinLog(Base):
    __tablename__ = "checkin_logs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    ticket_id = Column(String(36), ForeignKey("tickets.id", ondelete="CASCADE"), nullable=False)
    operator_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    result = Column(Enum(CheckinResult), nullable=False)
    failure_reason = Column(String(255), nullable=True)
    model_version_id = Column(String(36), ForeignKey("model_versions.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    ticket = relationship("Ticket", back_populates="logs")
    operator = relationship("User")
    model_version = relationship("ModelVersion")

class ModelVersion(Base):
    __tablename__ = "model_versions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    algorithm = Column(String(50), default="HOG-KNN-PSO", nullable=False)
    hog_config = Column(Text, nullable=False)
    knn_config = Column(Text, nullable=False)
    pso_config = Column(Text, nullable=True)
    threshold = Column(Float, default=0.65, nullable=False)
    artifact_reference = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    activated_at = Column(DateTime, nullable=True)

class OperatorAssignment(Base):
    __tablename__ = "operator_assignments"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    operator_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    event_id = Column(String(36), ForeignKey("events.id", ondelete="CASCADE"), nullable=False)

    operator = relationship("User", back_populates="operator_assignments")
    event = relationship("Event", back_populates="operator_assignments")

    __table_args__ = (
        UniqueConstraint("operator_id", "event_id", name="uq_operator_event_assignment"),
    )

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    actor_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    action = Column(String(100), nullable=False)
    resource_type = Column(String(50), nullable=False)
    resource_id = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

