from __future__ import annotations

import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
WORKSPACE_ROOT = PROJECT_ROOT.parent
DEFAULT_DATASET_PATH = Path(
    os.getenv("CREDIT_RISK_DATASET", str(WORKSPACE_ROOT / "german_credit_data.csv"))
)

MODELS_DIR = PROJECT_ROOT / "models"
ASSETS_DIR = PROJECT_ROOT / "assets"
DATA_DIR = ASSETS_DIR / "data"
METRICS_DIR = ASSETS_DIR / "metrics"
EXPLANATIONS_DIR = ASSETS_DIR / "explanations"
REPORTS_DIR = ASSETS_DIR / "reports"
ANIMATIONS_DIR = ASSETS_DIR / "animations"

RAW_TO_STANDARD = {
    "Age": "age",
    "Sex": "sex",
    "Job": "job",
    "Housing": "housing",
    "Saving accounts": "saving_accounts",
    "Checking account": "checking_account",
    "Credit amount": "credit_amount",
    "Duration": "duration",
    "Purpose": "purpose",
}

STANDARD_TO_DISPLAY = {
    "age": "Age",
    "sex": "Sex",
    "job": "Job",
    "housing": "Housing",
    "saving_accounts": "Saving accounts",
    "checking_account": "Checking account",
    "credit_amount": "Credit amount (Rs)",
    "duration": "Duration",
    "purpose": "Purpose",
    "risk": "Risk",
    "risk_label": "Risk label",
}

BASE_FEATURES = [
    "age",
    "sex",
    "job",
    "housing",
    "saving_accounts",
    "checking_account",
    "credit_amount",
    "duration",
    "purpose",
]
NUMERIC_COLUMNS = ["age", "credit_amount", "duration"]
CATEGORICAL_COLUMNS = [
    "sex",
    "job",
    "housing",
    "saving_accounts",
    "checking_account",
    "purpose",
]

JOB_LABELS = {
    0: "unskilled and non-resident",
    1: "unskilled and resident",
    2: "skilled",
    3: "highly skilled",
}
JOB_OPTIONS = list(JOB_LABELS.values()) + ["Unknown"]

DM_PER_EUR = 1.95583
EUR_TO_INR_REFERENCE = 108.7795
DM_TO_INR_RATE = EUR_TO_INR_REFERENCE / DM_PER_EUR

RISK_COLORS = {
    "LOW": "#21c48f",
    "MEDIUM": "#ff9f43",
    "HIGH": "#ff5a6f",
}

RISK_EXPLANATIONS = {
    "LOW": "This profile looks comparatively resilient under the synthetic underwriting policy.",
    "MEDIUM": "This profile sits in a watch zone and would benefit from an analyst review.",
    "HIGH": "This profile concentrates multiple stress signals and should be treated cautiously.",
}

ACCOUNT_ORDER = ["Unknown", "little", "moderate", "quite rich", "rich"]
HOUSING_ORDER = ["own", "rent", "free", "Unknown"]
SEX_ORDER = ["male", "female", "Unknown"]
PURPOSE_ORDER = [
    "car",
    "furniture/equipment",
    "radio/TV",
    "domestic appliances",
    "repairs",
    "education",
    "business",
    "vacation/others",
    "Unknown",
]

CHOOSE_OPTION = "Choose..."

DEFAULT_INPUTS = {
    "age": 0,
    "sex": CHOOSE_OPTION,
    "job": CHOOSE_OPTION,
    "housing": CHOOSE_OPTION,
    "saving_accounts": CHOOSE_OPTION,
    "checking_account": CHOOSE_OPTION,
    "credit_amount": 0,
    "duration": 0,
    "purpose": CHOOSE_OPTION,
}

THEMES = {
    "dark": {
        "bg": "#081320",
        "bg_secondary": "#0d1b2a",
        "surface": "rgba(14, 27, 45, 0.72)",
        "surface_strong": "rgba(22, 38, 61, 0.86)",
        "text": "#f5fbff",
        "muted": "#97adc5",
        "border": "rgba(129, 184, 255, 0.18)",
        "accent": "#21c48f",
        "accent_alt": "#20c7d9",
        "warning": "#ff9f43",
        "danger": "#ff5a6f",
        "shadow": "0 24px 80px rgba(5, 12, 24, 0.42)",
        "hero_gradient": "linear-gradient(135deg, rgba(19, 45, 79, 0.96), rgba(12, 103, 98, 0.88), rgba(255, 159, 67, 0.78))",
    },
    "light": {
        "bg": "#f2f7fb",
        "bg_secondary": "#ffffff",
        "surface": "rgba(255, 255, 255, 0.82)",
        "surface_strong": "rgba(255, 255, 255, 0.96)",
        "text": "#0e2239",
        "muted": "#5a7087",
        "border": "rgba(40, 77, 120, 0.12)",
        "accent": "#0c9a78",
        "accent_alt": "#118ab2",
        "warning": "#d97706",
        "danger": "#dc4c64",
        "shadow": "0 24px 80px rgba(33, 61, 97, 0.14)",
        "hero_gradient": "linear-gradient(135deg, rgba(13, 110, 253, 0.12), rgba(17, 138, 178, 0.16), rgba(255, 193, 7, 0.12))",
    },
}

ARTIFACT_PATHS = {
    "clean_data": DATA_DIR / "credit_risk_clean.csv",
    "risk_profile": DATA_DIR / "risk_profile.json",
    "preprocessor_bundle": MODELS_DIR / "preprocessor_bundle.joblib",
    "random_forest": MODELS_DIR / "random_forest.joblib",
    "xgboost": MODELS_DIR / "xgboost_model.joblib",
    "model_metrics": METRICS_DIR / "model_metrics.json",
    "roc_points": METRICS_DIR / "roc_points.json",
    "shap_summary": EXPLANATIONS_DIR / "shap_summary.png",
    "shap_bar": EXPLANATIONS_DIR / "shap_bar.png",
    "top_shap_features": EXPLANATIONS_DIR / "top_shap_features.json",
}


def dm_to_inr(amount_dm: float | int) -> int:
    return int(round(float(amount_dm) * DM_TO_INR_RATE))


def inr_to_dm(amount_inr: float | int) -> int:
    return int(round(float(amount_inr) / DM_TO_INR_RATE))


def format_inr(amount_inr: float | int) -> str:
    return f"Rs {int(round(float(amount_inr))):,}"
