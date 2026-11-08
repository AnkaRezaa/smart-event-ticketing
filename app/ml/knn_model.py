from typing import List, Tuple, Dict, Any, Optional
import numpy as np
from sklearn.neighbors import NearestNeighbors, KNeighborsClassifier

class FaceKNNClassifier:
    """
    K-Nearest Neighbor classifier for facial identification and verification
    using Euclidean distance on HOG feature descriptors.
    """
    def __init__(self, k: int = 3, metric: str = "euclidean", weights: str = "uniform"):
        self.k = k
        self.metric = metric
        self.weights = weights
        self.classifier: Optional[KNeighborsClassifier] = None
        self.fitted_features: Optional[np.ndarray] = None
        self.fitted_labels: List[str] = []

    def fit(self, features: np.ndarray, labels: List[str]):
        """Fits the KNN model with enrolled gallery features and labels."""
        if len(labels) == 0:
            self.classifier = None
            self.fitted_features = None
            self.fitted_labels = []
            return

        self.fitted_features = np.asarray(features, dtype=np.float32)
        self.fitted_labels = list(labels)

        # Ensure k does not exceed number of training samples
        effective_k = max(1, min(self.k, len(self.fitted_labels)))
        self.classifier = KNeighborsClassifier(
            n_neighbors=effective_k,
            metric=self.metric,
            weights=self.weights
        )
        self.classifier.fit(self.fitted_features, self.fitted_labels)

    def is_fitted(self) -> bool:
        return self.classifier is not None and len(self.fitted_labels) > 0

    def predict_with_distances(
        self,
        feature_vector: np.ndarray,
        k: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Calculates nearest neighbors and Euclidean distances.
        Returns:
        - predicted_label
        - min_distance
        - neighbor_labels
        - neighbor_distances
        - confidence_score
        """
        if not self.is_fitted():
            return {
                "predicted_label": None,
                "min_distance": float("inf"),
                "neighbor_labels": [],
                "neighbor_distances": [],
                "confidence_score": 0.0
            }

        feat = feature_vector.reshape(1, -1).astype(np.float32)
        effective_k = k or self.k
        effective_k = max(1, min(effective_k, len(self.fitted_labels)))

        # Find k nearest neighbors and distances
        nn = NearestNeighbors(n_neighbors=effective_k, metric=self.metric)
        nn.fit(self.fitted_features)
        distances, indices = nn.kneighbors(feat)

        dist_list = [float(d) for d in distances[0]]
        neighbor_indices = indices[0]
        neighbor_labels = [self.fitted_labels[idx] for idx in neighbor_indices]

        # Majority vote among top k
        from collections import Counter
        vote_counts = Counter(neighbor_labels)
        predicted_label, _ = vote_counts.most_common(1)[0]
        min_distance = dist_list[0]

        # Confidence heuristic inversely proportional to distance: 1 / (1 + distance)
        confidence = 1.0 / (1.0 + min_distance)

        return {
            "predicted_label": predicted_label,
            "min_distance": min_distance,
            "neighbor_labels": neighbor_labels,
            "neighbor_distances": dist_list,
            "confidence_score": float(confidence)
        }

    def compute_distance_to_claimed_user(
        self,
        feature_vector: np.ndarray,
        claimed_user_id: str
    ) -> Dict[str, Any]:
        """
        Computes minimum Euclidean distance specifically between the query feature
        and the enrolled gallery samples of the claimed ticket owner.
        """
        if not self.is_fitted():
            return {
                "has_enrolled_samples": False,
                "min_distance": float("inf"),
                "mean_distance": float("inf")
            }

        # Filter features belonging to claimed_user_id
        user_indices = [i for i, lbl in enumerate(self.fitted_labels) if lbl == claimed_user_id]
        if not user_indices:
            return {
                "has_enrolled_samples": False,
                "min_distance": float("inf"),
                "mean_distance": float("inf")
            }

        user_feats = self.fitted_features[user_indices]
        feat = feature_vector.reshape(1, -1).astype(np.float32)

        # Euclidean distances: sqrt(sum((x - y)^2))
        diffs = user_feats - feat
        dists = np.sqrt(np.sum(diffs ** 2, axis=1))

        return {
            "has_enrolled_samples": True,
            "min_distance": float(np.min(dists)),
            "mean_distance": float(np.mean(dists)),
            "all_distances": [float(d) for d in dists]
        }

