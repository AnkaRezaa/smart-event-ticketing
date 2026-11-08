"""
Demo Seeding Script:
Creates a fully enrolled demo participant ('Budi Santoso') with 9 face samples,
HOG feature descriptors in gallery.npz, and an ACTIVE ticket with a convenient QR token.
Generates matching face sample and impostor face sample for turnstile verification testing.
"""
import os
import sys
import uuid
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import cv2
import numpy as np
from app.database.connection import SessionLocal
from app.database.models import User, UserRole, Event, Registration, Ticket, TicketStatus, FaceProfile, FaceSample, FaceFeature, EnrollmentStatus
from app.security.password import hash_password
from app.security.token import hash_token
from app.cv.image_loader import encode_image_to_base64
from app.cv.preprocessing import preprocess_face
from app.cv.hog_extractor import hog_extractor
from app.ml.dataset import default_gallery
from app.ml.inference import inference_engine
from app.config import settings

def create_face_canvas(eye_offset=0, mouth_smile=True, tint=180):
    """Draws a clean face pattern with controllable facial parameters."""
    img = np.full((180, 180, 3), tint, dtype=np.uint8)
    # Head outline
    cv2.circle(img, (90, 90), 65, (130, 130, 130), -1)
    # Eyes
    cv2.circle(img, (68 + eye_offset, 78), 9, (35, 35, 35), -1)
    cv2.circle(img, (112 + eye_offset, 78), 9, (35, 35, 35), -1)
    # Nose
    cv2.line(img, (90 + eye_offset // 2, 85), (90 + eye_offset // 2, 105), (50, 50, 50), 2)
    # Mouth
    if mouth_smile:
        cv2.ellipse(img, (90 + eye_offset // 2, 122), (22, 10), 0, 0, 180, (40, 40, 40), -1)
    else:
        cv2.line(img, (72, 122), (108, 122), (40, 40, 40), 2)
    return img

def seed_demo_data():
    db = SessionLocal()
    try:
        print("[*] Seeding demo participant and active ticket...")

        # 1. Get or create Event
        event = db.query(Event).first()
        if not event:
            print("[!] No event found. Creating fallback event...")
            event = Event(
                title="International AI & Music Festival 2026",
                location="Grand Arena Stadium, Main Stage",
                start_at=datetime.utcnow(),
                end_at=datetime.utcnow(),
                registration_open_at=datetime.utcnow(),
                registration_close_at=datetime.utcnow(),
                checkin_open_at=datetime.utcnow(),
                checkin_close_at=datetime.utcnow(),
                capacity=500,
                status="ACTIVE"
            )
            db.add(event)
            db.commit()

        # 2. Get or create Participant
        email = "budi@smartticket.com"
        user = db.query(User).filter(User.email == email).first()
        if not user:
            user = User(
                name="Budi Santoso",
                email=email,
                password_hash=hash_password("budi123"),
                role=UserRole.PARTICIPANT
            )
            db.add(user)
            db.commit()
            db.refresh(user)

        # 3. Get or create Registration
        reg = db.query(Registration).filter(
            Registration.user_id == user.id,
            Registration.event_id == event.id
        ).first()
        if not reg:
            reg = Registration(
                event_id=event.id,
                user_id=user.id,
                status="CONFIRMED"
            )
            db.add(reg)
            db.commit()
            db.refresh(reg)

        # 4. Get or create FaceProfile
        profile = db.query(FaceProfile).filter(FaceProfile.user_id == user.id).first()
        if not profile:
            profile = FaceProfile(
                user_id=user.id,
                enrollment_status=EnrollmentStatus.COMPLETED,
                consent_timestamp=datetime.utcnow(),
                feature_version="v1.0"
            )
            db.add(profile)
            db.commit()
            db.refresh(profile)

        # 5. Remove any old gallery entries for this user to avoid duplicates
        default_gallery.remove_user(user.id)

        # 6. Generate 9 pose samples for Budi
        poses = [
            ("frontal_1", 0, True),
            ("slight_left", -4, True),
            ("slight_right", 4, True),
            ("angle_left", -7, False),
            ("angle_right", 7, False),
            ("slight_up", 0, False),
            ("slight_down", 0, True),
            ("expression", 0, True),
            ("frontal_2", 0, True)
        ]

        os.makedirs(settings.PRIVATE_FACES_DIR, exist_ok=True)
        # Clear previous sample rows for clean seed
        db.query(FaceSample).filter(FaceSample.profile_id == profile.id).delete()

        for label, offset, smile in poses:
            face_img = create_face_canvas(eye_offset=offset, mouth_smile=smile, tint=180)
            sample_id = str(uuid.uuid4())
            filename = f"{user.id}_{sample_id}.jpg"
            filepath = os.path.join(settings.PRIVATE_FACES_DIR, filename)
            cv2.imwrite(filepath, face_img)

            # Preprocess and extract real 8100-dim HOG vector
            preprocessed = preprocess_face(face_img, target_size=128)
            features, _ = hog_extractor.extract_features(preprocessed)

            # DB records
            sample = FaceSample(
                id=sample_id,
                profile_id=profile.id,
                image_reference=filename,
                pose_label=label,
                quality_status="PASSED"
            )
            db.add(sample)
            db.flush()

            feature_rec = FaceFeature(
                sample_id=sample.id,
                feature_reference=f"{sample_id}_hog.npy",
                feature_version="v1.0"
            )
            db.add(feature_rec)

            # Add to persistent gallery
            default_gallery.add_features(user.id, sample_id, features)

        db.commit()
        inference_engine.refresh_model()

        # 7. Create ACTIVE Ticket with predictable demo token
        demo_raw_token = "DEMO-QR-BUDI-SANTOSO-2026-TOKEN"
        token_hash = hash_token(demo_raw_token)

        ticket = db.query(Ticket).filter(Ticket.registration_id == reg.id).first()
        if not ticket:
            ticket = Ticket(
                event_id=event.id,
                registration_id=reg.id,
                user_id=user.id,
                token_hash=token_hash,
                status=TicketStatus.ACTIVE,
                issued_at=datetime.utcnow()
            )
            db.add(ticket)
        else:
            ticket.status = TicketStatus.ACTIVE
            ticket.token_hash = token_hash
            ticket.used_at = None

        db.commit()

        # 8. Save test probes in storage/ for manual verification testing
        matching_probe = create_face_canvas(eye_offset=0, mouth_smile=True, tint=180)
        impostor_probe = create_face_canvas(eye_offset=12, mouth_smile=False, tint=100)

        probe_dir = os.path.join(str(settings.BASE_DIR), "storage", "test_probes")
        os.makedirs(probe_dir, exist_ok=True)
        cv2.imwrite(os.path.join(probe_dir, "budi_matching_probe.jpg"), matching_probe)
        cv2.imwrite(os.path.join(probe_dir, "impostor_probe.jpg"), impostor_probe)

        print("\n" + "=" * 60)
        print("DEMO DATA SEEDED SUCCESSFULLY!")
        print("=" * 60)
        print(f"Attendee Name : {user.name}")
        print(f"Login Email   : {user.email}")
        print(f"Login Password: budi123")
        print(f"Event Title   : {event.title}")
        print(f"Ticket Status : ACTIVE")
        print(f"Demo QR Token : {demo_raw_token}")
        print(f"\nTest probes saved to: {probe_dir}")
        print("  1. budi_matching_probe.jpg (Will produce ACCESS GRANTED)")
        print("  2. impostor_probe.jpg       (Will produce ACCESS DENIED)")
        print("=" * 60)

    finally:
        db.close()

if __name__ == "__main__":
    seed_demo_data()

