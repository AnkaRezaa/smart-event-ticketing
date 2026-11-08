from typing import Tuple, Dict, Any, Optional
import numpy as np
import cv2
from skimage.feature import hog
from app.config import settings

class HOGFeatureExtractor:
    def __init__(
        self,
        orientations: int = 9,
        pixels_per_cell: Tuple[int, int] = (8, 8),
        cells_per_block: Tuple[int, int] = (2, 2),
        block_norm: str = "L2-Hys",
        target_size: int = 128
    ):
        self.orientations = orientations
        self.pixels_per_cell = pixels_per_cell
        self.cells_per_block = cells_per_block
        self.block_norm = block_norm
        self.target_size = target_size

        # Validate expected dimensions:
        # For 128x128 with (8,8) cells and (2,2) blocks:
        # num_cells_x = 128 // 8 = 16
        # num_blocks_x = 16 - 2 + 1 = 15
        # 15 * 15 * 2 * 2 * 9 = 8100 features
        cells_x = target_size // pixels_per_cell[0]
        cells_y = target_size // pixels_per_cell[1]
        blocks_x = cells_x - cells_per_block[0] + 1
        blocks_y = cells_y - cells_per_block[1] + 1
        self.expected_dim = blocks_x * blocks_y * (cells_per_block[0] * cells_per_block[1]) * orientations

    def extract_features(
        self,
        preprocessed_gray: np.ndarray,
        visualize: bool = False
    ) -> Tuple[np.ndarray, Optional[np.ndarray]]:
        """
        Extracts fixed-length HOG feature vector from 128x128 grayscale image.
        Returns (feature_vector, hog_image_or_None).
        """
        if preprocessed_gray.shape != (self.target_size, self.target_size):
            preprocessed_gray = cv2.resize(
                preprocessed_gray,
                (self.target_size, self.target_size),
                interpolation=cv2.INTER_LINEAR
            )

        if visualize:
            features, hog_image = hog(
                preprocessed_gray,
                orientations=self.orientations,
                pixels_per_cell=self.pixels_per_cell,
                cells_per_block=self.cells_per_block,
                block_norm=self.block_norm,
                visualize=True
            )
        else:
            features = hog(
                preprocessed_gray,
                orientations=self.orientations,
                pixels_per_cell=self.pixels_per_cell,
                cells_per_block=self.cells_per_block,
                block_norm=self.block_norm,
                visualize=False
            )
            hog_image = None

        features = features.astype(np.float32)
        # Apply global L2 unit normalization so distance metric scales consistently
        norm = float(np.linalg.norm(features))
        if norm > 1e-7:
            features = features / norm

        return features, hog_image

    def compute_gradients_manual(
        self,
        gray_image: np.ndarray
    ) -> Dict[str, np.ndarray]:
        """
        Computes horizontal gradient Gx, vertical gradient Gy,
        magnitude M, and orientation theta as described in Equations (1)-(4)
        of the reference paper.
        """
        img_float = gray_image.astype(np.float32)

        # 1D derivative filters: dx = [-1, 0, 1], dy = [-1, 0, 1]^T
        kernel_x = np.array([[-1, 0, 1]], dtype=np.float32)
        kernel_y = np.array([[-1], [0], [1]], dtype=np.float32)

        gx = cv2.filter2D(img_float, -1, kernel_x)
        gy = cv2.filter2D(img_float, -1, kernel_y)

        # Magnitude = sqrt(Gx^2 + Gy^2)
        magnitude = np.sqrt(gx**2 + gy**2)

        # Orientation = atan2(Gy, Gx) converted to degrees [0, 180)
        orientation = np.arctan2(gy, gx) * (180.0 / np.pi)
        orientation = np.mod(orientation, 180.0)

        return {
            "gx": gx,
            "gy": gy,
            "magnitude": magnitude,
            "orientation": orientation
        }

hog_extractor = HOGFeatureExtractor(
    orientations=settings.HOG_ORIENTATIONS,
    pixels_per_cell=(settings.HOG_PIXELS_PER_CELL, settings.HOG_PIXELS_PER_CELL),
    cells_per_block=(settings.HOG_CELLS_PER_BLOCK, settings.HOG_CELLS_PER_BLOCK),
    block_norm=settings.HOG_BLOCK_NORM,
    target_size=settings.TARGET_FACE_SIZE
)

