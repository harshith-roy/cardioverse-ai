"""
CardioVerse AI - FastAPI Backend Application
Serves cardiovascular disease risk predictions from the trained logistic regression model.
"""
import os
import pickle
import sys
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, ConfigDict

# ============================================================
# PROJECT ROOT & MODEL PATH
# ============================================================
PROJECT_ROOT = Path(__file__).resolve().parent
BACKEND_DIR = PROJECT_ROOT / "src" / "backend"
# Pickled sklearn objects can reference ml_pipeline classes during deserialization.
# This path MUST be configured before pickle.load(), not afterwards.
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))
MODEL_ARTIFACT_PATH = PROJECT_ROOT / "models" / "Logistic_Regression_screening_model.pkl"

# ============================================================
# CLINICAL FEATURE DEFINITIONS (verified from dataset)
# ============================================================
SCREENING_FEATURES = ["age", "sex", "cp", "trestbps", "chol", "fbs", "restecg"]

CODING_SCHEMA = {
    "age": {"type": "continuous", "min": 29, "max": 77,
            "description": "Age in years"},
    "sex": {"type": "categorical",
            "categories": {"0": "Female", "1": "Male"},
            "description": "Sex (0=female, 1=male)"},
    "cp": {"type": "categorical",
           "categories": {"1": "Typical angina", "2": "Atypical angina",
                          "3": "Non-anginal pain", "4": "Asymptomatic"},
           "description": "Chest pain type"},
    "trestbps": {"type": "continuous", "min": 94, "max": 200,
                 "description": "Resting blood pressure (mm Hg)"},
    "chol": {"type": "continuous", "min": 126, "max": 564,
             "description": "Serum cholesterol (mg/dl)"},
    "fbs": {"type": "categorical",
            "categories": {"0": "Fasting BS <= 120 mg/dl",
                           "1": "Fasting BS > 120 mg/dl"},
            "description": "Fasting blood sugar > 120 mg/dl"},
    "restecg": {"type": "categorical",
               "categories": {"0": "Normal", "1": "ST-T abnormality",
                              "2": "LV hypertrophy by Estes' criteria"},
               "description": "Resting electrocardiographic results"}
}

# ============================================================
# PYDANTIC MODELS for API input/output validation
# ============================================================

class PatientFeatures(BaseModel):
    """Input schema for seven clinical features."""
    age: float = Field(..., ge=29, le=77,
                       description="Age in years (29-77)")
    sex: int = Field(..., ge=0, le=1,
                     description="Sex (0=female, 1=male)")
    cp: int = Field(..., ge=1, le=4,
                    description="Chest pain type (1-4)")
    trestbps: float = Field(..., ge=94, le=200,
                            description="Resting blood pressure (mm Hg)")
    chol: float = Field(..., ge=126, le=564,
                        description="Serum cholesterol (mg/dl)")
    fbs: int = Field(..., ge=0, le=1,
                     description="Fasting BS > 120 mg/dl (0/1)")
    restecg: int = Field(..., ge=0, le=2,
                         description="Resting ECG results (0-2)")

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "age": 63.0, "sex": 1, "cp": 1,
            "trestbps": 145.0, "chol": 233.0,
            "fbs": 1, "restecg": 0
        }
    })


class PredictionResponse(BaseModel):
    """Response schema for POST /api/predict."""
    disease_probability: float = Field(..., ge=0.0, le=1.0,
                                       description="Predicted probability [0,1]")
    predicted_class: int = Field(..., ge=0, le=1,
                                 description="0=No disease, 1=Disease")
    model_version: str = "lr-screening-v1.0"
    risk_category: str
    disclaimer: str


class HealthResponse(BaseModel):
    """Response schema for GET /health."""
    status: str
    model_loaded: bool
    version: str


class ModelInfoResponse(BaseModel):
    """Response schema for GET /api/model-info."""
    model_type: str
    version: str
    features: list
    feature_descriptions: dict
    class_labels: list
    training_cohort: str
    data_source: str


