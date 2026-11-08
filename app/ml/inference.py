import time
from typing import Dict, Any, Optional
import numpy as np

from app.cv.image_loader import decode_base64_image
from app.cv.face_detector import face_detector
from app.cv.preprocessing import preprocess_face
from app.cv.quality_check import validate_face_quality
from app.cv.hog_extractor import hog_extractor
from app.ml.dataset import default_gallery
from app.ml.knn_model import FaceKNNClassifier
from app.ml.threshold import threshold_calibrator
from app.config import settings

class BiometricInferenceEngine:
    """
    Production facial inference pipeline coordinating CV preprocessing,
    HOG feature extraction, KNN classification, and threshold verification.
    """
    def __init__(self):
        self.knn = FaceKNNClassifier(k=settings.KNN_DEFAULT_K)
        self.active_threshold = settings.RECOGNITION_THRESHOLD
        self.refresh_model()

    def refresh_model(self):
        """Reloads gallery features into KNN classifier."""
        features, labels = default_gallery.get_all()
        if len(labels) > 0:
            self.knn.fit(features, labels)

    def verify_claimed_identity(
        self,
        image_data: str,
        claimed_user_id: str
    ) -> Dict[str, Any]:
        """
        Two-stage entrance verification:
        1. Preprocess & extract HOG descriptor from live camera frame.
        2. Test open-set prediction via KNN.
        3. Test Euclidean distance against the claimed ticket owner's enrolled gallery samples.
        4. Recheck calibrated rejection threshold.
        """
        start_time = time.time()

        # Step 1: Decode image
        image, err = decode_base64_image(image_data)
        if image is None:
            return {
                "verified": False,
                "reason": f"Image decoding error: {err}",
                "failure_code": "INVALID_IMAGE",
                "details": {}
            }

        # Step 2: Detect faces
        boxes = face_detector.detect_faces(image)
        quality = validate_face_quality(image, boxes)
        if not quality["passed"]:
            return {
                "verified": False,
                "reason": quality["reason"],
                "failure_code": "QUALITY_CHECK_FAILED",
                "details": quality.get("details", {})
            }

        # Step 3: Extract ROI & preprocess
        roi = face_detector.extract_face_roi(image, boxes[0])
        preprocessed = preprocess_face(roi, target_size=settings.TARGET_FACE_SIZE)

        # Step 4: Extract HOG descriptors (8100 dims)
        hog_features, _ = hog_extractor.extract_features(preprocessed)

        # Step 5: Check if gallery is populated
        self.refresh_model()
        if not self.knn.is_fitted():
            return {
                "verified": False,
                "reason": "System facial gallery is currently uninitialized",
                "failure_code": "GALLERY_EMPTY",
                "details": {}
            }

        # Step 6: Query KNN
        knn_res = self.knn.predict_with_distances(hog_features)
        claimed_dist_res = self.knn.compute_distance_to_claimed_user(hog_features, claimed_user_id)

        latency_ms = (time.time() - start_time) * 1000

        if not claimed_dist_res["has_enrolled_samples"]:
            return {
                "verified": False,
                "reason": "Ticket owner has not completed facial enrollment",
                "failure_code": "NO_ENROLLED_SAMPLES",
                "latency_ms": latency_ms,
                "details": {}
            }

        owner_distance = claimed_dist_res["min_distance"]
        predicted_user_id = knn_res["predicted_label"]

        # Check distance threshold
        within_threshold = (owner_distance <= self.active_threshold)
        identity_matches = (predicted_user_id == claimed_user_id)

        # Both identity match and distance threshold are strictly checked
        if identity_matches and within_threshold:
            return {
                "verified": True,
                "reason": "Facial verification successful: identity matched",
                "failure_code": None,
                "owner_distance": float(round(owner_distance, 4)),
                "threshold": float(self.active_threshold),
                "confidence": float(round(knn_res["confidence_score"], 4)),
                "latency_ms": latency_ms,
                "details": {
                    "predicted_id": predicted_user_id,
                    "claimed_id": claimed_user_id,
                    "neighbor_distances": knn_res["neighbor_distances"]
                }
            }
        else:
            failure_reason = "Face does not match the ticket owner"
            if not within_threshold:
                failure_reason = f"Face distance ({owner_distance:.3f}) exceeds threshold ({self.active_threshold:.3f})"
            elif not identity_matches:
                failure_reason = "Face classified as a different identity"

            return {
                "verified": False,
                "reason": failure_reason,
                "failure_code": "IDENTITY_MISMATCH",
                "owner_distance": float(round(owner_distance, 4)),
                "threshold": float(self.active_threshold),
                "confidence": float(round(knn_res["confidence_score"], 4)),
                "latency_ms": latency_ms,
                "details": {
                    "predicted_id": predicted_user_id,
                    "claimed_id": claimed_user_id,
                    "neighbor_distances": knn_res["neighbor_distances"]
                }
            }

inference_engine = BiometricInferenceEngine()

