from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import joblib
import pandas as pd

from utils.constants import (
    ARTIFACT_PATHS,
    BASE_FEATURES,
    CATEGORICAL_COLUMNS,
    NUMERIC_COLUMNS,
    RISK_COLORS,
    RISK_EXPLANATIONS,
    inr_to_dm,
)
from utils.validation import (
    load_json,
    safe_probability,
    sanitize_user_input,
    summarize_reason_factors,
)


def _core_missing_artifacts() -> list[str]:
    required = [
        "clean_data",
        "risk_profile",
        "preprocessor_bundle",
        "random_forest",
        "xgboost",
        "model_metrics",
        "roc_points",
    ]
    return [name for name in required if not ARTIFACT_PATHS[name].exists()]


@lru_cache(maxsize=1)
def load_artifacts() -> dict[str, Any]:
    missing = _core_missing_artifacts()
    if missing:
        raise FileNotFoundError(
            "Required artifacts are missing: "
            + ", ".join(missing)
            + ". Run the training pipeline from the project directory."
        )

    bundle = joblib.load(ARTIFACT_PATHS["preprocessor_bundle"])
    random_forest = joblib.load(ARTIFACT_PATHS["random_forest"])
    xgboost_model = joblib.load(ARTIFACT_PATHS["xgboost"])
    metrics = load_json(ARTIFACT_PATHS["model_metrics"])
    roc_points = load_json(ARTIFACT_PATHS["roc_points"])
    risk_profile = load_json(ARTIFACT_PATHS["risk_profile"])
    top_shap_payload = {"features": []}
    if ARTIFACT_PATHS["top_shap_features"].exists():
        top_shap_payload = load_json(ARTIFACT_PATHS["top_shap_features"])

    return {
        "bundle": bundle,
        "random_forest": random_forest,
        "xgboost": xgboost_model,
        "metrics": metrics,
        "roc_points": roc_points,
        "risk_profile": risk_profile,
        "top_shap": top_shap_payload.get("features", []),
        "shap_paths": {
            "summary": ARTIFACT_PATHS["shap_summary"],
            "bar": ARTIFACT_PATHS["shap_bar"],
        },
    }


def _normalize_input_payload(user_input: dict[str, Any]) -> dict[str, Any]:
    normalized = dict(user_input)
    if "credit_amount_inr" in normalized:
        normalized["credit_amount"] = inr_to_dm(normalized["credit_amount_inr"])
    return normalized


def build_input_frame(user_input: dict[str, Any]) -> pd.DataFrame:
    artifacts = load_artifacts()
    bundle = artifacts["bundle"]
    normalized = _normalize_input_payload(user_input)
    sanitized = sanitize_user_input(normalized, bundle["categorical_levels"], bundle["feature_bounds"])
    row = pd.DataFrame([[sanitized[column] for column in BASE_FEATURES]], columns=BASE_FEATURES)

    for column in CATEGORICAL_COLUMNS:
        row[column] = pd.Categorical(row[column], categories=bundle["categorical_levels"][column])

    encoded = pd.get_dummies(row, columns=CATEGORICAL_COLUMNS, dtype=int)
    encoded = encoded.reindex(columns=bundle["encoded_feature_names"], fill_value=0)
    encoded[NUMERIC_COLUMNS] = bundle["scaler"].transform(encoded[NUMERIC_COLUMNS])
    return encoded


def _risk_tier(probability: float) -> tuple[str, str]:
    if probability < 0.35:
        return "LOW", RISK_COLORS["LOW"]
    if probability < 0.65:
        return "MEDIUM", RISK_COLORS["MEDIUM"]
    return "HIGH", RISK_COLORS["HIGH"]


def predict_credit_risk(user_input: dict[str, Any]) -> dict[str, Any]:
    artifacts = load_artifacts()
    bundle = artifacts["bundle"]
    normalized = _normalize_input_payload(user_input)
    sanitized = sanitize_user_input(normalized, bundle["categorical_levels"], bundle["feature_bounds"])
    features = build_input_frame(sanitized)

    rf_probability = safe_probability(artifacts["random_forest"].predict_proba(features)[0, 1])
    xgb_probability = safe_probability(artifacts["xgboost"].predict_proba(features)[0, 1])

    rf_auc = artifacts["metrics"]["random_forest"]["roc_auc"]
    xgb_auc = artifacts["metrics"]["xgboost"]["roc_auc"]
    weight_total = rf_auc + xgb_auc
    rf_weight = rf_auc / weight_total
    xgb_weight = xgb_auc / weight_total

    probability = safe_probability((rf_probability * rf_weight) + (xgb_probability * xgb_weight))
    risk_label, risk_color = _risk_tier(probability)
    top_contributors = summarize_reason_factors(sanitized)

    explanation = (
        f"{RISK_EXPLANATIONS[risk_label]} "
        f"Strongest current signals: {top_contributors[0]} "
        f"{top_contributors[1] if len(top_contributors) > 1 else ''}".strip()
    )
    confidence_percent = max(probability, 1 - probability) * 100

    return {
        "probability": probability,
        "confidence_percent": confidence_percent,
        "risk_label": risk_label,
        "risk_color": risk_color,
        "plain_english_explanation": explanation,
        "model_breakdown": {
            "random_forest": {
                "probability": rf_probability,
                "validation_auc": rf_auc,
                "weight": rf_weight,
            },
            "xgboost": {
                "probability": xgb_probability,
                "validation_auc": xgb_auc,
                "weight": xgb_weight,
            },
        },
        "top_contributors": top_contributors,
    }


if __name__ == "__main__":
    sample_input = {
        "age": 33,
        "sex": "male",
        "job": "skilled",
        "housing": "own",
        "saving_accounts": "moderate",
        "checking_account": "moderate",
        "credit_amount": 4200,
        "duration": 18,
        "purpose": "radio/TV",
    }
    print(predict_credit_risk(sample_input))