class ExplanationRequest(BaseModel):
    """Request schema for POST /api/explain."""
    patient_features: PatientFeatures

    model_config = ConfigDict(json_schema_extra={
        "example": {"patient_features": {
            "age": 63.0, "sex": 1, "cp": 1,
            "trestbps": 145.0, "chol": 233.0,
            "fbs": 1, "restecg": 0
        }}
    })


class ExplanationResponse(BaseModel):
    """Response schema for POST /api/explain."""
    probability: float
    predicted_class: int
    log_odds: float
    positive_contributions: dict
    negative_contributions: dict
    top_factors: list
    clinical_text: str
    model_version: str
    disclaimer: str


# ============================================================
# FASTAPI APP INITIALIZATION
# ============================================================

app = FastAPI(
    title="CardioVerse AI - Clinical Screening API",
    description="""
    AI-powered cardiovascular risk prediction using logistic regression.

    CRITICAL DISCLAIMERS:
    - This model estimates probability of coronary artery disease based on
      clinical features from historical data (UCI 1980s dataset).
    - It does NOT diagnose coronary artery disease or identify specific
      coronary artery blockages.
    - The output is a probability estimate, NOT a confirmed diagnosis.
    - Does NOT convert classification probability into 10-year cardiovascular
      event risk.
    - Always consult a healthcare professional for medical advice,
      diagnosis, or treatment.
    - This model is for research and educational purposes only.
    - Does not claim clinical validation or confirmed diagnosis.
    """,
    version="1.0.0",
    contact={"name": "CardioVerse AI Team"},
    docs_url="/docs",
    redoc_url="/redoc"
)

# ============================================================
# CORS MIDDLEWARE (configured for production & local dev)
# ============================================================
allowed_origins_env = os.environ.get("ALLOWED_ORIGINS", "")
allowed_origins = [
    "http://localhost",
    "http://127.0.0.1",
    "http://localhost:8080",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
]
if allowed_origins_env and allowed_origins_env != "*":
    for origin in allowed_origins_env.split(","):
        cleaned = origin.strip()
        if cleaned and cleaned not in allowed_origins:
            allowed_origins.append(cleaned)

if allowed_origins_env == "*":
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["*"],
    )
else:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_origin_regex=r"https://.*\.vercel\.app",
        allow_credentials=True,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["Content-Type", "Authorization"],
    )

# ============================================================
# GLOBAL STATE - Model & Explainability
# ============================================================
model_pipeline = None
explainer = None
model_loaded = False

# Track loaded model parameters for compatibility checks
loaded_coefficients = None
loaded_intercept = None
loaded_feature_names = None
loaded_feature_means = None
loaded_feature_stds = None


