import os
import json
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import numpy as np
from app.config import settings

class FeatureGallery:
    """
    Manages persisted facial feature vectors and labels for enrolled participants.
    Stored under storage/features/gallery.npz.
    """
    def __init__(self, gallery_path: Optional[str] = None):
        self.gallery_path = gallery_path or os.path.join(settings.FEATURES_DIR, "gallery.npz")
        self.meta_path = gallery_path or os.path.join(settings.FEATURES_DIR, "gallery_meta.json")
        self.features: np.ndarray = np.empty((0, 8100), dtype=np.float32)
        self.labels: List[str] = []
        self.sample_ids: List[str] = []
        self.load()

    def load(self) -> bool:
        if os.path.exists(self.gallery_path) and os.path.exists(self.meta_path):
            try:
                data = np.load(self.gallery_path)
                self.features = data["features"].astype(np.float32)
                # Ensure existing features are unit-normalized
                if len(self.features) > 0:
                    norms = np.linalg.norm(self.features, axis=1, keepdims=True)
                    norms[norms < 1e-7] = 1.0
                    self.features = self.features / norms
                with open(self.meta_path, "r", encoding="utf-8") as f:
                    meta = json.load(f)
                    self.labels = meta.get("labels", [])
                    self.sample_ids = meta.get("sample_ids", [])
                return True
            except Exception as e:
                print(f"Warning: Failed to load gallery: {e}")
                return False
        return False

    def save(self):
        os.makedirs(os.path.dirname(self.gallery_path), exist_ok=True)
        if len(self.features) > 0:
            norms = np.linalg.norm(self.features, axis=1, keepdims=True)
            norms[norms < 1e-7] = 1.0
            self.features = (self.features / norms).astype(np.float32)
        np.savez_compressed(self.gallery_path, features=self.features)
        with open(self.meta_path, "w", encoding="utf-8") as f:
            json.dump({
                "labels": self.labels,
                "sample_ids": self.sample_ids,
                "count": len(self.labels),
                "feature_dim": int(self.features.shape[1]) if len(self.features) > 0 else 8100
            }, f, indent=2)

    def add_features(self, user_id: str, sample_id: str, feature_vector: np.ndarray):
        """Adds a single feature vector for a user."""
        feat = feature_vector.reshape(1, -1).astype(np.float32)
        norm = float(np.linalg.norm(feat))
        if norm > 1e-7:
            feat = feat / norm
        if len(self.features) == 0:
            self.features = feat
        else:
            self.features = np.vstack([self.features, feat])
        self.labels.append(user_id)
        self.sample_ids.append(sample_id)
        self.save()

    def remove_user(self, user_id: str):
        """Removes all enrolled features of a specific user."""
        indices = [i for i, lbl in enumerate(self.labels) if lbl != user_id]
        if len(indices) == len(self.labels):
            return
        if len(indices) == 0:
            self.features = np.empty((0, 8100), dtype=np.float32)
            self.labels = []
            self.sample_ids = []
        else:
            self.features = self.features[indices]
            self.labels = [self.labels[i] for i in indices]
            self.sample_ids = [self.sample_ids[i] for i in indices]
        self.save()

    def get_user_features(self, user_id: str) -> np.ndarray:
        """Returns all feature vectors for a given user."""
        indices = [i for i, lbl in enumerate(self.labels) if lbl == user_id]
        if not indices:
            return np.empty((0, 8100), dtype=np.float32)
        return self.features[indices]

    def get_all(self) -> Tuple[np.ndarray, List[str]]:
        return self.features, self.labels

    def count(self) -> int:
        return len(self.labels)

    def unique_users(self) -> List[str]:
        return list(set(self.labels))

default_gallery = FeatureGallery()

