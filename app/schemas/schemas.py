from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

# Authentication
class UserRegisterRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: str = Field(..., min_length=5, max_length=120)
    password: str = Field(..., min_length=6, max_length=128)
    role: Optional[str] = "participant"

class UserLoginRequest(BaseModel):
    email: str = Field(..., min_length=5, max_length=120)
    password: str

class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    role: str
    created_at: datetime

# Events
class EventCreateRequest(BaseModel):
    title: str = Field(..., min_length=3, max_length=200)
    description: Optional[str] = None
    location: str = Field(..., min_length=2, max_length=200)
    start_at: datetime
    end_at: datetime
    registration_open_at: datetime
    registration_close_at: datetime
    checkin_open_at: datetime
    checkin_close_at: datetime
    capacity: int = Field(default=100, ge=1)

class EventResponse(BaseModel):
    id: str
    title: str
    description: Optional[str]
    location: str
    start_at: datetime
    end_at: datetime
    registration_open_at: datetime
    registration_close_at: datetime
    checkin_open_at: datetime
    checkin_close_at: datetime
    capacity: int
    status: str
    registered_count: Optional[int] = 0

# Registration
class EventRegisterRequest(BaseModel):
    event_id: str

# Facial Enrollment
class FacialSampleUpload(BaseModel):
    image_base64: str
    pose_label: str

class CompleteEnrollmentRequest(BaseModel):
    consent: bool

# Checkin
class ValidateQRRequest(BaseModel):
    qr_token: str

class FaceVerificationRequest(BaseModel):
    session_id: str
    image_base64: str

# CV Lab Inspection
class CVLabInspectRequest(BaseModel):
    image_base64: str