def load_model_artifact():
    """Load the trained model pipeline and initialize explainability module."""
    global model_pipeline, explainer, model_loaded
    global loaded_coefficients, loaded_intercept
    global loaded_feature_names, loaded_feature_means, loaded_feature_stds

    if model_loaded:
        return

    if not MODEL_ARTIFACT_PATH.exists():
        raise FileNotFoundError(
            f"Model artifact NOT found at: {MODEL_ARTIFACT_PATH}"
        )

    try:
        import pickle
        with open(MODEL_ARTIFACT_PATH, 'rb') as f:
            model_pipeline = pickle.load(f)

        # Verify scikit-learn compatibility
        import sklearn
        min_version = "1.0.0"
        installed_version = sklearn.__version__
        print(f"scikit-learn version: {installed_version} (minimum required: {min_version})")

        # Extract pipeline components
        imputer = model_pipeline.steps[0][1]
        scaler = model_pipeline.steps[1][1]
        classifier = model_pipeline.steps[2][1]

        # Verify it's the expected model type
        if not hasattr(classifier, 'coef_'):
            raise TypeError("Classifier does not have 'coef_' attribute - not a logistic regression")

        if not hasattr(classifier, 'intercept_'):
            raise TypeError("Classifier does not have 'intercept_' attribute")

        # Feature names - use the verified SCREENING_FEATURES order
        feature_names = SCREENING_FEATURES.copy()

        # Extract scaler parameters using feature NAMES (pandas Series indexed by feature name)
        # The scaler was fitted on DataFrame with SCREENING_FEATURES columns
        def ordered_stats(values, label):
            if hasattr(values, "loc"):
                return np.asarray(values.loc[feature_names], dtype=float)
            array = np.asarray(values, dtype=float).reshape(-1)
            if array.size != len(feature_names):
                raise ValueError(f"Unexpected {label} length: {array.size}")
            return array

        feature_means = ordered_stats(scaler.mean_, "scaler means")
        feature_stds = ordered_stats(scaler.scale_, "scaler scales")

        # Extract model parameters
        loaded_coefficients = np.asarray(classifier.coef_, dtype=float).reshape(-1)
        if loaded_coefficients.size != len(feature_names):
            raise ValueError("Unexpected number of logistic regression coefficients")
        loaded_intercept = float(np.asarray(classifier.intercept_).reshape(-1)[0])
        loaded_feature_names = feature_names
        loaded_feature_means = feature_means
        loaded_feature_stds = feature_stds

        # Initialize explainability module
        try:
            from ml_pipeline.explainability import LogisticRegressionExplainability
            explainer = LogisticRegressionExplainability(
                coefficients=loaded_coefficients,
                intercept=loaded_intercept,
                feature_names=loaded_feature_names,
                feature_means=loaded_feature_means,
                feature_stds=loaded_feature_stds,
                class_labels=["No CAD", "CAD"]
            )
        except Exception as e:
            print(f"Explainability module not available: {e}")
            explainer = None

        model_loaded = True
        print(f"Model artifact loaded successfully from: {MODEL_ARTIFACT_PATH}")
        print(f"  Features: {feature_names}")
        print(f"  Coefficients: {loaded_coefficients}")
        print(f"  Intercept: {loaded_intercept:.4f}")
        print(f"  Explainer initialized with {len(feature_names)} features")

    except Exception as e:
        print(f"Failed to load model artifact: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        model_pipeline = None
        explainer = None
        model_loaded = False


# Load model at startup
@app.on_event("startup")
def startup_event():
    load_model_artifact()


# ============================================================
# API ENDPOINTS
# ============================================================

@app.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check endpoint",
    description="Verify API is running and model is loaded"
)
async def health_check():
    """Verify API status and model availability."""
    if model_loaded and model_pipeline is not None:
        return HealthResponse(
            status="healthy",
            model_loaded=True,
            version="1.0.0"
        )
    else:
        return HealthResponse(
            status="degraded",
            model_loaded=False,
            version="1.0.0"
        )


@app.post(
    "/api/predict",
    response_model=PredictionResponse,
    summary="Predict cardiovascular disease risk",
    description="Accept seven clinical features and return disease probability"
)
async def predict(patient: PatientFeatures):
    """
    Predict heart disease risk from seven routinely available clinical features.

    Accepts: age, sex, cp, trestbps, chol, fbs, restecg
    Validates input values against verified schema.
    Applies the saved preprocessing pipeline (fitted only on training data).
    Loads the trained logistic regression model.
    Returns the actual model prediction and estimated disease probability.
    Includes model identification and research-use disclaimer.
    """
    if not model_loaded or model_pipeline is None:
        raise HTTPException(
            status_code=503,
            detail="Model not loaded. Check server startup logs."
        )

    try:
        # 1. Extract features in correct ordering
        features_dict = patient.model_dump()
        feature_order = SCREENING_FEATURES  # ["age", "sex", "cp", "trestbps", "chol", "fbs", "restecg"]

        # The saved Pipeline performs its own imputation and scaling.
        # Never manually scale inputs before calling Pipeline.predict_proba.
        model_input = pd.DataFrame([features_dict], columns=SCREENING_FEATURES)
        probability = float(model_pipeline.predict_proba(model_input)[0, 1])
        predicted_class = int(probability >= 0.5)

        # Determine risk category
        if probability >= 0.75:
            risk_category = "High Risk"
        elif probability >= 0.5:
            risk_category = "Elevated Risk"
        else:
            risk_category = "Lower Risk"

        # Model disclaimer (RESEARCH USE ONLY)
        disclaimer = (
            "DISCLAIMER: This model provides a statistical probability estimate "
            "based on clinical features from historical data (UCI 1980s dataset). "
            "It does NOT diagnose coronary artery disease, identify specific "
            "coronary artery blockages, or predict 10-year cardiovascular event risk. "
            "The output is a probability estimate derived from logistic regression "
            "trained on historical clinical data, not a confirmed diagnosis. "
            "Always consult a healthcare professional for medical advice, diagnosis, "
            "or treatment. This tool is for research and educational purposes only."
        )

        return PredictionResponse(
            disease_probability=round(probability, 4),
            predicted_class=predicted_class,
            model_version="lr-screening-v1.0",
            risk_category=risk_category,
            disclaimer=disclaimer
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Prediction failed; inspect server logs."
        )


