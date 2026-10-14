"""
CardioVerse AI - FastAPI Backend

Cardiovascular Disease Screening using Logistic Regression.

Research and educational use only.
Not intended for medical diagnosis or clinical decision-making.
"""

import logging
import pickle
from contextlib import asynccontextmanager
from pathlib import Path
from typing import List

import numpy as np
import pandas as pd
import uvicorn

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from pydantic import (
    BaseModel,
    Field,
    ConfigDict,
    field_validator,
)


# ============================================================
# CONFIGURATION
# ============================================================

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger("cardioverse")

PROJECT_ROOT = Path(__file__).resolve().parent.parent

MODEL_ARTIFACT_PATH = (
    PROJECT_ROOT
    / "models"
    / "Logistic_Regression_screening_model.pkl"
)

DATASET_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed.cleveland.data"
)

SCREENING_FEATURES = [
    "age",
    "sex",
    "cp",
    "trestbps",
    "chol",
    "fbs",
    "restecg",
]

MODEL_VERSION = "lr-screening-v1.0"

API_VERSION = "1.0.0"

DISCLAIMER = (
    "This model provides research-oriented statistical estimates "
    "based on historical clinical data. It does not diagnose "
    "coronary artery disease, identify coronary blockages, "
    "or predict 10-year cardiovascular events. "
    "Consult a qualified healthcare professional for medical decisions."
)


# ============================================================
# FEATURE DEFINITIONS
# ============================================================

CODING_SCHEMA = {
    "age": {
        "type": "continuous",
        "min": 29,
        "max": 77,
        "description": "Age in years",
    },
    "sex": {
        "type": "categorical",
        "categories": {
            "0": "Female",
            "1": "Male",
        },
        "description": "Sex",
    },
    "cp": {
        "type": "categorical",
        "categories": {
            "1": "Typical angina",
            "2": "Atypical angina",
            "3": "Non-anginal pain",
            "4": "Asymptomatic",
        },
        "description": "Chest pain type",
    },
    "trestbps": {
        "type": "continuous",
        "min": 94,
        "max": 200,
        "description": "Resting blood pressure",
    },
    "chol": {
        "type": "continuous",
        "min": 126,
        "max": 564,
        "description": "Serum cholesterol",
    },
    "fbs": {
        "type": "categorical",
        "categories": {
            "0": "Fasting blood sugar <= 120 mg/dl",
            "1": "Fasting blood sugar > 120 mg/dl",
        },
        "description": "Fasting blood sugar",
    },
    "restecg": {
        "type": "categorical",
        "categories": {
            "0": "Normal",
            "1": "ST-T abnormality",
            "2": "LV hypertrophy",
        },
        "description": "Resting ECG",
    },
}


FEATURE_DISPLAY_NAMES = {
    "age": "Age",
    "sex": "Sex",
    "cp": "Chest pain type",
    "trestbps": "Resting blood pressure",
    "chol": "Serum cholesterol",
    "fbs": "Fasting blood sugar",
    "restecg": "Resting ECG",
}


# ============================================================
# PYDANTIC REQUEST MODELS
# ============================================================

class PatientFeatures(BaseModel):

    age: float = Field(..., ge=29, le=77)

    sex: int = Field(..., ge=0, le=1)

    cp: int = Field(..., ge=1, le=4)

    trestbps: float = Field(..., ge=94, le=200)

    chol: float = Field(..., ge=126, le=564)

    fbs: int = Field(..., ge=0, le=1)

    restecg: int = Field(..., ge=0, le=2)

    @field_validator("*", mode="before")
    @classmethod
    def check_category_values(cls, value, info):

        field_name = info.field_name

        schema = CODING_SCHEMA.get(field_name)

        if schema and schema["type"] == "categorical":

            allowed = schema["categories"]

            if str(value) not in allowed:
                raise ValueError(
                    f"Invalid {field_name}: {value}. "
                    f"Allowed: {list(allowed.keys())}"
                )

        return value

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "age": 63,
                "sex": 1,
                "cp": 1,
                "trestbps": 145,
                "chol": 233,
                "fbs": 1,
                "restecg": 0,
            }
        }
    )


