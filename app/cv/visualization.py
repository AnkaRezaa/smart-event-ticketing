from typing import Dict, Any, Tuple
import cv2
import numpy as np
from app.cv.image_loader import encode_image_to_base64
from app.cv.preprocessing import convert_to_grayscale, resize_face, normalize_lighting
from app.cv.face_detector import face_detector
from app.cv.hog_extractor import hog_extractor

def generate_pipeline_visualizations(
    bgr_image: np.ndarray,
    box: Tuple[int, int, int, int]
) -> Dict[str, Any]:
    """
    Computes real intermediate stage images for the CV Lab:
    1. Original with face bounding box
    2. Cropped ROI
    3. 128x128 Grayscale
    4. Equalized Grayscale
    5. Horizontal Gradient (Gx)
    6. Vertical Gradient (Gy)
    7. Gradient Magnitude (M)
    8. Gradient Orientation (Theta)
    9. HOG Visualization
    10. Feature Vector summary
    """
    # 1. Bounding box overlay
    annotated = bgr_image.copy()
    x, y, w, h = box
    cv2.rectangle(annotated, (x, y), (x + w, y + h), (0, 255, 0), 2)
    cv2.putText(annotated, "Face Detected", (x, max(20, y - 10)),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
    b64_annotated = encode_image_to_base64(annotated)

    # 2. Cropped ROI
    roi = face_detector.extract_face_roi(bgr_image, box)
    b64_roi = encode_image_to_base64(roi)

    # 3. Grayscale 128x128
    gray_roi = convert_to_grayscale(roi)
    resized_gray = resize_face(gray_roi, target_size=128)
    b64_gray = encode_image_to_base64(cv2.cvtColor(resized_gray, cv2.COLOR_GRAY2BGR))

    # 4. Equalized
    equalized = normalize_lighting(resized_gray)
    b64_equalized = encode_image_to_base64(cv2.cvtColor(equalized, cv2.COLOR_GRAY2BGR))

    # 5-8. Manual Gradients
    grads = hog_extractor.compute_gradients_manual(equalized)

    # Normalize Gx and Gy to [0, 255] for visual representation
    gx_norm = cv2.normalize(grads["gx"], None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
    gy_norm = cv2.normalize(grads["gy"], None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
    mag_norm = cv2.normalize(grads["magnitude"], None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
    ori_norm = (grads["orientation"] / 180.0 * 255.0).astype(np.uint8)

    # Color maps for visualization
    gx_color = cv2.applyColorMap(gx_norm, cv2.COLORMAP_JET)
    gy_color = cv2.applyColorMap(gy_norm, cv2.COLORMAP_JET)
    mag_color = cv2.applyColorMap(mag_norm, cv2.COLORMAP_INFERNO)
    ori_color = cv2.applyColorMap(ori_norm, cv2.COLORMAP_HSV)

    b64_gx = encode_image_to_base64(gx_color)
    b64_gy = encode_image_to_base64(gy_color)
    b64_mag = encode_image_to_base64(mag_color)
    b64_ori = encode_image_to_base64(ori_color)

    # 9. Scikit-image HOG visualization
    features, hog_img = hog_extractor.extract_features(equalized, visualize=True)
    if hog_img is not None:
        hog_norm = cv2.normalize(hog_img, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
        hog_color = cv2.applyColorMap(hog_norm, cv2.COLORMAP_HOT)
        b64_hog = encode_image_to_base64(hog_color)
    else:
        b64_hog = ""

    # Feature vector stats
    feature_summary = {
        "dimension": int(len(features)),
        "min": float(np.min(features)),
        "max": float(np.max(features)),
        "mean": float(np.mean(features)),
        "std": float(np.std(features)),
        "sparsity_zeros_pct": float(np.mean(features == 0) * 100),
        "first_20_values": [round(float(v), 4) for v in features[:20]]
    }

    return {
        "annotated_image": b64_annotated,
        "roi_image": b64_roi,
        "gray_image": b64_gray,
        "equalized_image": b64_equalized,
        "gx_image": b64_gx,
        "gy_image": b64_gy,
        "magnitude_image": b64_mag,
        "orientation_image": b64_ori,
        "hog_image": b64_hog,
        "feature_summary": feature_summary
    }