@app.post(
    "/api/explain",
    response_model=ExplanationResponse,
    summary="Get model explanation for a patient",
    description="Provide feature contributions and clinical interpretation"
)
async def explain(request: ExplanationRequest):
    """
    Provide model explanation using logistic regression feature contributions
    in log-odds space.

    Returns the overall predicted probability, positive/negative contributing
    features, top influential factors, and a clinical explanation text.
    Uses the exact preprocessing pipeline and feature ordering from training.
    """
    if not model_loaded or explainer is None or model_pipeline is None:
        raise HTTPException(
            status_code=503,
            detail="Model not loaded or explainability module unavailable"
        )

    try:
        # Extract and order features
        features_dict = request.patient_features.model_dump()
        feature_order = SCREENING_FEATURES

        # Get explanation from the explainability module
        explanation = explainer.explain_patient(features_dict)

        # Get actual probability from the saved pipeline
        model_input = pd.DataFrame([features_dict], columns=SCREENING_FEATURES)
        actual_probability = float(model_pipeline.predict_proba(model_input)[0, 1])

        # Verify explanation matches actual pipeline prediction
        if abs(float(explanation["probability"]) - actual_probability) > 1e-5:
            raise RuntimeError("Explanation probability disagrees with saved model pipeline")

        # Build explanation response
        disclaimer = (
            "DISCLAIMER: This explanation provides feature contributions in "
            "log-odds space based on a logistic regression model trained on "
            "historical clinical data (UCI 1980s dataset). It does NOT diagnose "
            "coronary artery disease, identify specific blockages, or establish "
            "clinical causation. The output represents statistical associations, "
            "not medical causation or diagnosis. Always consult a healthcare "
            "professional for medical advice."
        )

        # Map top 3 factors for response - use correct keys from explanation
        # The explainability module returns "sorted_features" and contributions in "positive_contributions"/"negative_contributions"
        sorted_features = explanation.get("sorted_features", [])
        pos_contribs = explanation.get("positive_contributions", {})
        neg_contribs = explanation.get("negative_contributions", {})

        top_factors = []
        for name in sorted_features[:3]:
            if name in pos_contribs:
                contrib = pos_contribs[name]
                direction = "increases"
            else:
                contrib = neg_contribs.get(name, 0.0)
                direction = "decreases"
            top_factors.append({
                "feature": name,
                "contribution": round(contrib, 4),
                "direction": direction + " risk"
            })

        return ExplanationResponse(
            probability=actual_probability,
            predicted_class=int(actual_probability >= 0.5),
            log_odds=round(explanation.get("log_odds", 0.0), 4),
            positive_contributions=explanation.get("positive_contributions", {}),
            negative_contributions=explanation.get("negative_contributions", {}),
            top_factors=top_factors,
            clinical_text=explanation.get("summary", ""),
            model_version="lr-screening-v1.0",
            disclaimer="DISCLAIMER: This explanation provides feature contributions in log-odds space based on a logistic regression model trained on historical clinical data (UCI 1980s dataset). It does NOT diagnose coronary artery disease, identify specific blockages, or establish clinical causation. The output represents statistical associations, not medical causation or diagnosis. Always consult a healthcare professional for medical advice."
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Explanation failed; inspect server logs."
        )


