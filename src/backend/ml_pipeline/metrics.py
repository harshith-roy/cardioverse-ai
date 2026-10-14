"""
Standalone Pure Python/NumPy Metrics and Validation Utilities
Does not require scikit-learn.
"""
import numpy as np
import pandas as pd
from typing import Tuple, List, Dict, Any

def roc_auc_score(y_true: np.ndarray, y_score: np.ndarray) -> float:
    """
    Calculate ROC-AUC using Mann-Whitney U test (Wilcoxon rank-sum statistic).
    Mathematically identical to sklearn's roc_auc_score.
    """
    y_true = np.asarray(y_true)
    y_score = np.asarray(y_score)

    n_pos = np.sum(y_true == 1)
    n_neg = np.sum(y_true == 0)

    if n_pos == 0 or n_neg == 0:
        return 0.5

    # Rank all scores
    order = np.argsort(y_score)
    ranks = np.empty_like(order, dtype=float)
    ranks[order] = np.arange(1, len(y_score) + 1)

    # Handle ties by assigning average rank
    unique_scores, counts = np.unique(y_score, return_counts=True)
    for score, count in zip(unique_scores, counts):
        if count > 1:
            tie_mask = (y_score == score)
            ranks[tie_mask] = np.mean(ranks[tie_mask])

    rank_sum_pos = np.sum(ranks[y_true == 1])
    u_stat = rank_sum_pos - (n_pos * (n_pos + 1)) / 2.0
    auc = u_stat / (n_pos * n_neg)
    return float(auc)

def confusion_matrix(y_true: np.ndarray, y_pred: np.ndarray) -> np.ndarray:
    """Calculate 2x2 confusion matrix [[tn, fp], [fn, tp]]"""
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)
    tn = np.sum((y_true == 0) & (y_pred == 0))
    fp = np.sum((y_true == 0) & (y_pred == 1))
    fn = np.sum((y_true == 1) & (y_pred == 0))
    tp = np.sum((y_true == 1) & (y_pred == 1))
    return np.array([[tn, fp], [fn, tp]])

def brier_score_loss(y_true: np.ndarray, y_prob: np.ndarray) -> float:
    """Mean squared difference between predicted probabilities and outcomes"""
    y_true = np.asarray(y_true)
    y_prob = np.asarray(y_prob)
    return float(np.mean((y_prob - y_true) ** 2))

def average_precision_score(y_true: np.ndarray, y_score: np.ndarray) -> float:
    """Calculate PR-AUC using trapezoidal/step integration"""
    y_true = np.asarray(y_true)
    y_score = np.asarray(y_score)

    order = np.argsort(-y_score)
    y_eval = y_true[order]

    tp_cumsum = np.cumsum(y_eval == 1)
    fp_cumsum = np.cumsum(y_eval == 0)

    precision = tp_cumsum / (tp_cumsum + fp_cumsum)
    recall = tp_cumsum / np.sum(y_true == 1)

    # Step integration
    recall_diff = np.diff(np.insert(recall, 0, 0))
    ap = np.sum(precision * recall_diff)
    return float(ap)

class StratifiedKFold:
    """Pure NumPy implementation of Stratified K-Fold cross validation"""
    def __init__(self, n_splits: int = 5, shuffle: bool = True, random_state: int = 42):
        self.n_splits = n_splits
        self.shuffle = shuffle
        self.random_state = random_state

    def split(self, X: Any, y: Any):
        y_arr = np.asarray(y)
        rng = np.random.RandomState(self.random_state)

        pos_idx = np.where(y_arr == 1)[0]
        neg_idx = np.where(y_arr == 0)[0]

        if self.shuffle:
            rng.shuffle(pos_idx)
            rng.shuffle(neg_idx)

        pos_folds = np.array_split(pos_idx, self.n_splits)
        neg_folds = np.array_split(neg_idx, self.n_splits)

        for fold in range(self.n_splits):
            val_idx = np.concatenate([pos_folds[fold], neg_folds[fold]])
            train_idx = np.concatenate([
                np.concatenate([pos_folds[f] for f in range(self.n_splits) if f != fold]),
                np.concatenate([neg_folds[f] for f in range(self.n_splits) if f != fold])
            ])
            yield train_idx, val_idx

def train_test_split_stratified(
    X: pd.DataFrame,
    y: pd.Series,
    test_size: float = 0.3,
    random_state: int = 42
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    """Stratified train test split without scikit-learn"""
    rng = np.random.RandomState(random_state)
    y_arr = np.asarray(y)

    pos_idx = np.where(y_arr == 1)[0]
    neg_idx = np.where(y_arr == 0)[0]

    rng.shuffle(pos_idx)
    rng.shuffle(neg_idx)

    n_pos_test = int(len(pos_idx) * test_size)
    n_neg_test = int(len(neg_idx) * test_size)

    test_idx = np.concatenate([pos_idx[:n_pos_test], neg_idx[:n_neg_test]])
    train_idx = np.concatenate([pos_idx[n_pos_test:], neg_idx[n_neg_test:]])

    rng.shuffle(test_idx)
    rng.shuffle(train_idx)

    return X.iloc[train_idx].copy(), X.iloc[test_idx].copy(), y.iloc[train_idx].copy(), y.iloc[test_idx].copy()
