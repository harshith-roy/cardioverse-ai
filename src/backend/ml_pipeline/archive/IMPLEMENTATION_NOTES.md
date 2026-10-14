# Implementation Notes

## Technical Decisions

### Why Pure Python Implementation?

The machine learning pipeline was implemented using pure Python data structures to avoid dependency issues in the containerized environment. While scikit-learn would be preferable in production, the current implementation demonstrates the complete pipeline architecture.

### Feature Selection Rationale

**Clinical Screening Model**: 7 features selected based on:
1. **Availability**: All obtainable during primary care visit
2. **Clinical Validity**: Standard screening measurements
3. **Data Quality**: Minimal missing values in Cleveland dataset
4. **Leakage Prevention**: Excludes diagnostic test results requiring specialist procedures

**Excluded Features**:
- `ca` (number of vessels) - Requires cardiac catheterization
- `thal` (thallium scan) - Requires nuclear stress testing
- `thalach`, `exang`, `oldpeak`, `slope` - Require exercise testing

### Missing Data Strategy

**Cleveland Dataset**: Minimal missing data (4 ca, 2 thal)
- Strategy: Median imputation
- Rationale: Small amount, unlikely to bias results

**External Cohorts**: Extensive missing data in diagnostic features
- Strategy: Use screening features only for validation
- Rationale: Maintains consistency with training data

### Model Selection

**Logistic Regression**:
- Pros: Interpretable, calibrated probabilities, baseline
- Cons: Assumes linear relationships
- Best for: Clinical explanation and regulatory acceptance

**Random Forest**:
- Pros: Captures non-linearities, handles interactions
- Cons: Less interpretable, potential overfitting
- Best for: Performance maximization

**Baseline**:
- Dummy classifier for performance floor
- Essential for demonstrating model value

## Known Issues

### Dependency Limitations
- scikit-learn not available in current environment
- Implemented simplified versions for demonstration
- Production deployment requires proper ML libraries

### Data Quality Concerns
1. **Historical Data**: 1980s population may differ from modern
2. **Selection Bias**: Cardiac catheterization cohort
3. **Limited Features**: No smoking, family history, BMI
4. **Single Institution**: Cleveland only for training

## Validation Protocol

### Internal Validation
1. 5-fold stratified cross-validation
2. Held-out test set (30%)
3. Preprocessing pipeline fitted only on training data

### External Validation
1. Hungarian cohort: 294 patients
2. VA cohort: 200 patients
3. Feature compatibility verified
4. Performance degradation assessment

## Clinical Considerations

### Model Interpretability
- Feature importance rankings must be presented carefully
- Correlations ≠ causation
- Model outputs should inform, not replace clinical judgment

### Fairness
- Performance may vary across demographic groups
- Age and sex are predictive features
- Monitor for bias in external validation

### Calibration
- Probability estimates need recalibration for new populations
- Present confidence intervals
- Avoid overconfident predictions

## Next Steps for Production

1. **Dependencies**: Install scikit-learn, xgboost, shap
2. **Testing**: Add unit tests for all modules
3. **Documentation**: Generate API documentation
4. **Versioning**: Implement model version control
5. **Monitoring**: Add performance monitoring
6. **Security**: Implement input validation and sanitization

## Code Quality

### Testing
- Input validation tests implemented
- Prediction consistency tests
- Range validation for clinical features

### Documentation
- Module docstrings
- Function documentation
- Architecture diagrams
- Model cards

## References

- UCI Heart Disease Database
- Detrano et al. (1989)
- Google Model Cards for Model Reporting
- FDA Software as Medical Device guidelines