@app.get(
    "/api/model-info",
    response_model=ModelInfoResponse,
    summary="Get model information and metadata",
    description="Return model details, feature definitions, and training context"
)
async def model_info():
    """Provide comprehensive model metadata and feature definitions."""
    if not model_loaded or model_pipeline is None:
        raise HTTPException(
            status_code=503,
            detail="Model not loaded. Startup may have failed."
        )

    # Build feature descriptions from verified coding schema
    feature_descriptions = {}
    for feat in SCREENING_FEATURES:
        if feat in CODING_SCHEMA:
            schema = CODING_SCHEMA[feat]
            feature_descriptions[feat] = {
                "type": schema["type"],
                "description": schema["description"],
                "categories": schema.get("categories", None)
            }

    return ModelInfoResponse(
        model_type="Logistic Regression",
        version="lr-screening-v1.0",
        features=SCREENING_FEATURES,
        feature_descriptions=feature_descriptions,
        class_labels=["No CAD", "CAD"],
        training_cohort="Cleveland Heart Disease Dataset (UCI 1980s)",
        data_source="UCI Machine Learning Repository; Detrano et al., "
                     "American Journal of Cardiology, 1989"
    )


@app.get("/")
async def root():
    """Root endpoint with API overview and disclaimers."""
    return JSONResponse(content={
        "message": ("CardioVerse AI - Clinical Screening API v1.0.0"),
        "version": "1.0.0",
        "status": "operational" if model_loaded else "initializing",
        "endpoints": [
            "/health",
            "/api/predict",
            "/api/explain",
            "/api/model-info"
        ],
        "model_loaded": model_loaded,
        "features": SCREENING_FEATURES,
        "disclaimer": ("This API provides research-oriented cardiovascular risk "
                       "predictions based on logistic regression modeling of historical "
                       "clinical data. NOT for clinical diagnosis. Does not claim "
                       "clinical validation or confirmed diagnosis. Does not convert "
                       "probability to 10-year cardiovascular event risk. "
                       "Always consult a healthcare professional for medical advice."),
        "endpoints_detail": {
            "/health": "Verify API status and model availability",
            "/api/predict": ("Accept seven clinical features and return disease "
                             "probability with risk category and disclaimer"),
            "/api/explain": ("Provide feature contributions in log-odds space "
                             "and clinical interpretation text"),
            "/api/model-info": ("Return model metadata, feature definitions, "
                                "and training context")
        }
    })


# ============================================================
# EXCEPTION HANDLERS
# ============================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions with appropriate disclaimers."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "disclaimer": ("This API provides research-oriented cardiovascular "
                           "risk predictions. NOT for clinical decision-making. "
                           "Does not diagnose disease or identify blockages.")
        }
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request, exc):
    """Handle unexpected exceptions gracefully."""
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "details": "Check server logs for details",
            "disclaimer": ("This API provides research-oriented cardiovascular "
                           "risk predictions. NOT for clinical decision-making.")
        }
    )


# ============================================================
# MAIN ENTRY POINT
# ============================================================

if __name__ == "__main__":
    import uvicorn
    import sklearn
    print("=" * 70)
    print("CardioVerse AI - Clinical Screening API")
    print("=" * 70)
    print(f"Model artifact: {MODEL_ARTIFACT_PATH}")
    print(f"Features: {SCREENING_FEATURES}")
    print(f"scikit-learn version: {sklearn.__version__}")
    print("=" * 70)
    port = int(os.environ.get("PORT", 8000))
    host = os.environ.get("HOST", "0.0.0.0")
    print("Starting Uvicorn server...")
    print(f"Access API at: http://{host}:{port}")
    print(f"API docs at: http://{host}:{port}/docs")
    print("=" * 70)
    uvicorn.run(app, host=host, port=port)