class ExplanationRequest(BaseModel):
    patient_features: PatientFeatures


# ============================================================
# PYDANTIC RESPONSE MODELS
# ============================================================

class PredictionResponse(BaseModel):

    disease_probability: float = Field(..., ge=0, le=1)
    predicted_class: int = Field(..., ge=0, le=1)
    model_version: str
    risk_category: str
    disclaimer: str


class HealthResponse(BaseModel):

    status: str
    model_loaded: bool
    version: str


class ModelInfoResponse(BaseModel):

    model_type: str
    version: str
    features: List[str]
    feature_descriptions: dict
    class_labels: List[str]
    training_cohort: str
    data_source: str


class ExplanationResponse(BaseModel):

    probability: float
    predicted_class: int
    log_odds: float
    positive_contributors: dict
    negative_contributors: dict
    top_factors: list
    clinical_text: str
    model_version: str
    disclaimer: str


# ============================================================
# GLOBAL MODEL STATE
# ============================================================

model_pipeline = None

model_classifier = None

explainer = None

model_loaded = False

model_error = None


# ============================================================
# MODEL HELPER FUNCTIONS
# ============================================================

def get_pipeline_component(pipeline, component_name):
    """
    Retrieve a component from the project's custom pipeline.
    """

    if not hasattr(pipeline, "steps"):
        raise TypeError(
            "Loaded model does not expose pipeline steps."
        )

    for name, component in pipeline.steps:

        if name == component_name:
            return component

    raise ValueError(
        f"Pipeline component '{component_name}' not found."
    )


def get_positive_class_probability(probabilities, classifier):
    """
    Extract probability for positive class 1.
    """

    classes = np.asarray(
        classifier.classes_
    ).reshape(-1).tolist()

    if 1 not in classes:
        raise ValueError(
            "Classifier does not contain positive class 1."
        )

    positive_index = classes.index(1)

    probabilities = np.asarray(
        probabilities,
        dtype=float,
    )

    if probabilities.ndim != 2:
        raise ValueError(
            "Expected a two-dimensional probability array."
        )

    if probabilities.shape[0] != 1:
        raise ValueError(
            "Expected probabilities for exactly one patient."
        )

    if probabilities.shape[1] != len(classes):
        raise ValueError(
            "Probability columns do not match classifier classes."
        )

    probability = float(
        probabilities[0, positive_index]
    )

    if not np.isfinite(probability):
        raise ValueError(
            "Model returned a non-finite probability."
        )

    if not 0 <= probability <= 1:
        raise ValueError(
            "Model returned a probability outside [0, 1]."
        )

    return probability


def get_risk_category(probability):
    """
    Illustrative model-score categories.

    These thresholds are not clinically validated.
    """

    if probability >= 0.75:
        return "High Risk"

    if probability >= 0.5:
        return "Elevated Risk"

    return "Lower Risk"


def create_patient_dataframe(patient):
    """
    Convert validated patient features into a DataFrame.

    Preserve the seven-feature training order.
    """

    patient_data = patient.model_dump()

    ordered_data = {
        feature: patient_data[feature]
        for feature in SCREENING_FEATURES
    }

    return pd.DataFrame(
        [ordered_data],
        columns=SCREENING_FEATURES,
    )


# ============================================================
# EXPLANATION HELPER FUNCTIONS
# ============================================================

def normalize_contributions(contributions):
    """
    Convert explanation contributions to plain Python floats.

    Reject invalid or non-finite values.
    """

    if not isinstance(contributions, dict):
        raise ValueError(
            "Expected contributions to be a dictionary."
        )

    normalized = {}

    for feature, value in contributions.items():

        contribution = float(value)

        if not np.isfinite(contribution):
            raise ValueError(
                f"Non-finite contribution for {feature}."
            )

        normalized[str(feature)] = contribution

    return normalized


