# CardioVerse AI - ML Pipeline

## Overview

Machine learning pipeline for clinical screening of coronary artery disease using the UCI Heart Disease dataset.

## Architecture

```
src/backend/ml_pipeline/
├── __init__.py
├── data_loader.py      # Dataset loading and validation
├── preprocessing.py    # Feature preprocessing
├── models.py           # Model implementations
├── evaluation.py       # Model evaluation metrics
├── explainability.py   # SHAP and feature analysis
├── external_validation.py # External cohort validation
├── train.py            # Main training script
└── tests/              # Input validation tests
```

## Features

### Clinical Screening Model
- **Features**: age, sex, cp, trestbps, chol, fbs, restecg
- **Target**: Binary heart disease classification
- **Dataset**: Cleveland (primary), Hungarian, VA (external validation)

### Key Characteristics
- Reproducible preprocessing pipeline
- Stratified cross-validation
- External validation on independent cohorts
- Model explainability (SHAP)
- Input validation and testing

## Quick Start

### Training Model
```python
from ml_pipeline.train import train_with_cross_validation

results = train_with_cross_validation()
```

### Loading Dataset
```python
from ml_pipeline.data_loader import load_cleveland_dataset
from pathlib import Path

df = load_cleveland_dataset(Path('data/processed.cleveland.data'))
```

### Making Predictions
```python
from ml_pipeline.models import create_model_pipeline
import joblib

# Load trained model
pipeline = joblib.load('models/logistic_regression_screening_model.joblib')

# Make prediction
X_new = pd.DataFrame([patient_data])
probability = pipeline.predict_proba(X_new)[0, 1]
```

## Model Limitations

⚠️ **Research/Educational Use Only**
- Not for clinical diagnosis
- Historical dataset (1980s)
- Requires clinical judgment
- Correlation not causation

## Documentation

- `../dataset_verification_report.md` - Dataset quality assessment
- `../feature_selection_strategy.md` - Feature selection rationale
- `../model_card.md` - Model documentation
- `archive/ML_PIPELINE_SUMMARY.md` - Complete summary

## Dependencies

- pandas
- numpy
- scikit-learn
- matplotlib
- joblib

## Citation

If using this pipeline, please cite:
- UCI Heart Disease Dataset
- Detrano et al. (1989). American Journal of Cardiology
