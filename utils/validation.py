from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from utils.constants import (
    ACCOUNT_ORDER,
    ARTIFACT_PATHS,
    BASE_FEATURES,
    CATEGORICAL_COLUMNS,
    DATA_DIR,
    DEFAULT_DATASET_PATH,
    EXPLANATIONS_DIR,
    HOUSING_ORDER,
    JOB_LABELS,
    JOB_OPTIONS,
    METRICS_DIR,
    MODELS_DIR,
    NUMERIC_COLUMNS,
    PURPOSE_ORDER,
    RAW_TO_STANDARD,
    REPORTS_DIR,
    SEX_ORDER,
)


def ensure_directories() -> None:
    for directory in (DATA_DIR, METRICS_DIR, EXPLANATIONS_DIR, REPORTS_DIR, MODELS_DIR):
        directory.mkdir(parents=True, exist_ok=True)


def resolve_dataset_path(candidate: str | None = None) -> Path:
    path = Path(candidate).expanduser().resolve() if candidate else DEFAULT_DATASET_PATH.resolve()
    if not path.exists():
        raise FileNotFoundError(f"Dataset not found at {path}")
    return path


def standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    unknown_columns = set(RAW_TO_STANDARD) - set(df.columns)
    if unknown_columns:
        raise ValueError(f"Dataset is missing expected columns: {sorted(unknown_columns)}")
    renamed = df.rename(columns=RAW_TO_STANDARD)
    return renamed[[RAW_TO_STANDARD[key] for key in RAW_TO_STANDARD]]


def map_job_to_string(value: Any) -> str:
    if pd.isna(value):
        return "Unknown"
    if isinstance(value, str):
        stripped = value.strip()
        if stripped in JOB_OPTIONS:
            return stripped
        if stripped.isdigit():
            return JOB_LABELS.get(int(stripped), "Unknown")
        return stripped or "Unknown"
    try:
        return JOB_LABELS.get(int(value), "Unknown")
    except (TypeError, ValueError):
        return "Unknown"


def ordered_categories(column: str, values: list[str]) -> list[str]:
    base_order = {
        "sex": SEX_ORDER,
        "job": JOB_OPTIONS,
        "housing": HOUSING_ORDER,
        "saving_accounts": ACCOUNT_ORDER,
        "checking_account": ACCOUNT_ORDER,
        "purpose": PURPOSE_ORDER,
    }.get(column, [])
    known = [item for item in base_order if item in values]
    extra = sorted(set(values) - set(known))
    return known + extra


def find_balanced_threshold(scores: pd.Series, target_share: float = 0.40) -> tuple[int, float]:
    candidates = sorted(scores.dropna().unique())
    best_threshold = candidates[0]
    best_share = float((scores >= best_threshold).mean())
    best_distance = abs(best_share - target_share)
    for threshold in candidates:
        risky_share = float((scores >= threshold).mean())
        distance = abs(risky_share - target_share)
        if distance < best_distance:
            best_threshold = int(threshold)
            best_share = risky_share
            best_distance = distance
    minority_share = min(best_share, 1 - best_share)
    if not 0.30 <= minority_share <= 0.45:
        raise ValueError(
            "Synthetic risk target is too imbalanced. "
            f"Threshold {best_threshold} produced risky share {best_share:.3f}."
        )
    return int(best_threshold), best_share


def validate_cleaned_dataframe(df: pd.DataFrame) -> None:
    required_columns = set(BASE_FEATURES + ["risk", "risk_label", "risk_score"])
    missing = required_columns - set(df.columns)
    if missing:
        raise ValueError(f"Cleaned dataframe missing required columns: {sorted(missing)}")
    if df.isna().sum().sum() != 0:
        raise ValueError("Cleaned dataframe still contains NaN values.")
    if set(df["risk"].unique()) != {0, 1}:
        raise ValueError("Risk target must contain both 0 and 1 classes.")


def sanitize_user_input(
    user_input: dict[str, Any],
    categorical_levels: dict[str, list[str]],
    feature_bounds: dict[str, dict[str, float]],
) -> dict[str, Any]:
    clean: dict[str, Any] = {}
    for column in NUMERIC_COLUMNS:
        bounds = feature_bounds[column]
        value = user_input.get(column, bounds["median"])
        numeric_value = float(value)
        numeric_value = max(bounds["min"], min(bounds["max"], numeric_value))
        clean[column] = int(round(numeric_value))
    for column in CATEGORICAL_COLUMNS:
        levels = categorical_levels.get(column, ["Unknown"])
        selected = str(user_input.get(column, "Unknown")).strip() or "Unknown"
        clean[column] = selected if selected in levels else "Unknown"
    return clean


def prettify_feature_name(name: str) -> str:
    label = name.replace("_", " ")
    label = label.replace("saving accounts", "saving")
    label = label.replace("checking account", "checking")
    return label.title()


def summarize_reason_factors(user_input: dict[str, Any]) -> list[str]:
    factors: list[str] = []
    if user_input["duration"] >= 48:
        factors.append("Long repayment duration increases exposure.")
    elif user_input["duration"] >= 30:
        factors.append("Above-average duration stretches repayment capacity.")
    if user_input["credit_amount"] >= 9000:
        factors.append("High requested credit amount amplifies the repayment burden.")
    elif user_input["credit_amount"] >= 6500:
        factors.append("Moderately large credit demand adds leverage pressure.")
    if user_input["age"] <= 25:
        factors.append("Younger applicant age adds uncertainty in this synthetic policy.")
    if user_input["saving_accounts"] in {"little", "Unknown"}:
        factors.append("Limited visible savings reduce the cash-buffer signal.")
    if user_input["checking_account"] in {"little", "Unknown"}:
        factors.append("Thin checking-account liquidity is a short-term risk signal.")
    if user_input["housing"] in {"rent", "free"}:
        factors.append("Housing status contributes less ownership stability.")
    if user_input["job"] in {"unskilled and non-resident", "unskilled and resident"}:
        factors.append("Lower job-skill category raises income resilience concerns.")
    if user_input["purpose"] in {"business", "education", "car"}:
        factors.append("Loan purpose falls into a more volatile financing segment.")
    if not factors:
        factors.append("The profile has relatively balanced affordability and stability signals.")
    return factors[:4]


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def dump_json(path: Path, payload: dict[str, Any]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)


def missing_artifacts() -> list[str]:
    return [name for name, path in ARTIFACT_PATHS.items() if not path.exists()]


def safe_probability(probability: float) -> float:
    return float(np.clip(probability, 0.0, 1.0))
