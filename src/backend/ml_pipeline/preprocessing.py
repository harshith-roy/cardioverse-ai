"""
Pure NumPy/Pandas Data Preprocessing Pipeline
"""
import numpy as np
import pandas as pd
from typing import Tuple, List, Dict, Any

class SimpleImputer:
    """Median Imputer for numeric data"""
    def __init__(self, strategy: str = 'median'):
        self.strategy = strategy
        self.fill_values_ = {}

    def fit(self, X: pd.DataFrame) -> 'SimpleImputer':
        for col in X.columns:
            if self.strategy == 'median':
                self.fill_values_[col] = X[col].median()
            elif self.strategy == 'mean':
                self.fill_values_[col] = X[col].mean()
            else:
                self.fill_values_[col] = X[col].mode()[0]
        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        X_out = X.copy()
        for col, val in self.fill_values_.items():
            if col in X_out.columns:
                X_out[col] = X_out[col].fillna(val)
        return X_out

    def fit_transform(self, X: pd.DataFrame) -> pd.DataFrame:
        return self.fit(X).transform(X)


class StandardScaler:
    """Standard Scaler (Z-score normalization)"""
    def __init__(self):
        self.mean_ = None
        self.scale_ = None

    def fit(self, X: pd.DataFrame) -> 'StandardScaler':
        self.mean_ = X.mean(axis=0)
        self.scale_ = X.std(axis=0)
        # Avoid division by zero
        self.scale_ = self.scale_.replace(0, 1.0)
        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        X_out = (X - self.mean_) / self.scale_
        return X_out

    def fit_transform(self, X: pd.DataFrame) -> pd.DataFrame:
        return self.fit(X).transform(X)


class Pipeline:
    """Sequential Data Preprocessing Pipeline"""
    def __init__(self, steps: List[Tuple[str, Any]]):
        self.steps = steps

    def fit(self, X: pd.DataFrame, y=None) -> 'Pipeline':
        X_trans = X.copy()
        for name, step in self.steps[:-1]:
            X_trans = step.fit_transform(X_trans)
        self.steps[-1][1].fit(X_trans, y)
        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        X_trans = X.copy()
        for name, step in self.steps[:-1]:
            X_trans = step.transform(X_trans)
        return X_trans

    def fit_transform(self, X: pd.DataFrame, y=None) -> pd.DataFrame:
        self.fit(X, y)
        return self.transform(X)

    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        X_trans = X.copy()
        for name, step in self.steps[:-1]:
            X_trans = step.transform(X_trans)
        return self.steps[-1][1].predict_proba(X_trans)

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        X_trans = X.copy()
        for name, step in self.steps[:-1]:
            X_trans = step.transform(X_trans)
        return self.steps[-1][1].predict(X_trans)


if __name__ == "__main__":
    print("Pure NumPy/Pandas Preprocessing Pipeline Ready")
