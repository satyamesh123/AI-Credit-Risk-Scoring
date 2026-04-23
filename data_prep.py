from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path

import pandas as pd

from utils.constants import ARTIFACT_PATHS, CATEGORICAL_COLUMNS
from utils.validation import (
    dump_json,
    ensure_directories,
    find_balanced_threshold,
    map_job_to_string,
    resolve_dataset_path,
    standardize_columns,
    validate_cleaned_dataframe,
)


def build_risk_score(df: pd.DataFrame) -> pd.Series:
    p70 = df["credit_amount"].quantile(0.70)
    p85 = df["credit_amount"].quantile(0.85)
    risk_score = (
        (df["duration"] >= 30).astype(int)
        + (df["duration"] >= 48).astype(int)
        + (df["credit_amount"] >= p70).astype(int)
        + (df["credit_amount"] >= p85).astype(int)
        + (df["age"] <= 25).astype(int)
        + df["housing"].isin(["rent", "free"]).astype(int)
        + df["saving_accounts"].isin(["little", "Unknown"]).astype(int)
        + df["checking_account"].isin(["little", "Unknown"]).astype(int)
        + df["job"].isin(["unskilled and non-resident", "unskilled and resident"]).astype(int)
        + df["purpose"].isin(["business", "education", "car"]).astype(int)
    )
    return risk_score.astype(int)


def prepare_dataset(dataset_path: Path) -> pd.DataFrame:
    raw_df = pd.read_csv(dataset_path)
    if "Unnamed: 0" in raw_df.columns:
        raw_df = raw_df.drop(columns=["Unnamed: 0"])

    df = standardize_columns(raw_df)
    df["job"] = df["job"].apply(map_job_to_string)

    for column in CATEGORICAL_COLUMNS:
        if column == "job":
            continue
        df[column] = (
            df[column]
            .fillna("Unknown")
            .astype(str)
            .str.strip()
            .replace({"": "Unknown", "nan": "Unknown", "NaN": "Unknown"})
        )

    df["risk_score"] = build_risk_score(df)
    threshold, risky_share = find_balanced_threshold(df["risk_score"], target_share=0.40)
    df["risk"] = (df["risk_score"] >= threshold).astype(int)
    df["risk_label"] = df["risk"].map({0: "Safe", 1: "Risky"})

    validate_cleaned_dataframe(df)

    profile = {
        "dataset_rows": int(len(df)),
        "threshold": threshold,
        "risky_share": risky_share,
        "class_balance": {str(key): int(value) for key, value in Counter(df["risk"]).items()},
        "minority_share": min(risky_share, 1 - risky_share),
        "null_count": int(df.isna().sum().sum()),
        "risk_score_distribution": {str(key): int(value) for key, value in Counter(df["risk_score"]).items()},
        "feature_ranges": {
            column: {
                "min": int(df[column].min()),
                "max": int(df[column].max()),
                "median": float(df[column].median()),
            }
            for column in ["age", "credit_amount", "duration"]
        },
        "note": "The risk target is synthetic and derived from explicit underwriting-style rules.",
    }

    df.to_csv(ARTIFACT_PATHS["clean_data"], index=False)
    dump_json(ARTIFACT_PATHS["risk_profile"], profile)
    return df


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare and label the German credit dataset.")
    parser.add_argument("--dataset", type=str, default=None, help="Optional path to the raw CSV dataset.")
    args = parser.parse_args()

    ensure_directories()
    dataset_path = resolve_dataset_path(args.dataset)
    prepared_df = prepare_dataset(dataset_path)
    print(f"Prepared dataset saved to {ARTIFACT_PATHS['clean_data']}")
    print(f"Risk profile saved to {ARTIFACT_PATHS['risk_profile']}")
    print(prepared_df['risk_label'].value_counts().to_string())


if __name__ == "__main__":
    main()
