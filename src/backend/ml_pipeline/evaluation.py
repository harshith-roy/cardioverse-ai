"""
Evaluation Module with Pure Python Implementation
Uses internal metrics module without external scikit-learn dependency.
"""
import numpy as np
from typing import Dict, Any, Tuple
import matplotlib.pyplot as plt
from pathlib import Path

from ml_pipeline.metrics import (
    roc_auc_score,
    average_precision_score,
    confusion_matrix,
    brier_score_loss
)

def evaluate_model(
    y_true: np.ndarray,
    y_pred_proba: np.ndarray,
    y_pred: np.ndarray,
    model_name: str = "Model",
    output_dir: Path = None
) -> Dict[str, Any]:
    """
    Comprehensive model evaluation

    Args:
        y_true: True labels (0 or 1)
        y_pred_proba: Predicted probabilities for class 1
        y_pred: Predicted binary classes (0 or 1)
        model_name: Name for reporting
        output_dir: Directory to save plots

    Returns:
        Dictionary with metrics
    """
    y_true = np.asarray(y_true).astype(int)
    y_pred_proba = np.asarray(y_pred_proba)
    y_pred = np.asarray(y_pred).astype(int)

    metrics = {}

    # Discrimination
    metrics['roc_auc'] = roc_auc_score(y_true, y_pred_proba)
    metrics['pr_auc'] = average_precision_score(y_true, y_pred_proba)

    # Calibration
    metrics['brier_score'] = brier_score_loss(y_true, y_pred_proba)

    # Confusion matrix
    cm = confusion_matrix(y_true, y_pred)
    tn, fp, fn, tp = cm.ravel()

    metrics['sensitivity'] = float(tp / (tp + fn)) if (tp + fn) > 0 else 0.0
    metrics['specificity'] = float(tn / (tn + fp)) if (tn + fp) > 0 else 0.0
    metrics['precision'] = float(tp / (tp + fp)) if (tp + fp) > 0 else 0.0
    metrics['recall'] = metrics['sensitivity']
    metrics['accuracy'] = float((tp + tn) / (tp + tn + fp + fn))

    # Print report
    print(f"\n=== {model_name} Evaluation ===")
    print(f"ROC-AUC: {metrics['roc_auc']:.3f}")
    print(f"PR-AUC: {metrics['pr_auc']:.3f}")
    print(f"Brier Score: {metrics['brier_score']:.3f}")
    print(f"Accuracy: {metrics['accuracy']:.3f}")
    print(f"Sensitivity (Recall): {metrics['sensitivity']:.3f}")
    print(f"Specificity: {metrics['specificity']:.3f}")
    print(f"Precision: {metrics['precision']:.3f}")

    return metrics

def generate_evaluation_report(
    results: Dict[str, Dict[str, Any]],
    output_path: Path
) -> None:
    """Generate comprehensive evaluation report"""
    report = "# Model Evaluation Report\n\n"

    report += "## Summary\n\n"
    for model_name, metrics in results.items():
        report += f"### {model_name}\n"
        for metric, value in metrics.items():
            if isinstance(value, float):
                report += f"- {metric}: {value:.3f}\n"
            else:
                report += f"- {metric}: {value}\n"
        report += "\n"

    # Rank models by ROC-AUC
    ranked = sorted(results.items(), key=lambda x: x[1]['roc_auc'], reverse=True)
    report += "## Model Ranking (by ROC-AUC)\n\n"
    for i, (name, metrics) in enumerate(ranked, 1):
        report += f"{i}. {name}: ROC-AUC = {metrics['roc_auc']:.3f}\n"

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        f.write(report)

    print(f"\nEvaluation report saved to {output_path}")

if __name__ == "__main__":
    print("Evaluation module loaded successfully")