def build_top_factors(
    positive_contributions,
    negative_contributions,
):
    """
    Identify the three largest absolute feature contributions.
    """

    all_contributions = {}

    all_contributions.update(
        positive_contributions
    )

    all_contributions.update(
        negative_contributions
    )

    sorted_factors = sorted(
        all_contributions.items(),
        key=lambda item: abs(item[1]),
        reverse=True,
    )

    top_factors = [
        {
            "feature": name,
            "contribution": round(value, 4),
        }
        for name, value in sorted_factors[:3]
    ]

    return top_factors


def build_clinical_text(top_factors):
    """
    Generate a descriptive, non-diagnostic explanation.

    Contributions describe model behavior, not causation.
    """

    if not top_factors:
        return (
            "Feature contribution information is unavailable. "
            "This model output is for research and educational "
            "purposes only."
        )

    factor_descriptions = []

    for factor in top_factors:

        feature = factor["feature"]

        contribution = factor["contribution"]

        display_name = FEATURE_DISPLAY_NAMES.get(
            feature,
            feature,
        )

        if contribution > 0:
            direction = "increased"

        elif contribution < 0:
            direction = "decreased"

        else:
            direction = "did not change"

        factor_descriptions.append(
            f"{display_name} ({direction} the model score)"
        )

    factors_text = ", ".join(
        factor_descriptions
    )

    return (
        "The strongest feature contributions for this "
        f"prediction were: {factors_text}. "
        "Positive contributions increase the model's "
        "estimated log-odds, while negative contributions "
        "decrease them. These contributions describe "
        "statistical model behavior, not clinical causation. "
        "This explanation is not a medical diagnosis."
    )


# ============================================================
# MODEL LOADING
# ============================================================

def load_model():

    global model_pipeline
    global model_classifier
    global explainer
    global model_loaded
    global model_error

    if model_loaded:
        return

    model_pipeline = None
    model_classifier = None
    explainer = None
    model_loaded = False
    model_error = None

    try:

        if not MODEL_ARTIFACT_PATH.exists():
            raise FileNotFoundError(
                f"Model artifact not found: {MODEL_ARTIFACT_PATH}"
            )

        # Only load trusted pickle artifacts.

        with open(MODEL_ARTIFACT_PATH, "rb") as file:
            loaded_pipeline = pickle.load(file)

        if not hasattr(loaded_pipeline, "predict_proba"):
            raise TypeError(
                "Loaded pipeline does not support predict_proba."
            )

        classifier = get_pipeline_component(
            loaded_pipeline,
            "classifier",
        )

        if not hasattr(classifier, "classes_"):
            raise TypeError(
                "Classifier does not expose trained class labels."
            )

        classes = np.asarray(
            classifier.classes_
        ).reshape(-1).tolist()

        if 1 not in classes:
            raise ValueError(
                "Classifier is missing positive class 1."
            )

        coefficients = np.asarray(
            classifier.coef_,
            dtype=float,
        ).reshape(-1)

        if coefficients.shape != (len(SCREENING_FEATURES),):
            raise ValueError(
                "Classifier coefficient count does not match "
                "the seven screening features."
            )

        model_pipeline = loaded_pipeline
        model_classifier = classifier
        model_loaded = True

        logger.info(
            "Model loaded successfully from %s",
            MODEL_ARTIFACT_PATH,
        )

        logger.info(
            "Classifier coefficient shape: %s",
            coefficients.shape,
        )

        logger.info(
            "Classifier classes: %s",
            classes,
        )

        # ----------------------------------------------------
        # EXPLAINABILITY INITIALIZATION
        # ----------------------------------------------------

        try:

            from ml_pipeline.explainability import (
                LogisticRegressionExplainability
            )

            from ml_pipeline.data_loader import (
                load_cleveland_dataset,
                get_screening_dataset,
            )

            if not DATASET_PATH.exists():
                raise FileNotFoundError(
                    f"Dataset not found: {DATASET_PATH}"
                )

            df = load_cleveland_dataset(
                DATASET_PATH
            )

            X = get_screening_dataset(
                df,
                include_target=False,
            )

            feature_names = list(X.columns)

            if feature_names != SCREENING_FEATURES:
                raise ValueError(
                    "Dataset feature order does not match "
                    "the expected screening features. "
                    f"Dataset: {feature_names}; "
                    f"Expected: {SCREENING_FEATURES}"
                )

            scaler = get_pipeline_component(
                model_pipeline,
                "scaler",
            )

            feature_means = np.asarray(
                scaler.mean_,
                dtype=float,
            ).reshape(-1)

            feature_stds = np.asarray(
                scaler.scale_,
                dtype=float,
            ).reshape(-1)

            coefficients = np.asarray(
                model_classifier.coef_,
                dtype=float,
            ).reshape(-1)

            intercept = float(
                np.asarray(
                    model_classifier.intercept_
                ).item()
            )

            if feature_means.shape != coefficients.shape:
                raise ValueError(
                    "Scaler means and classifier coefficients "
                    "have incompatible dimensions."
                )

            if feature_stds.shape != coefficients.shape:
                raise ValueError(
                    "Scaler standard deviations and classifier "
                    "coefficients have incompatible dimensions."
                )

            if not np.all(np.isfinite(feature_stds)):
                raise ValueError(
                    "Scaler contains non-finite standard deviations."
                )

            if np.any(feature_stds == 0):
                raise ValueError(
                    "Scaler contains zero standard deviations."
                )

            explainer = LogisticRegressionExplainability(
                coefficients=coefficients,
                intercept=intercept,
                feature_names=feature_names,
                feature_means=feature_means,
                feature_stds=feature_stds,
                class_labels=[
                    "No CAD",
                    "CAD",
                ],
            )

            logger.info(
                "Explainability module initialized successfully."
            )

        except Exception:

            logger.exception(
                "Explainability initialization failed. "
                "Prediction functionality remains available."
            )

            explainer = None

    except Exception as error:

        model_error = str(error)

        model_pipeline = None
        model_classifier = None
        explainer = None
        model_loaded = False

        logger.exception(
            "Failed to load ML model."
        )


