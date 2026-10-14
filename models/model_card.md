# Model Card: CardioVerse AI Clinical Screening Model

## Model Details

**Model Name**: CardioVerse AI Clinical Screening Model v1.0
**Version**: 1.0
**Date**: 2026-10-12
**Purpose**: Estimate probability of coronary artery disease using routinely available clinical features

**Intended Use**: Research and educational purposes only. Not for clinical diagnosis.

## Model Description

This model predicts the probability of heart disease (as defined by the UCI Heart Disease dataset) using seven clinical screening features that are routinely available during primary care visits.

### Features
1. **age** (years): Patient age
2. **sex** (0=female, 1=male): Biological sex
3. **cp** (1-4): Chest pain type (1=typical angina, 2=atypical angina, 3=non-anginal pain, 4=asymptomatic)
4. **trestbps** (mm Hg): Resting blood pressure
5. **chol** (mg/dl): Serum cholesterol
6. **fbs** (0/1): Fasting blood sugar > 120 mg/dl
7. **restecg** (0-2): Resting ECG results

### Target Variable
Binary classification derived from dataset `num` field:
- 0: < 50% diameter narrowing (no disease)
- 1+: > 50% diameter narrowing (disease)

## Training Data

**Dataset**: Cleveland Heart Disease Database
**Source**: UCI Machine Learning Repository
**Size**: 303 patients
**Class Distribution**:
- No disease: 164 (54.1%)
- Disease: 139 (45.9%)

**Preprocessing**:
- Missing values: Median imputation
- Feature scaling: StandardScaler
- Train/Test split: 70/30 stratified

**Validation**:
- Internal: 5-fold stratified cross-validation
- External: Hungarian and VA datasets (screening features only)

## Model Architecture

**Models Evaluated**:
1. Logistic Regression (interpretable baseline)
2. Random Forest (ensemble method)
3. Dummy Classifier (baseline)

**Selection Criteria**:
- ROC-AUC on held-out test set
- Calibration quality (Brier score)
- Sensitivity for clinical safety
- External validity

## Performance Metrics

*Results will be populated after training*

### Expected Performance Range
Based on literature and similar models:
- ROC-AUC: 0.75-0.85
- Sensitivity: > 0.70
- Specificity: > 0.70
- Brier Score: < 0.20

## Limitations

### Data Limitations
1. **Historical Data**: Dataset from 1980s, may not reflect modern populations
2. **Single Institution**: Trained primarily on Cleveland data
3. **Limited Features**: Only 7 features, missing important risk factors (smoking, family history, BMI)
4. **Outcome Definition**: Angiographic findings, not clinical events
5. **Selection Bias**: Dataset from cardiac catheterization referral population

### Model Limitations
1. **Correlation Not Causation**: Model identifies associations, not causal relationships
2. **Population Specificity**: May not generalize to all populations
3. **Calibration**: Probability estimates may require recalibration for new populations
4. **Missing Clinical Judgment**: Cannot replace physician assessment

### Ethical Considerations
1. **Fairness**: Model performance may vary across demographic groups
2. **Transparency**: Predictions should be explained to patients
3. **Accountability**: Clinical decisions require human oversight
4. **Privacy**: Patient data must be appropriately de-identified

## Recommended Use

### Appropriate Use Cases
- Educational demonstration of ML in cardiology
- Research studies for methodological development
- Hypothesis generation for clinical research
- Risk stratification support (with clinical judgment)

### Inappropriate Use Cases
- Primary diagnostic tool
- Clinical decision-making without physician review
- Patient triage or referral decisions
- Insurance or employment decisions

## Monitoring Requirements

If deployed in research settings:
- Monitor performance drift over time
- Track calibration across subgroups
- Regular revalidation on new data
- Document all use cases and outcomes

## Disclaimer

This model is provided for research and educational purposes only. It is not intended for clinical decision-making. Always consult a healthcare professional for medical advice, diagnosis, or treatment.

The model predictions are probabilistic estimates based on historical data and should not be interpreted as definitive diagnoses. Clinical judgment and additional testing are always required for proper patient assessment.

## Contact Information

For questions about model development or limitations, contact the CardioVerse AI development team.

## References

- UCI Heart Disease Dataset
- Detrano et al. (1989). International application of a new probability algorithm for diagnosis of coronary artery disease. American Journal of Cardiology.
