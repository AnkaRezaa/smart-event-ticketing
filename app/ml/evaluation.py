from typing import List, Dict, Any, Tuple
import time
import numpy as np
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, confusion_matrix

def evaluate_classification_metrics(
    y_true: List[str],
    y_pred: List[str]
) -> Dict[str, Any]:
    """
    Computes standard multi-class machine learning evaluation metrics.
    """
    if len(y_true) == 0:
        return {}

    acc = float(accuracy_score(y_true, y_pred))
    p, r, f1, _ = precision_recall_fscore_support(y_true, y_pred, average="weighted", zero_division=0)

    # Unique labels
    labels = sorted(list(set(y_true + y_pred)))
    cm = confusion_matrix(y_true, y_pred, labels=labels)

    return {
        "accuracy": acc,
        "precision": float(p),
        "recall": float(r),
        "f1_score": float(f1),
        "confusion_matrix": cm.tolist(),
        "labels": labels,
        "total_samples": len(y_true)
    }

def evaluate_biometric_verification(
    genuine_matches: List[bool],
    impostor_rejections: List[bool]
) -> Dict[str, Any]:
    """
    Computes biometric acceptance metrics:
    - TP: Genuine user verified
    - FN: Genuine user rejected (False Rejection)
    - TN: Impostor/unknown face rejected
    - FP: Impostor/unknown face accepted (False Acceptance)
    - FAR = FP / (FP + TN)
    - FRR = FN / (TP + FN)
    - Accuracy = (TP + TN) / (TP + TN + FP + FN)
    """
    tp = sum(1 for v in genuine_matches if v is True)
    fn = sum(1 for v in genuine_matches if v is False)
    tn = sum(1 for v in impostor_rejections if v is True)
    fp = sum(1 for v in impostor_rejections if v is False)

    total = tp + fn + tn + fp
    accuracy = (tp + tn) / total if total > 0 else 0.0
    far = fp / (fp + tn) if (fp + tn) > 0 else 0.0
    frr = fn / (tp + fn) if (tp + fn) > 0 else 0.0

    return {
        "tp": tp,
        "fn": fn,
        "tn": tn,
        "fp": fp,
        "accuracy": float(accuracy),
        "far": float(far),
        "frr": float(frr),
        "total_trials": total
    }