# ============================================================
# APPLICATION LIFESPAN
# ============================================================

@asynccontextmanager
async def lifespan(app: FastAPI):

    load_model()

    yield


# ============================================================
# FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="CardioVerse AI - Clinical Screening API",
    description=DISCLAIMER,
    version=API_VERSION,
    contact={
        "name": "CardioVerse AI Team"
    },
    lifespan=lifespan,
)


# ============================================================
# CORS CONFIGURATION
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=[
        "GET",
        "POST",
    ],
    allow_headers=[
        "Content-Type",
        "Authorization",
    ],
)


# ============================================================
# HEALTH ENDPOINT
# ============================================================

@app.get(
    "/health",
    response_model=HealthResponse,
)
async def health_check():

    return HealthResponse(
        status=(
            "healthy"
            if model_loaded
            else "degraded"
        ),
        model_loaded=model_loaded,
        version=API_VERSION,
    )


# ============================================================
# PREDICTION ENDPOINT
# ============================================================

@app.post(
    "/api/predict",
    response_model=PredictionResponse,
)
async def predict(patient: PatientFeatures):

    if not model_loaded or model_pipeline is None:
        raise HTTPException(
            status_code=503,
            detail="Model not loaded",
        )

    if model_classifier is None:
        raise HTTPException(
            status_code=503,
            detail="Classifier not initialized",
        )

    try:

        input_df = create_patient_dataframe(
            patient
        )

        probabilities = model_pipeline.predict_proba(
            input_df
        )

        probability = get_positive_class_probability(
            probabilities,
            model_classifier,
        )

        prediction = int(
            probability >= 0.5
        )

        risk_category = get_risk_category(
            probability
        )

        return PredictionResponse(
            disease_probability=round(
                probability,
                4,
            ),
            predicted_class=prediction,
            model_version=MODEL_VERSION,
            risk_category=risk_category,
            disclaimer=DISCLAIMER,
        )

    except Exception:

        logger.exception(
            "Prediction failed."
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Prediction failed. "
                "Check backend logs."
            ),
        )


# ============================================================
# EXPLANATION ENDPOINT
# ============================================================

