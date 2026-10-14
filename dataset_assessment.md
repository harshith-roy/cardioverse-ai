# Dataset Assessment Report: Heart Disease

## Overview
This assessment covers 4 datasets concerning heart disease diagnosis: Cleveland, Hungarian, Switzerland, and Long Beach VA.

## Source
- Source: UCI Machine Learning Repository (Heart Disease Data Set)
- Date: 1988
- Original Creators: Hungarian Institute of Cardiology (Janosi), University Hospital Zurich/Basel (Steinbrunn/Pfisterer), V.A. Medical Center Long Beach/Cleveland Clinic (Detrano).

## Dataset Summary (Processed Versions)

| Dataset | Records | Features | Missing Values | Class 0 (No Disease) | Class 1-4 (Disease) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| Cleveland | 303 | 13 | 0 | 164 | 139 |
| Hungarian | 294 | 13 | 0 | 188 | 106 |
| Switzerland | 123 | 13 | 0 | 8 | 115 |
| Long Beach VA | 200 | 13 | 0 | 51 | 149 |

## Feature Descriptions (14 Attributes Used)
1. **age**: age in years
2. **sex**: 1 = male; 0 = female
3. **cp**: chest pain type (1: typical angina, 2: atypical angina, 3: non-anginal pain, 4: asymptomatic)
4. **trestbps**: resting blood pressure (mm Hg)
5. **chol**: serum cholestoral (mg/dl)
6. **fbs**: fasting blood sugar > 120 mg/dl (1 = true; 0 = false)
7. **restecg**: resting electrocardiographic results (0: normal, 1: ST-T wave abnormality, 2: probable/definite LV hypertrophy)
8. **thalach**: maximum heart rate achieved
9. **exang**: exercise induced angina (1 = yes; 0 = no)
10. **oldpeak**: ST depression induced by exercise relative to rest
11. **slope**: slope of the peak exercise ST segment (1: upsloping, 2: flat, 3: downsloping)
12. **ca**: number of major vessels (0-3) colored by flourosopy
13. **thal**: 3 = normal; 6 = fixed defect; 7 = reversable defect
14. **num** (target): diagnosis of heart disease (angiographic status). 0: < 50% narrowing, 1-4: > 50% narrowing.

## Quality Concerns
- **Switzerland/VA Datasets**: Highly imbalanced toward presence of disease. Use with caution for training models aimed at general populations.
- **Preprocessing**: The provided "processed" files are already cleaned of missing values.
- **Combined Analysis**: While datasets share the same format, they originate from different populations and methodologies. Evaluation should be performed per-dataset or with domain-adaptation techniques.

## Suitability
- **CAD Classification**: Suitable for binary classification (0 vs 1-4).
- **Risk Estimation**: These datasets provide angiographic outcomes, not long-term event risk. They are NOT suitable for direct cardiovascular risk assessment (e.g., 10-year risk of CV event).

## Recommendation
Use the Cleveland dataset as the primary development dataset due to its balanced nature and extensive use in literature.
