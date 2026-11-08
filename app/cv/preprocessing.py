import cv2
import numpy as np

def convert_to_grayscale(bgr_image: np.ndarray) -> np.ndarray:
    """
    Converts BGR image to grayscale using the reference formula:
    Gray = 0.2989 * R + 0.5870 * G + 0.1140 * B
    """
    if len(bgr_image.shape) == 2:
        return bgr_image

    # BGR channels in OpenCV
    b = bgr_image[:, :, 0].astype(np.float32)
    g = bgr_image[:, :, 1].astype(np.float32)
    r = bgr_image[:, :, 2].astype(np.float32)

    gray = 0.2989 * r + 0.5870 * g + 0.1140 * b
    gray = np.clip(gray, 0, 255).astype(np.uint8)
    return gray

def resize_face(image: np.ndarray, target_size: int = 128) -> np.ndarray:
    """
    Resizes face image to square target size (128x128) using bilinear interpolation.
    """
    return cv2.resize(image, (target_size, target_size), interpolation=cv2.INTER_LINEAR)

def normalize_lighting(gray_image: np.ndarray) -> np.ndarray:
    """
    Applies histogram equalization for contrast and illumination normalization.
    """
    return cv2.equalizeHist(gray_image)

def preprocess_face(bgr_roi: np.ndarray, target_size: int = 128, equalize: bool = True) -> np.ndarray:
    """
    Full standard preprocessing pipeline:
    1. Grayscale conversion using scientific formula.
    2. Resizing to target_size x target_size (default 128x128).
    3. Lighting/contrast normalization.
    """
    gray = convert_to_grayscale(bgr_roi)
    resized = resize_face(gray, target_size=target_size)
    if equalize:
        return normalize_lighting(resized)
    return resized

