from typing import Dict, Any, Tuple, List
import cv2
import numpy as np

def check_blur(gray_image: np.ndarray, min_variance: float = 40.0) -> Tuple[bool, float]:
    """
    Computes variance of the Laplacian to estimate focus/blur.
    Lower variance indicates blurry image.
    """
    laplacian = cv2.Laplacian(gray_image, cv2.CV_64F)
    variance = float(laplacian.var())
    return (variance >= min_variance), variance

def check_brightness(gray_image: np.ndarray, min_mean: float = 30.0, max_mean: float = 235.0) -> Tuple[bool, float]:
    """
    Checks if average lighting intensity is within acceptable range.
    """
    mean_val = float(np.mean(gray_image))
    is_ok = (min_mean <= mean_val <= max_mean)
    return is_ok, mean_val

def check_face_position(
    box: Tuple[int, int, int, int],
    frame_shape: Tuple[int, int]
) -> Tuple[bool, str]:
    """
    Validates that face is reasonably positioned and sized inside the frame.
    """
    h_frame, w_frame = frame_shape[:2]
    x, y, w, h = box

    # Must be at least 10% of frame dimensions
    if w < (w_frame * 0.1) or h < (h_frame * 0.1):
        return False, "Face is too far from camera"

    # Center of face
    cx = x + w / 2.0
    cy = y + h / 2.0

    # Must be within central 85% of frame
    if not (0.1 * w_frame <= cx <= 0.9 * w_frame and 0.1 * h_frame <= cy <= 0.9 * h_frame):
        return False, "Face is too close to the edge of the camera"

    return True, "Face position is good"

def validate_face_quality(
    image: np.ndarray,
    detected_boxes: List[Tuple[int, int, int, int]]
) -> Dict[str, Any]:
    """
    Runs full image quality check suite:
    - Face detection count (must be exactly 1)
    - Face position
    - Blur / sharpness
    - Illumination
    """
    if len(detected_boxes) == 0:
        return {
            "passed": False,
            "reason": "No face detected in the frame",
            "details": {"faces_found": 0}
        }
    if len(detected_boxes) > 1:
        return {
            "passed": False,
            "reason": "Multiple faces detected. Please ensure only one person is in frame",
            "details": {"faces_found": len(detected_boxes)}
        }

    box = detected_boxes[0]
    pos_ok, pos_msg = check_face_position(box, image.shape)
    if not pos_ok:
        return {
            "passed": False,
            "reason": pos_msg,
            "details": {"box": box}
        }

    x, y, w, h = box
    face_roi = image[y:y+h, x:x+w]
    if len(face_roi.shape) == 3:
        gray_roi = cv2.cvtColor(face_roi, cv2.COLOR_BGR2GRAY)
    else:
        gray_roi = face_roi

    sharp_ok, lap_var = check_blur(gray_roi)
    if not sharp_ok:
        return {
            "passed": False,
            "reason": f"Image is too blurry (sharpness score: {lap_var:.1f}). Hold camera steady",
            "details": {"sharpness": lap_var}
        }

    bright_ok, bright_val = check_brightness(gray_roi)
    if not bright_ok:
        reason = "Lighting is too dark" if bright_val < 30.0 else "Lighting is too bright / washed out"
        return {
            "passed": False,
            "reason": f"{reason} (brightness: {bright_val:.1f}). Adjust your light",
            "details": {"brightness": bright_val}
        }

    return {
        "passed": True,
        "reason": "Image quality is optimal",
        "details": {
            "faces_found": 1,
            "box": box,
            "sharpness": lap_var,
            "brightness": bright_val
        }
    }

