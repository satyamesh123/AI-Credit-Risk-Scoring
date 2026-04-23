from __future__ import annotations

import joblib
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
    roc_curve,
)
from xgboost import XGBClassifier

from utils.constants import ARTIFACT_PATHS
from utils.validation import dump_json, ensure_directories, prettify_feature_name


def evaluate_model(model, X_test, y_test, feature_names: list[str]) -> tuple[dict, dict]:
    probabilities = model.predict_proba(X_test)[:, 1]
    predictions = (probabilities >= 0.5).astype(int)
    fpr, tpr, _ = roc_curve(y_test, probabilities)
    metrics = {
        "accuracy": float(accuracy_score(y_test, predictions)),
        "roc_auc": float(roc_auc_score(y_test, probabilities)),
        "f1": float(f1_score(y_test, predictions)),
        "precision": float(precision_score(y_test, predictions, zero_division=0)),
        "recall": float(recall_score(y_test, predictions, zero_division=0)),
        "confusion_matrix": confusion_matrix(y_test, predictions).tolist(),
        "feature_importance": [
            {
                "feature": prettify_feature_name(name),
                "raw_feature": name,
                "importance": float(value),
            }
            for name, value in sorted(
                zip(feature_names, model.feature_importances_), key=lambda item: item[1], reverse=True
            )
        ],
    }
    roc_payload = {
        "fpr": [float(value) for value in fpr],
        "tpr": [float(value) for value in tpr],
    }
    return metrics, roc_payload


def main() -> None:
    ensure_directories()
    bundle = joblib.load(ARTIFACT_PATHS["preprocessor_bundle"])
    X_train = bundle["X_train"]
    X_test = bundle["X_test"]
    y_train = bundle["y_train"]
    y_test = bundle["y_test"]
    feature_names = bundle["encoded_feature_names"]

    negative_count = int((y_train == 0).sum())
    positive_count = int((y_train == 1).sum())
    scale_pos_weight = negative_count / max(positive_count, 1)

    random_forest = RandomForestClassifier(
        n_estimators=420,
        max_depth=10,
        min_samples_leaf=4,
        min_samples_split=8,
        max_features="sqrt",
        class_weight="balanced_subsample",
        random_state=42,
        n_jobs=-1,
    )
    xgboost_model = XGBClassifier(
        n_estimators=380,
        max_depth=4,
        learning_rate=0.05,
        subsample=0.92,
        colsample_bytree=0.90,
        min_child_weight=2,
        reg_lambda=1.1,
        objective="binary:logistic",
        eval_metric="auc",
        scale_pos_weight=scale_pos_weight,
        random_state=42,
        tree_method="hist",
        n_jobs=0,
    )

    random_forest.fit(X_train, y_train)
    xgboost_model.fit(X_train, y_train)

    rf_metrics, rf_roc = evaluate_model(random_forest, X_test, y_test, feature_names)
    xgb_metrics, xgb_roc = evaluate_model(xgboost_model, X_test, y_test, feature_names)

    metrics_payload = {
        "random_forest": rf_metrics,
        "xgboost": xgb_metrics,
    }
    roc_payload = {
        "random_forest": rf_roc,
        "xgboost": xgb_roc,
    }

    joblib.dump(random_forest, ARTIFACT_PATHS["random_forest"])
    joblib.dump(xgboost_model, ARTIFACT_PATHS["xgboost"])
    dump_json(ARTIFACT_PATHS["model_metrics"], metrics_payload)
    dump_json(ARTIFACT_PATHS["roc_points"], roc_payload)

    print(f"Random Forest saved to {ARTIFACT_PATHS['random_forest']}")
    print(f"XGBoost saved to {ARTIFACT_PATHS['xgboost']}")
    print(f"Metrics saved to {ARTIFACT_PATHS['model_metrics']}")
    print(
        "Validation AUCs -> RF: "
        f"{metrics_payload['random_forest']['roc_auc']:.3f}, "
        f"XGB: {metrics_payload['xgboost']['roc_auc']:.3f}"
    )


if __name__ == "__main__":
    main()
