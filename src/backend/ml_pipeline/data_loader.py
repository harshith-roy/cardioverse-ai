"""
Data Loader Module
Handles loading and verification of UCI Heart Disease datasets
"""
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Tuple, Dict, Optional

# Feature definitions
SCREENING_FEATURES = [
    'age', 'sex', 'cp', 'trestbps', 'chol',
    'fbs', 'restecg'
]

ALL_FEATURES = SCREENING_FEATURES + [
    'thalach', 'exang', 'oldpeak', 'slope', 'ca', 'thal'
]

TARGET_COLUMN = 'num'

def load_cleveland_dataset(data_path: Path) -> pd.DataFrame:
    """
    Load Cleveland heart disease dataset with proper validation

    Args:
        data_path: Path to processed.cleveland.data file

    Returns:
        DataFrame with proper column names and validated schema
    """
    # Verify file exists
    if not data_path.exists():
        raise FileNotFoundError(f"Dataset not found at {data_path}")

    # Load with proper parsing
    df = pd.read_csv(
        data_path,
        header=None,
        sep=',',
        na_values=['-9', '?', ''],
        engine='python'
    )

    # Set column names
    feature_names = SCREENING_FEATURES + ['thalach', 'exang', 'oldpeak', 'slope', 'ca', 'thal', TARGET_COLUMN]
    df.columns = feature_names

    # Verify schema
    _validate_schema(df)

    # Create binary target (0 vs 1+)
    df['target_binary'] = (df[TARGET_COLUMN] > 0).astype(int)

    return df

def _validate_schema(df: pd.DataFrame) -> None:
    """Validate dataset schema and data integrity"""
    # Check required columns
    required_cols = SCREENING_FEATURES + [TARGET_COLUMN]
    missing_cols = set(required_cols) - set(df.columns)
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")

    # Check for unexpected missing values in screening features
    screening_missing = df[SCREENING_FEATURES].isna().sum()
    if screening_missing.sum() > 0:
        print(f"Warning: Missing values detected in screening features:\n{screening_missing[screening_missing > 0]}")

    # Verify value ranges
    _verify_value_ranges(df)

def _verify_value_ranges(df: pd.DataFrame) -> None:
    """Verify clinical value ranges are reasonable"""
    ranges = {
        'age': (29, 77),
        'sex': (0, 1),
        'cp': (1, 4),
        'trestbps': (94, 200),
        'chol': (126, 564),
        'fbs': (0, 1),
        'restecg': (0, 2)
    }

    for col, (min_val, max_val) in ranges.items():
        if col in df.columns:
            col_min = df[col].min()
            col_max = df[col].max()
            if pd.notna(col_min) and pd.notna(col_max):
                if col_min < min_val or col_max > max_val:
                    print(f"Warning: {col} values outside expected range [{min_val}, {max_val}]: ({col_min}, {col_max})")

def get_screening_dataset(df: pd.DataFrame, include_target: bool = True) -> pd.DataFrame:
    """
    Extract screening features from full dataset

    Args:
        df: Full dataframe
        include_target: Whether to include target column

    Returns:
        DataFrame with screening features only
    """
    cols = SCREENING_FEATURES.copy()
    if include_target:
        cols.append('target_binary')

    return df[cols].copy()

def split_cleveland_train_test(
    df: pd.DataFrame,
    test_size: float = 0.3,
    random_state: int = 42
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    """
    Split Cleveland dataset with stratification

    Args:
        df: Cleveland dataframe
        test_size: Proportion for test set
        random_state: Random seed

    Returns:
        X_train, X_test, y_train, y_test
    """
    from sklearn.model_selection import train_test_split

    X = get_screening_dataset(df, include_target=False)
    y = df['target_binary']

    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=test_size,
        stratify=y,
        random_state=random_state
    )

    return X_train, X_test, y_train, y_test

if __name__ == "__main__":
    # Test loading
    data_path = Path("C:/Users/konda/Downloads/cardioverse-ai/data/processed.cleveland.data")
    df = load_cleveland_dataset(data_path)
    print(f"Loaded dataset: {df.shape}")
    print(f"Class distribution:\n{df['target_binary'].value_counts()}")
