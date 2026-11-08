import os
import uuid
from datetime import datetime
from typing import Dict, Any, Tuple
import cv2
from sqlalchemy.orm import Session
from app.config import settings
from app.database.models import FaceProfile, FaceSample, FaceFeature, EnrollmentStatus
from app.cv.image_loader import decode_base64_image
from app.cv.face_detector import face_detector
from app.cv.quality_check import validate_face_quality
from app.cv.preprocessing import preprocess_face
from app.cv.hog_extractor import hog_extractor
from app.ml.dataset import default_gallery
from app.ml.inference import inference_engine

def save_sample_and_extract_feature(
    db: Session,
    user_id: str,
    image_b64: str,
    pose_label: str
) -> Dict[str, Any]:
    """
    Processes, quality-checks, stores, and extracts HOG features for one enrollment frame.
    """
    image, err = decode_base64_image(image_b64)
    if image is None:
        return {"success": False, "message": f"Failed to decode image: {err}"}

    boxes = face_detector.detect_faces(image)
    quality = validate_face_quality(image, boxes)
    if not quality["passed"]:
        return {
            "success": False,
            "message": quality["reason"],
            "details": quality.get("details", {})
        }

    # Extract facial ROI & preprocess
    roi = face_detector.extract_face_roi(image, boxes[0])
    preprocessed = preprocess_face(roi, target_size=settings.TARGET_FACE_SIZE)
    features, _ = hog_extractor.extract_features(preprocessed)

    # Get or create FaceProfile
    profile = db.query(FaceProfile).filter(FaceProfile.user_id == user_id).first()
    if not profile:
        profile = FaceProfile(
            user_id=user_id,
            enrollment_status=EnrollmentStatus.PENDING,
            feature_version="v1.0"
        )
        db.add(profile)
        db.flush()

    # Save private image to storage/private_faces
    sample_id = str(uuid.uuid4())
    img_filename = f"{user_id}_{sample_id}.jpg"
    img_path = os.path.join(settings.PRIVATE_FACES_DIR, img_filename)
    cv2.imwrite(img_path, roi)

    # Record sample in DB
    sample = FaceSample(
        id=sample_id,
        profile_id=profile.id,
        image_reference=img_filename,
        pose_label=pose_label,
        quality_status="PASSED",
        created_at=datetime.utcnow()
    )
    db.add(sample)
    db.flush()

    # Record feature in DB
    feature_ref = f"{sample_id}_hog.npy"
    face_feature = FaceFeature(
        sample_id=sample.id,
        feature_reference=feature_ref,
        feature_version="v1.0",
        created_at=datetime.utcnow()
    )
    db.add(face_feature)
    db.commit()

    # Add to in-memory/persisted feature gallery and refresh inference engine
    default_gallery.add_features(user_id, sample.id, features)
    inference_engine.refresh_model()

    # Count total samples for this profile
    total_samples = db.query(FaceSample).filter(FaceSample.profile_id == profile.id).count()

    return {
        "success": True,
        "sample_id": sample.id,
        "pose_label": pose_label,
        "total_samples": total_samples,
        "message": "Sample captured and feature vector extracted successfully"
    }

def complete_user_enrollment(db: Session, user_id: str, consent: bool) -> FaceProfile:
    """Marks user enrollment as completed after minimum samples are gathered."""
    if not consent:
        raise ValueError("Consent for biometric data processing is required")

    profile = db.query(FaceProfile).filter(FaceProfile.user_id == user_id).first()
    if not profile:
        raise ValueError("No enrollment session found for this user")

    count = db.query(FaceSample).filter(FaceSample.profile_id == profile.id).count()
    if count < 3:  # minimum viable threshold (target is 9)
        raise ValueError(f"At least 3 valid face samples are required to complete enrollment (captured: {count})")

    profile.enrollment_status = EnrollmentStatus.COMPLETED
    profile.consent_timestamp = datetime.utcnow()
    db.commit()
    db.refresh(profile)

    inference_engine.refresh_model()
    return profile

