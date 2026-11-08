import numpy as np
import pytest
from app.ml.knn_model import FaceKNNClassifier
from app.ml.threshold import ThresholdCalibrator
from app.ml.pso_optimizer import ParticleSwarmOptimizer

def test_knn_fit_and_predict():
    knn = FaceKNNClassifier(k=3)
    dim = 8100

    # 3 mock identities with distinct feature vectors
    class_a = np.ones((5, dim), dtype=np.float32) * 0.1
    class_b = np.ones((5, dim), dtype=np.float32) * 0.5
    class_c = np.ones((5, dim), dtype=np.float32) * 0.9

    X = np.vstack([class_a, class_b, class_c])
    y = ["User_A"] * 5 + ["User_B"] * 5 + ["User_C"] * 5

    knn.fit(X, y)
    assert knn.is_fitted()

    # Query matching User_A
    query_a = np.ones(dim, dtype=np.float32) * 0.12
    res = knn.predict_with_distances(query_a)

    assert res["predicted_label"] == "User_A"
    assert res["min_distance"] < 2.0
    assert len(res["neighbor_labels"]) == 3

def test_claimed_identity_distance():
    knn = FaceKNNClassifier(k=1)
    dim = 8100

    feat_a = np.zeros((2, dim), dtype=np.float32)
    feat_b = np.ones((2, dim), dtype=np.float32)
    knn.fit(np.vstack([feat_a, feat_b]), ["Alice", "Alice", "Bob", "Bob"])

    # Query is close to Alice
    query = np.zeros(dim, dtype=np.float32) + 0.05
    dist_alice = knn.compute_distance_to_claimed_user(query, "Alice")
    dist_bob = knn.compute_distance_to_claimed_user(query, "Bob")

    assert dist_alice["has_enrolled_samples"] is True
    assert dist_bob["has_enrolled_samples"] is True
    assert dist_alice["min_distance"] < dist_bob["min_distance"]

def test_threshold_rejection():
    calibrator = ThresholdCalibrator(default_threshold=0.65)
    # Distance <= 0.65 is accepted
    assert calibrator.evaluate_decision(0.45) is True
    assert calibrator.evaluate_decision(0.65) is True
    # Distance > 0.65 is rejected as UNKNOWN
    assert calibrator.evaluate_decision(0.72) is False

def test_pso_optimizer():
    # Test PSO parameter tuning
    np.random.seed(42)
    X_train = np.random.uniform(0, 1, size=(20, 100)).astype(np.float32)
    y_train = ["A"] * 10 + ["B"] * 10
    X_val = np.random.uniform(0, 1, size=(10, 100)).astype(np.float32)
    y_val = ["A"] * 5 + ["B"] * 5

    pso = ParticleSwarmOptimizer(num_particles=4, max_iter=3, bounds=[(1.0, 5.0), (0.4, 0.8)])
    res = pso.optimize(X_train, y_train, X_val, y_val)

    assert "optimized_k" in res
    assert 1 <= res["optimized_k"] <= 5
    assert 0.4 <= res["optimized_threshold"] <= 0.8
    assert len(res["fitness_history"]) == 3

