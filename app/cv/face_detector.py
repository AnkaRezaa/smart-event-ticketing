import os
from typing import List, Tuple, Optional
import cv2
import numpy as np

class FaceDetector:
    def __init__(self, cascade_path: Optional[str] = None):
        if cascade_path and os.path.exists(cascade_path):
            self.cascade = cv2.CascadeClassifier(cascade_path)
        else:
            default_path = os.path.join(cv2.data.haarcascades, "haarcascade_frontalface_default.xml")
            self.cascade = cv2.CascadeClassifier(default_path)

        if self.cascade.empty():
            raise RuntimeError("Failed to load OpenCV Haar Cascade frontal face detector")

    def detect_faces(
        self,
        image: np.ndarray,
        scale_factor: float = 1.1,
        min_neighbors: int = 5,
        min_size: Tuple[int, int] = (60, 60)
    ) -> List[Tuple[int, int, int, int]]:
        """
        Detects faces in BGR image.
        Returns list of bounding boxes (x, y, w, h).
        """
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image

        faces = self.cascade.detectMultiScale(
            gray,
            scaleFactor=scale_factor,
            minNeighbors=min_neighbors,
            minSize=min_size
        )

        return [tuple(box) for box in faces]

    def extract_face_roi(
        self,
        image: np.ndarray,
        box: Tuple[int, int, int, int],
        padding_ratio: float = 0.1
    ) -> np.ndarray:
        """
        Extracts cropped facial ROI with symmetric padding around bounding box.
        """
        x, y, w, h = box
        img_h, img_w = image.shape[:2]

        pad_x = int(w * padding_ratio)
        pad_y = int(h * padding_ratio)

        x1 = max(0, x - pad_x)
        y1 = max(0, y - pad_y)
        x2 = min(img_w, x + w + pad_x)
        y2 = min(img_h, y + h + pad_y)

        roi = image[y1:y2, x1:x2]
        return roi

face_detector = FaceDetector()

