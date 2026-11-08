import numpy as np
import cv2
import pytest
from app.cv.image_loader import decode_image_from_bytes, decode_base64_image, encode_image_to_base64
from app.cv.face_detector import face_detector
from app.cv.preprocessing import convert_to_grayscale, resize_face, preprocess_face
from app.cv.quality_check import check_blur, check_brightness, validate_face_quality
from app.cv.hog_extractor import hog_extractor

def create_synthetic_face_image(width=200, height=200):
    """Generates a synthetic image with a face-like pattern for CV testing."""
    img = np.full((height, width, 3), 180, dtype=np.uint8)
    # Head circle
    cv2.circle(img, (width // 2, height // 2), 60, (140, 140, 140), -1)
    # Eyes
    cv2.circle(img, (width // 2 - 20, height // 2 - 15), 8, (40, 40, 40), -1)
    cv2.circle(img, (width // 2 + 20, height // 2 - 15), 8, (40, 40, 40), -1)
    # Nose
    cv2.line(img, (width // 2, height // 2 - 5), (width // 2, height // 2 + 15), (60, 60, 60), 2)
    # Mouth
    cv2.ellipse(img, (width // 2, height // 2 + 30), (20, 8), 0, 0, 180, (50, 50, 50), -1)
    return img

def test_image_loader_b64():
    synth = create_synthetic_face_image()
    b64 = encode_image_to_base64(synth)
    assert b64.startswith("data:image/")

    decoded, err = decode_base64_image(b64)
    assert err is None
    assert decoded is not None
    assert decoded.shape == synth.shape

def test_grayscale_formula():
    """Verify Gray = 0.2989*R + 0.5870*G + 0.1140*B."""
    # Create pure red pixel: B=0, G=0, R=255
    bgr = np.zeros((1, 1, 3), dtype=np.uint8)
    bgr[0, 0, 2] = 255
    gray = convert_to_grayscale(bgr)
    expected_red = int(round(0.2989 * 255))
    assert abs(int(gray[0, 0]) - expected_red) <= 1

def test_resizing_and_preprocessing():
    synth = create_synthetic_face_image(250, 250)
    preprocessed = preprocess_face(synth, target_size=128)
    assert preprocessed.shape == (128, 128)
    assert preprocessed.dtype == np.uint8

def test_hog_feature_dimension():
    """Verify HOG descriptor yields exactly 8,100 numerical values."""
    synth_gray = np.full((128, 128), 128, dtype=np.uint8)
    cv2.circle(synth_gray, (64, 64), 30, 40, -1)

    features, _ = hog_extractor.extract_features(synth_gray)
    assert features.shape == (8100,)
    assert features.dtype == np.float32
    assert hog_extractor.expected_dim == 8100

def test_quality_checks():
    sharp_img = np.zeros((100, 100), dtype=np.uint8)
    cv2.line(sharp_img, (0, 0), (99, 99), 255, 3)
    is_sharp, var = check_blur(sharp_img)
    assert var > 40.0

    is_bright, mean_val = check_brightness(sharp_img)
    assert mean_val < 240.0

