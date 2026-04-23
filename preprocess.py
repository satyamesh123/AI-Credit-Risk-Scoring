from __future__ import annotations

import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

from utils.constants import ARTIFACT_PATHS, BASE_FEATURES, CATEGORICAL_COLUMNS, NUMERIC_COLUMNS
from utils.validation import ensure_directories, load_json, ordered_categories


def build_preprocessor_bundle() -> dict:
    cleaned_df = pd.read_csv(ARTIFACT_PATHS["clean_data"])
    feature_df = cleaned_df[BASE_FEATURES].copy()
    target = cleaned_df["risk"].astype(int).copy()

    categorical_levels: dict[str, list[str]] = {}
    for column in CATEGORICAL_COLUMNS:
        feature_df[column] = feature_df[column].fillna("Unknown").astype(str)
        categorical_levels[column] = ordered_categories(column, feature_df[column].unique().tolist())
        feature_df[column] = pd.Categorical(feature_df[column], categories=categorical_levels[column])

    encoded_df = pd.get_dummies(feature_df, columns=CATEGORICAL_COLUMNS, dtype=int)
    encoded_feature_names = encoded_df.columns.tolist()

    X_train, X_test, y_train, y_test = train_test_split(
        encoded_df,
        target,
        test_size=0.20,
        random_state=42,
        stratify=target,
    )

    scaler = StandardScaler()
    X_train = X_train.copy()
    X_test = X_test.copy()
    X_train[NUMERIC_COLUMNS] = scaler.fit_transform(X_train[NUMERIC_COLUMNS])
    X_test[NUMERIC_COLUMNS] = scaler.transform(X_test[NUMERIC_COLUMNS])

    feature_bounds = {
        column: {
            "min": int(cleaned_df[column].min()),
            "max": int(cleaned_df[column].max()),
            "median": int(cleaned_df[column].median()),
        }
        for column in NUMERIC_COLUMNS
    }

    bundle = {
        "scaler": scaler,
        "encoded_feature_names": encoded_feature_names,
        "numeric_columns": NUMERIC_COLUMNS,
        "categorical_columns": CATEGORICAL_COLUMNS,
        "categorical_levels": categorical_levels,
        "feature_bounds": feature_bounds,
        "X_train": X_train,
        "X_test": X_test,
        "y_train": y_train,
        "y_test": y_test,
        "cleaned_df": cleaned_df,
        "risk_profile": load_json(ARTIFACT_PATHS["risk_profile"]),
    }
    return bundle


def main() -> None:
    ensure_directories()
    bundle = build_preprocessor_bundle()
    joblib.dump(bundle, ARTIFACT_PATHS["preprocessor_bundle"])
    print(f"Preprocessor bundle saved to {ARTIFACT_PATHS['preprocessor_bundle']}")
    print(f"Encoded feature count: {len(bundle['encoded_feature_names'])}")
    print(f"Train shape: {bundle['X_train'].shape}, Test shape: {bundle['X_test'].shape}")


if __name__ == "__main__":
    main()
