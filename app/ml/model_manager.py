import os
import json
from typing import Dict, Any, Optional
from datetime import datetime
from app.config import settings

class ModelArtifactManager:
    """
    Manages active model parameters, algorithm versions, and experiment results.
    """
    def __init__(self, artifacts_dir: Optional[str] = None):
        self.artifacts_dir = artifacts_dir or settings.MODEL_ARTIFACTS_DIR
        self.active_config_path = os.path.join(self.artifacts_dir, "active_model.json")
        self.evaluation_report_path = os.path.join(self.artifacts_dir, "latest_evaluation.json")

    def get_active_model_info(self) -> Dict[str, Any]:
        """Returns the currently deployed model configuration."""
        if os.path.exists(self.active_config_path):
            try:
                with open(self.active_config_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass

        # Return default active configuration based on reference study
        return {
            "version_id": "v1.0-pso-default",
            "algorithm": "HOG-KNN-PSO",
            "status": "ACTIVE",
            "hog": {
                "orientations": settings.HOG_ORIENTATIONS,
                "pixels_per_cell": [settings.HOG_PIXELS_PER_CELL, settings.HOG_PIXELS_PER_CELL],
                "cells_per_block": [settings.HOG_CELLS_PER_BLOCK, settings.HOG_CELLS_PER_BLOCK],
                "block_norm": settings.HOG_BLOCK_NORM,
                "feature_dimension": 8100,
                "target_face_size": [settings.TARGET_FACE_SIZE, settings.TARGET_FACE_SIZE]
            },
            "knn": {
                "k": settings.KNN_DEFAULT_K,
                "metric": "euclidean",
                "weights": "uniform"
            },
            "pso": {
                "num_particles": settings.PSO_NUM_PARTICLES,
                "max_iterations": settings.PSO_MAX_ITERATIONS,
                "inertia_w": 0.7,
                "c1": 1.5,
                "c2": 1.5
            },
            "threshold": settings.RECOGNITION_THRESHOLD,
            "activated_at": datetime.utcnow().isoformat()
        }

    def save_active_model_info(self, config: Dict[str, Any]):
        os.makedirs(self.artifacts_dir, exist_ok=True)
        with open(self.active_config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)

    def save_evaluation_report(self, report: Dict[str, Any]):
        os.makedirs(self.artifacts_dir, exist_ok=True)
        with open(self.evaluation_report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)

    def get_latest_evaluation_report(self) -> Optional[Dict[str, Any]]:
        if os.path.exists(self.evaluation_report_path):
            try:
                with open(self.evaluation_report_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return None

model_manager = ModelArtifactManager()

