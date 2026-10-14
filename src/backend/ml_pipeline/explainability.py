"""
Explainable AI Module for Clinical Screening Model
Provides logistic regression feature contributions in log-odds space.
"""
import numpy as np
from typing import Dict, Any, List
from pathlib import Path


class LogisticRegressionExplainability:
    """
    Compute feature contributions for Logistic Regression in log-odds space.

    For a logistic regression model: p = 1 / (1 + exp(-(b0 + b1*x1 + ... + bn*xn)))
    The log-odds contribution of feature j is: bj * (xj - mean_j) / std_j
    after standardization. The intercept b0 is included separately.

    IMPORTANT: Contributions are in log-odds space, NOT direct probability
    percentage points. Do NOT interpret as direct causal effects.
    """

    def __init__(
        self,
        coefficients: np.ndarray,
        intercept: float,
        feature_names: List[str],
        feature_means: np.ndarray,
        feature_stds: np.ndarray,
        class_labels: List[str] = None,
    ):
        """
        Initialize with trained model parameters.

        Args:
            coefficients: Model coefficients [b1, ..., bn] (1D array)
            intercept: Model intercept b0
            feature_names: List of feature names (length n)
            feature_means: Means used for StandardScaler (length n)
            feature_stds: Standard deviations used for StandardScaler (length n)
            class_labels: ['negative', 'positive'] or similar
        """
        self.coefficients = np.asarray(coefficients, dtype=float).flatten()
        self.intercept = float(intercept)
        self.feature_names = list(feature_names)
        self.feature_means = np.asarray(feature_means, dtype=float).flatten()
        self.feature_stds = np.asarray(feature_stds, dtype=float).flatten()
        self.class_labels = class_labels or ["No Disease", "Disease"]

        # Validate
        n = len(self.feature_names)
        assert self.coefficients.shape == (n,), (
            f"coefficient shape {self.coefficients.shape} != expected ({n})"
        )
        assert self.feature_means.shape == (n,), (
            f"feature_means shape {self.feature_means.shape} != expected ({n})"
        )
        assert self.feature_stds.shape == (n,), (
            f"feature_stds shape {self.feature_stds.shape} != expected ({n})"
        )
        assert self.feature_stds.min() > 0, "Standard deviations must be positive"

    def compute_contributions(
        self,
        patient_features: np.ndarray,
    ) -> Dict[str, Any]:
        """
        Compute feature contributions in log-odds space.

        For standardized features: contribution_j = bj * (xj - mean_j) / std_j
        The log-odds = intercept + sum(contribution_j for j in 1..n)
        Probability = 1 / (1 + exp(-log-odds))

        Args:
            patient_features: Array of feature values [x1, ..., xn]

        Returns:
            Dictionary with probability, log-odds, and contributions.
        """
        patient_features = np.asarray(patient_features, dtype=float).flatten()
        n = len(self.feature_names)

        if patient_features.shape[0] != n:
            raise ValueError(
                f"Expected {n} features, got {patient_features.shape[0]}"
            )

        # Standardized features: (x - mean) / std
        scaled = (patient_features - self.feature_means) / self.feature_stds

        # Contribution of each feature to log-odds: bj * scaled_j
        contributions = self.coefficients * scaled

        # Log-odds and probability
        log_odds = self.intercept + float(np.sum(contributions))
        probability = 1.0 / (1.0 + np.exp(-log_odds))

        # Separate positive and negative contributions based on CONTRIBUTION SIGN
        # contribution > 0 increases log-odds (increases risk)
        # contribution < 0 decreases log-odds (decreases risk)
        pos_contribs: Dict[str, float] = {}
        neg_contribs: Dict[str, float] = {}

        for i, (name, contrib) in enumerate(
            zip(self.feature_names, contributions)
        ):
            if contrib > 0:
                pos_contribs[name] = float(contrib)
            elif contrib < 0:
                neg_contribs[name] = float(contrib)
            # contrib == 0 goes to neither (neutral)

        # Aggregate mapping from feature name to its contribution value
        all_contribs: Dict[str, float] = {}
        for name, c in pos_contribs.items():
            all_contribs[name] = c
        for name, c in neg_contribs.items():
            all_contribs[name] = c

        # Sort features by absolute contribution
        sorted_features = sorted(all_contribs.keys(),
                                 key=lambda k: abs(all_contribs[k]),
                                 reverse=True)

        return {
            "probability": float(probability),
            "log_odds": float(log_odds),
            "positive_contributions": pos_contribs,
            "negative_contributions": neg_contribs,
            "all_contributions": all_contribs,
            "sorted_features": sorted_features,
        }

    def explain_patient(self, patient_data: Dict[str, float]) -> Dict[str, Any]:
        """
        Generate explanation for a patient's feature values.

        Args:
            patient_data: Dict with feature names as keys and numeric values.

        Returns:
            Dictionary with probability, log-odds, contributions, and summary.
        """
        # Convert to array in feature order
        feature_values: Dict[str, float] = {}
        patient_array: List[float] = []

        for name in self.feature_names:
            if name in patient_data:
                val = float(patient_data[name])
                patient_array.append(val)
                feature_values[name] = val
            else:
                raise ValueError(f"Missing feature: {name}")

        patient_array_np = np.array(patient_array, dtype=float)

        # Compute contributions
        contributions = self.compute_contributions(patient_array_np)

        # Build summary text
        prob = contributions["probability"]
        lodds = contributions["log_odds"]
        pos = contributions["positive_contributions"]
        neg = contributions["negative_contributions"]
        all_contribs = contributions["all_contributions"]
        sorted_f = contributions["sorted_features"]

        # Top 3 factors
        top_3 = sorted_f[:3]
        top_lines = []
        for name in top_3:
            c = all_contribs.get(name, 0.0)
            direction = "increases" if name in pos else "decreases"
            top_lines.append(f"  {name}: {direction} risk ( contrib={c:+.3f} )")

        summary = (
            f"Probability: {prob:.1%}, Log-Odds: {lodds:.3f}\n"
            f"Top factors: {', '.join(top_lines)}"
        )

        return {
            "probability": float(prob),
            "log_odds": float(lodds),
            "positive_contributions": contributions["positive_contributions"],
            "negative_contributions": contributions["negative_contributions"],
            "all_contributions": contributions["all_contributions"],
            "sorted_features": contributions["sorted_features"],
            "summary": summary,
        }


