# FEATURE SELECTION STRATEGY

## Two-Candidate Feature Sets

### Feature Set A: Clinical Screening Features
**Purpose**: Initial risk assessment at first clinical presentation
**Available at**: Primary care visit without specialist testing
**Features**:
- age (years)
- sex (0=female, 1=male)
- cp (chest pain type)
- trestbps (resting blood pressure, mmHg)
- chol (serum cholesterol, mg/dl)
- fbs (fasting blood sugar >120 mg/dl)
- restecg (resting ECG result)

**Missing Data**: Minimal (<1%)
**Clinical Validity**: HIGH - All features obtainable at initial screening

### Feature Set B: Extended Diagnostic Assessment
**Purpose**: Secondary assessment after exercise testing and/or cardiac catheterization
**Available at**: Cardiology workup
**Features**: All clinical screening features PLUS:
- thalach (maximum heart rate achieved)
- exang (exercise induced angina)
- oldpeak (ST depression)
- slope (ST segment slope)
- ca (number of major vessels from catheterization)
- thal (thallium scan result)

**Missing Data**: Substantial in non-Cleveland cohorts
**Clinical Validity**: HIGH - Features require diagnostic testing
**Risk**: Data leakage if used for initial screening model

## Recommended Model Architecture

### Model 1: Screening Model (Feature Set A)
- **Target**: CAD classification
- **Cohort**: Cleveland primary, Hungarian/VA validation
- **Missing Data**: Simple imputation
- **Validation**: External geographic validation

### Model 2: Diagnostic Model (Feature Set B)
- **Target**: CAD classification  
- **Cohort**: Cleveland only (complete data)
- **Missing Data**: Multiple imputation
- **Validation**: Internal cross-validation only
- **Use Case**: Educational demonstration of diagnostic refinement

## Training/Evaluation Protocol

### Step 1: Data Preparation
1. Load Cleveland processed dataset
2. Identify missing values (-9 encoding)
3. Separate screening vs diagnostic features
4. Create two feature matrices

### Step 2: Preprocessing Pipeline
1. Stratified split: 70% train, 30% test
2. Fit preprocessing only on training data:
   - Missing value imputation (median)
   - Feature scaling (StandardScaler)
   - No feature selection on test data

### Step 3: Model Training
Train three algorithms:
1. Logistic Regression (baseline, interpretable)
2. Random Forest (non-linear)
3. XGBoost (state-of-art)

### Step 4: Model Evaluation
Metrics:
- ROC-AUC (primary)
- PR-AUC (given class imbalance)
- Sensitivity/Specificity at optimal threshold
- Calibration (Brier score, reliability diagram)
- Confidence intervals via bootstrapping

### Step 5: External Validation
Apply trained screening model to:
- Hungarian dataset (screening features only)
- VA dataset (screening features only)
Report performance degradation and calibration drift

## Data Leakage Prevention Checklist

- [ ] No ca/thal in screening model
- [ ] Preprocessing fitted only on training data
- [ ] Stratified splits preserve class distribution
- [ ] Cross-validation prevents overfitting
- [ ] External validation on separate populations
- [ ] Report calibration metrics (not just discrimination)

## Clinical Deployment Considerations

**Model Output**: Probability score with confidence interval
**Model Limitations**: 
- Trained on older datasets (1980s)
- May not reflect modern populations
- Requires clinical judgment for interpretation
**Regulatory Status**: Research/educational use only
**Disclaimer**: Not a diagnostic tool

## Next Steps

1. Implement ML pipeline with Feature Set A
2. Train baseline models on Cleveland
3. Validate externally on Hungarian/VA
4. Generate model documentation and SHAP explanations
5. Proceed to backend API development