@app.post(
    "/api/explain",
    response_model=ExplanationResponse,
)
async def explain(request: ExplanationRequest):

    if not model_loaded:
        raise HTTPException(
            status_code=503,
            detail="Model not loaded",
        )

    if explainer is None:
        raise HTTPException(
            status_code=503,
            detail="Explainability module unavailable",
        )

    try:

        features = request.patient_features.model_dump()

        explanation = explainer.explain_patient(
            features
        )

        # ----------------------------------------------------
        # VALIDATE EXPLANATION PROBABILITY
        # ----------------------------------------------------

        probability = float(
            explanation["probability"]
        )

        if not np.isfinite(probability):
            raise ValueError(
                "Explanation returned a non-finite probability."
            )

        if not 0 <= probability <= 1:
            raise ValueError(
                "Explanation returned an invalid probability."
            )

        log_odds = float(
            explanation["log_odds"]
        )

        if not np.isfinite(log_odds):
            raise ValueError(
                "Explanation returned non-finite log-odds."
            )

        # ----------------------------------------------------
        # NORMALIZE CONTRIBUTIONS
        # ----------------------------------------------------

        positive_contributions = normalize_contributions(
            explanation.get(
                "positive_contributions",
                {},
            )
        )

        negative_contributions = normalize_contributions(
            explanation.get(
                "negative_contributions",
                {},
            )
        )

        # ----------------------------------------------------
        # FIX: GENERATE TOP THREE FACTORS
        # ----------------------------------------------------

        top_factors = build_top_factors(
            positive_contributions,
            negative_contributions,
        )

        # ----------------------------------------------------
        # FIX: GENERATE HUMAN-READABLE EXPLANATION
        # ----------------------------------------------------

        clinical_text = build_clinical_text(
            top_factors
        )

        return ExplanationResponse(
            probability=probability,
            predicted_class=int(
                probability >= 0.5
            ),
            log_odds=log_odds,
            positive_contributors=positive_contributions,
            negative_contributors=negative_contributions,
            top_factors=top_factors,
            clinical_text=clinical_text,
            model_version=explanation.get(
                "model_version",
                MODEL_VERSION,
            ),
            disclaimer=DISCLAIMER,
        )

    except Exception:

        logger.exception(
            "Explanation failed."
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Explanation failed. "
                "Check backend logs."
            ),
        )


# ============================================================
# MODEL INFORMATION ENDPOINT
# ============================================================

@app.get(
    "/api/model-info",
    response_model=ModelInfoResponse,
)
async def model_info():

    if not model_loaded or model_pipeline is None:
        raise HTTPException(
            status_code=503,
            detail="Model not loaded",
        )

    descriptions = {}

    for feature in SCREENING_FEATURES:

        schema = CODING_SCHEMA[feature]

        descriptions[feature] = {
            "type": schema["type"],
            "description": schema["description"],
            "categories": schema.get(
                "categories"
            ),
        }

    return ModelInfoResponse(
        model_type="Logistic Regression",
        version=API_VERSION,
        features=SCREENING_FEATURES,
        feature_descriptions=descriptions,
        class_labels=[
            "No CAD",
            "CAD",
        ],
        training_cohort=(
            "Cleveland Heart Disease Dataset "
            "(UCI 1980s)"
        ),
        data_source=(
            "UCI Machine Learning Repository, "
            "Detrano et al. (1989)"
        ),
    )


# ============================================================
# ROOT ENDPOINT
# ============================================================

@app.get("/")
async def root():

    return JSONResponse(
        content={
            "message": (
                "CardioVerse AI Clinical Screening API"
            ),
            "version": API_VERSION,
            "endpoints": [
                "/health",
                "/api/predict",
                "/api/explain",
                "/api/model-info",
            ],
            "disclaimer": DISCLAIMER,
        }
    )


# ============================================================
# EXCEPTION HANDLERS
# ============================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "disclaimer": DISCLAIMER,
        },
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request, exc):

    logger.exception(
        "Unhandled backend exception"
    )

    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "disclaimer": DISCLAIMER,
        },
    )


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("CardioVerse AI - Clinical Screening API")
    print("=" * 60)

    print(f"Project root: {PROJECT_ROOT}")
    print(f"Model artifact: {MODEL_ARTIFACT_PATH}")
    print(f"Dataset: {DATASET_PATH}")

    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
    )