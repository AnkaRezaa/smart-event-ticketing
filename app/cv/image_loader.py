import base64
import re
from typing import Tuple, Optional
import numpy as np
import cv2

def decode_image_from_bytes(image_bytes: bytes) -> Optional[np.ndarray]:
    """Decodes raw image bytes into an OpenCV BGR numpy array."""
    if not image_bytes:
        return None
    nparr = np.frombuffer(image_bytes, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    return image

def decode_base64_image(data_url_or_b64: str) -> Tuple[Optional[np.ndarray], Optional[str]]:
    """
    Decodes a base64 string or data URL (e.g. data:image/jpeg;base64,...)
    into an OpenCV BGR image and returns (image, error_message).
    """
    if not data_url_or_b64:
        return None, "Empty image data received"

    # Match base64 data URI header if present
    match = re.match(r"^data:image/([a-zA-Z0-9\+\-\.]+);base64,(.+)$", data_url_or_b64)
    if match:
        b64_str = match.group(2)
    else:
        b64_str = data_url_or_b64

    try:
        image_bytes = base64.b64decode(b64_str)
    except Exception as e:
        return None, f"Failed to base64-decode image: {str(e)}"

    image = decode_image_from_bytes(image_bytes)
    if image is None:
        return None, "Decoded bytes could not be parsed as a valid image"

    return image, None

def encode_image_to_base64(image: np.ndarray, ext: str = ".jpg") -> str:
    """Encodes an OpenCV image to base64 data URI string."""
    success, buffer = cv2.imencode(ext, image)
    if not success:
        return ""
    b64_data = base64.b64encode(buffer).decode("utf-8")
    mime = "image/png" if ext.lower() == ".png" else "image/jpeg"
    return f"data:{mime};base64,{b64_data}"