def load_explainability_model(model_path: Path) -> LogisticRegressionExplainability:
    """
    Load the explainability model from the trained pipeline artifact.

    Args:
        model_path: Path to the pickle file containing the trained pipeline

    Returns:
        LogisticRegressionExplainability instance ready for explanations.
    """
    import pickle

    with open(model_path, "rb") as f:
        pipeline = pickle.load(f)

    # Extract pipeline components
    imputer_step = pipeline.steps[0][1]  # imputer
    scaler_step = pipeline.steps[1][1]  # scaler
    classifier_step = pipeline.steps[2][1]  # LogisticRegression

    # Get feature names from the original training data
    import sys
    sys_path_backup = sys.path[:]
    try:
        sys.path.insert(0, str(Path(__file__).parent.parent.parent
                                / "src" / "backend" / "ml_pipeline"))
        from ml_pipeline.data_loader import load_cleveland_dataset, get_screening_dataset
        df = load_cleveland_dataset(
            Path(r"C:\Users\konda\Downloads\cardioverse-ai\data\processed.cleveland.data")
        )
        feature_names = list(get_screening_dataset(df, include_target=False).columns)
    finally:
        sys.path = sys_path_backup

    # Compute means and stds from the fitted scaler
    feature_means = np.array([scaler_step.mean_[name] for name in feature_names])
    feature_stds = np.array([scaler_step.scale_[name] for name in feature_names])

    # Extract model parameters
    coefficients = classifier_step.coef_[0]  # shape: (n_features,)
    intercept = float(classifier_step.intercept_)

    # Class labels
    class_labels = ["No CAD", "CAD"]

    return LogisticRegressionExplainability(
        coefficients=coefficients,
        intercept=intercept,
        feature_names=feature_names,
        feature_means=feature_means,
        feature_stds=feature_stds,
        class_labels=class_labels,
    )