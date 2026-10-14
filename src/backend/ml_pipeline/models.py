"""
Pure Python Model Implementations
"""
import numpy as np
from typing import Dict, Any, Tuple, List, Optional

class LogisticRegression:
    """Logistic Regression Implementation"""
    def __init__(self, max_iter: int = 1000, random_state: int = 42, class_weight: str = None):
        self.max_iter = max_iter
        self.random_state = random_state
        self.class_weight = class_weight
        self.coef_ = None
        self.intercept_ = None
        self.classes_ = None
        self._weights_ = None
        self._bias_ = None

    def fit(self, X: np.ndarray, y: np.ndarray) -> 'LogisticRegression':
        np.random.seed(self.random_state)
        self._weights_ = np.random.randn(X.shape[1])
        self._bias_ = 0.0

        for _ in range(self.max_iter):
            # Linear prediction
            z = np.dot(X, self._weights_) + self._bias_
            # Sigmoid activation
            a = 1 / (1 + np.exp(-z))
            # Gradient descent
            dw = (1 / len(y)) * np.dot(X.T, (a - y))
            db = (1 / len(y)) * np.sum(a - y)
            # Update parameters
            self._weights_ -= dw
            self._bias_ -= db

        # Store coefficients
        self.coef_ = self._weights_
        self.intercept_ = self._bias_
        self.classes_ = np.array([0, 1])
        return self

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        z = np.dot(X, self._weights_) + self._bias_
        a = 1 / (1 + np.exp(-z))
        return np.column_stack((1 - a, a))

    def predict(self, X: np.ndarray) -> np.ndarray:
        z = np.dot(X, self._weights_) + self._bias_
        a = 1 / (1 + np.exp(-z))
        return np.where(a >= 0.5, 1, 0)


class RandomForest:
    """Random Forest Implementation"""
    def __init__(self, n_estimators: int = 200, max_depth: int = 6, random_state: int = 42, class_weight: str = None):
        self.n_estimators = n_estimators
        self.max_depth = max_depth
        self.random_state = random_state
        self.class_weight = class_weight
        self.models_ = []

    def _build_tree(self, X: np.ndarray, y: np.ndarray, depth: int = 0) -> Tuple[Any, Any]:
        # Base case
        if depth >= self.max_depth or len(np.unique(y)) == 1:
            return np.mean(y), None

        # Select random features
        n_features = X.shape[1]
        feature_indices = np.random.choice(n_features, min(n_features, 5), replace=False)
        X_subset = X[:, feature_indices]

        # Find best split
        best_score = -np.inf
        best_feature = None
        best_threshold = None

        for feature_idx in range(X_subset.shape[1]):
            thresholds = np.unique(X_subset[:, feature_idx])
            for threshold in thresholds:
                y_pred = np.where(X_subset[:, feature_idx] <= threshold, 0, 1)
                gini = 1 - (np.sum((y == y_pred) * (y == 0))**2 + np.sum((y == y_pred) * (y == 1))**2) / len(y)
                if gini > best_score:
                    best_score = gini
                    best_feature = feature_idx
                    best_threshold = threshold

        if best_feature is None:
            return np.mean(y), None

        # Split data
        mask = X_subset[:, best_feature] <= best_threshold
        y_left = y[mask]
        y_right = y[~mask]

        # Recursively build tree
        left_subtree, right_subtree = self._build_tree(X, y, depth + 1)

        return (left_subtree[0] * len(y_left) + right_subtree[0] * len(y_right)) / len(y), best_feature

    def fit(self, X: np.ndarray, y: np.ndarray) -> 'RandomForest':
        for _ in range(self.n_estimators):
            np.random.seed(self.random_state + _)
            model = self._build_tree(X, y)
            self.models_.append(model)
        return self

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        probas = np.zeros((X.shape[0], 2))
        for model in self.models_:
            # Simplified prediction
            pred = np.where(X <= model[1], 0, 1)
            probas += np.where(pred == 0, 1, 0)
        return probas / len(self.models_)

    def predict(self, X: np.ndarray) -> np.ndarray:
        return np.where(self.predict_proba(X)[:, 1] >= 0.5, 1, 0)


class BaselineModel:
    """Baseline Model (Most Frequent Class)"""
    def __init__(self):
        self.classes_ = None
        self.classes_ = np.array([0, 1])

    def fit(self, X: np.ndarray, y: np.ndarray) -> 'BaselineModel':
        self.classes_ = np.unique(y)
        self.class_ = np.argmax(np.bincount(y))
        return self

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        return np.zeros((X.shape[0], 2))

    def predict(self, X: np.ndarray) -> np.ndarray:
        return np.full(X.shape[0], self.class_)


if __name__ == "__main__":
    print("Pure Python Models Ready")