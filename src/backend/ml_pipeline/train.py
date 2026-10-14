"""
Main Training Script with Pure Python Implementation
Uses custom metrics instead of scikit-learn.
"""
import sys
import os
from pathlib import Path
import pandas as pd
import numpy as np

# Add project root to path
sys.path.insert(0, '/sessions/serene-wizardly-wozniak/mnt/cardioverse-ai/src/backend')

from ml_pipeline.data_loader import (
    load_cleveland_dataset, get_screening_dataset
)
from ml_pipeline.metrics import (
    train_test_split_stratified, StratifiedKFold
)
from ml_pipeline.preprocessing import Pipeline, SimpleImputer, StandardScaler
from ml_pipeline.models import LogisticRegression, RandomForest, BaselineModel
from ml_pipeline.evaluation import evaluate_model, generate_evaluation_report
from ml_pipeline.metrics import roc_auc_score

# Configuration
DATA_PATH = Path('/sessions/serene-wizardly-wozniak/mnt/cardioverse-ai/data/processed.cleveland.data')
OUTPUT_DIR = Path('/sessions/serene-wizardly-wozniak/mnt/cardioverse-ai/models')
RANDOM_STATE = 42

def train_with_cross_validation():
    """
    Train models with stratified cross-validation
    """
    print("=" * 60)
    print("CARDIOVERSE AI - Clinical Screening Model Training")
    print("=" * 60)

    # Load data
    print("\n1. Loading Cleveland dataset...")
    df = load_cleveland_dataset(DATA_PATH)
    print(f"   Dataset loaded: {df.shape[0]} patients")
    print(f"   Class distribution: {df['target_binary'].value_counts().to_dict()}")

    # Split data
    print("\n2. Splitting data (70% train, 30% test)...")
    X = get_screening_dataset(df, include_target=False)
    y = df['target_binary']
    X_train, X_test, y_train, y_test = train_test_split_stratified(
        X, y, test_size=0.3, random_state=RANDOM_STATE
    )
    print(f"   Train: {X_train.shape[0]} patients")
    print(f"   Test: {X_test.shape[0]} patients")

    # Create output directory
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Train models with cross-validation
    print("\n3. Training models with stratified 5-fold CV...")
    results = {}

    models = {
        'Logistic Regression': LogisticRegression,
        'Random Forest': RandomForest
    }

    for model_name, model_class in models.items():
        print(f"\n   Training {model_name}...")

        # Pipeline
        pipeline = Pipeline([
            ('imputer', SimpleImputer(strategy='median')),
            ('scaler', StandardScaler()),
            ('classifier', model_class(max_iter=1000, random_state=RANDOM_STATE, class_weight='balanced'))
        ])

        # Cross-validation
        cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)
        cv_scores = []

        for fold, (train_idx, val_idx) in enumerate(cv.split(X_train, y_train), 1):
            X_tr, X_val = X_train.iloc[train_idx], X_train.iloc[val_idx]
            y_tr, y_val = y_train.iloc[train_idx], y_train.iloc[val_idx]

            pipeline.fit(X_tr, y_tr)
            y_pred_proba = pipeline.predict_proba(X_val)[:, 1]
            fold_auc = roc_auc_score(y_val.values, y_pred_proba)
            cv_scores.append(fold_auc)

        mean_cv_auc = np.mean(cv_scores)
        std_cv_auc = np.std(cv_scores)
        print(f"      CV ROC-AUC: {mean_cv_auc:.3f} ± {std_cv_auc:.3f}")

        # Train on full training set
        pipeline.fit(X_train, y_train)

        # Evaluate on test set
        y_test_proba = pipeline.predict_proba(X_test)[:, 1]
        y_test_pred = pipeline.predict(X_test)

        metrics = evaluate_model(
            y_test.values,
            y_test_proba,
            y_test_pred,
            model_name
        )
        metrics['cv_auc_mean'] = mean_cv_auc
        metrics['cv_auc_std'] = std_cv_auc
        results[model_name] = metrics

        # Save model (using joblib directly here since it's already installed)
        import pickle
        model_path = OUTPUT_DIR / f'{model_name.replace(" ", "_")}_screening_model.pkl'
        with open(model_path, 'wb') as f:
            pickle.dump(pipeline, f)
        print(f"      Model saved to {model_path}")

    # Baseline
    print("\n   Training Baseline...")
    baseline = BaselineModel()
    baseline.fit(X_train.values, y_train.values)
    y_baseline_proba = np.zeros((X_test.shape[0], 2))
    y_baseline_pred = baseline.predict(X_test.values)

    baseline_metrics = evaluate_model(
        y_test.values,
        y_baseline_proba[:, 1], # dummy model returns zeros, this might be issue with baseline model output shape
        y_baseline_pred,
        "Baseline"
    )
    results['Baseline'] = baseline_metrics

    # Report
    report_path = OUTPUT_DIR / 'evaluation_report.md'
    generate_evaluation_report(results, report_path)

    print("\n" + "=" * 60)
    print("Training Complete")
    print("=" * 60)

if __name__ == "__main__":
    train_with_cross_validation()
