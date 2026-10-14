"""
External Validation Module
Validates model on Hungarian and VA cohorts
"""
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, Any, Tuple

SCREENING_FEATURES = [
    'age', 'sex', 'cp', 'trestbps', 'chol',
    'fbs', 'restecg'
]

def load_external_dataset(
    filepath: Path,
    dataset_name: str
) -> pd.DataFrame:
    """
    Load external validation dataset

    Args:
        filepath: Path to dataset file
        dataset_name: Name of dataset for logging

    Returns:
        DataFrame with screening features
    """
    # Load data
    df = pd.read_csv(
        filepath,
        header=None,
        sep=',',
        na_values=['-9', '?', ''],
        engine='python'
    )

    # Set column names
    cols = SCREENING_FEATURES + ['thalach', 'exang', 'oldpeak', 'slope', 'ca', 'thal', 'num']
    df.columns = cols

    # Create binary target
    df['target_binary'] = (df['num'] > 0).astype(int)

    print(f"Loaded {dataset_name}: {df.shape[0]} patients")
    print(f"Class distribution: {df['target_binary'].value_counts().to_dict()}")

    # Check feature availability
    missing_features = []
    for feature in SCREENING_FEATURES:
        if feature not in df.columns:
            missing_features.append(feature)
        elif df[feature].isna().sum() > 0:
            print(f"Warning: {feature} has {df[feature].isna().sum()} missing values")

    if missing_features:
        print(f"Error: Missing features: {missing_features}")
        raise ValueError(f"Missing required features: {missing_features}")

    return df


def validate_model_external(
    model,
    X_external: pd.DataFrame,
    y_external: pd.Series,
    dataset_name: str
) -> Dict[str, Any]:
    """
    Validate model on external dataset

    Args:
        model: Trained model pipeline
        X_external: External features
        y_external: External targets
        dataset_name: Name for reporting

    Returns:
        Evaluation metrics
    """
    from ml_pipeline.evaluation import evaluate_model

    print(f"\nValidating on {dataset_name}...")
    print(f"Samples: {X_external.shape[0]}")
    print(f"Features: {X_external.shape[1]}")

    # Predict
    y_pred_proba = model.predict_proba(X_external)[:, 1]
    y_pred = model.predict(X_external)

    # Evaluate
    metrics = evaluate_model(
        y_external.values,
        y_pred_proba,
        y_pred,
        f"External Validation - {dataset_name}"
    )

    return metrics


def compare_external_performance(
    internal_metrics: Dict[str, Any],
    external_metrics: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Compare internal vs external performance

    Args:
        internal_metrics: Metrics from internal validation
        external_metrics: Metrics from external validation

    Returns:
        Comparison summary
    """
    comparison = {}

    for metric in ['roc_auc', 'sensitivity', 'specificity', 'accuracy']:
        if metric in internal_metrics and metric in external_metrics:
            internal_val = internal_metrics[metric]
            external_val = external_metrics[metric]

            comparison[metric] = {
                'internal': internal_val,
                'external': external_val,
                'difference': external_val - internal_val,
                'degradation_percent': ((internal_val - external_val) / internal_val * 100)
            }

    return comparison


def generate_external_validation_report(
    validation_results: Dict[str, Dict[str, Any]],
    output_path: Path
) -> None:
    """
    Generate external validation report

    Args:
        validation_results: Dictionary of validation results
        output_path: Output file path
    """
    report = "# External Validation Report\n\n"

    report += "## Validation Overview\n\n"
    report += "Model validation on external cohorts to assess generalizability.\n\n"

    for dataset_name, metrics in validation_results.items():
        report += f"### {dataset_name}\n\n"
        report += f"Samples: {metrics.get('samples', 'N/A')}\n"
        report += f"Class Distribution: {metrics.get('class_dist', 'N/A')}\n\n"

        for metric, value in metrics.items():
            if metric not in ['samples', 'class_dist']:
                report += f"- {metric}: {value:.3f}\n"
        report += "\n"

    report += "## Generalizability Assessment\n\n"
    report += "External validation performance compared to internal validation:\n\n"

    for metric, comp in validation_results.get('comparison', {}).items():
        report += f"- **{metric}**:\n"
        report += f"  - Internal: {comp['internal']:.3f}\n"
        report += f"  - External: {comp['external']:.3f}\n"
        report += f"  - Degradation: {comp['degradation_percent']:.1f}%\n\n"

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        f.write(report)

    print(f"External validation report saved to {output_path}")


if __name__ == "__main__":
    print("External validation module loaded successfully")
