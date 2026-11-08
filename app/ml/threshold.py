from typing import Dict, Any, List, Tuple
import numpy as np

class ThresholdCalibrator:
    """
    Manages calibrated Euclidean distance rejection thresholds
    to distinguish genuine known enrolled users from unknown faces or impostors.
    """
    def __init__(self, default_threshold: float = 0.65):
        self.threshold = default_threshold

    def evaluate_decision(
        self,
        min_distance: float,
        threshold: float = None
    ) -> bool:
        """
        Returns True if min_distance <= threshold (accepted as known identity),
        False if min_distance > threshold (rejected as UNKNOWN).
        """
        thresh = threshold if threshold is not None else self.threshold
        return min_distance <= thresh

    def calibrate_from_distances(
        self,
        genuine_distances: List[float],
        impostor_distances: List[float],
        target_metric: str = "equal_error_rate"
    ) -> Dict[str, Any]:
        """
        Calibrates optimal threshold based on genuine and impostor distance distributions.
        Calculates FAR (False Acceptance Rate) and FRR (False Rejection Rate).
        """
        if not genuine_distances or not impostor_distances:
            return {
                "optimal_threshold": self.threshold,
                "eer": None,
                "thresholds_evaluated": []
            }

        all_dists = sorted(list(genuine_distances) + list(impostor_distances))
        candidate_thresholds = np.linspace(min(all_dists), max(all_dists), 100)

        best_thresh = self.threshold
        min_diff = float("inf")
        best_eer = 1.0

        gen_arr = np.array(genuine_distances)
        imp_arr = np.array(impostor_distances)

        records = []
        for t in candidate_thresholds:
            # Genuine rejected (distance > t)
            frr = float(np.mean(gen_arr > t))
            # Impostor accepted (distance <= t)
            far = float(np.mean(imp_arr <= t))

            records.append({
                "threshold": float(t),
                "far": far,
                "frr": frr,
                "diff": abs(far - frr)
            })

            if abs(far - frr) < min_diff:
                min_diff = abs(far - frr)
                best_thresh = float(t)
                best_eer = float((far + frr) / 2.0)

        self.threshold = best_thresh
        return {
            "optimal_threshold": best_thresh,
            "eer": best_eer,
            "records": records
        }

threshold_calibrator = ThresholdCalibrator(default_threshold=0.65)

