from __future__ import annotations

import joblib
import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import shap

from utils.constants import ARTIFACT_PATHS
from utils.validation import dump_json, ensure_directories, prettify_feature_name


def compute_shap_with_fallback(model, X_train):
    sample_sizes = [min(250, len(X_train)), min(140, len(X_train)), min(80, len(X_train))]
    sample_sizes = [size for index, size in enumerate(sample_sizes) if size > 0 and size not in sample_sizes[:index]]
    explainer = shap.TreeExplainer(model)
    last_error = None
    for size in sample_sizes:
        sample = X_train.sample(n=size, random_state=42)
        try:
            explanation = explainer(sample)
            values = explanation.values if hasattr(explanation, "values") else explanation
            return sample, np.array(values)
        except Exception as exc:  # noqa: BLE001
            last_error = exc
    raise RuntimeError(f"Unable to compute SHAP values. Last error: {last_error}") from last_error


def main() -> None:
    ensure_directories()
    bundle = joblib.load(ARTIFACT_PATHS["preprocessor_bundle"])
    model = joblib.load(ARTIFACT_PATHS["xgboost"])
    X_train = bundle["X_train"]

    sample, shap_values = compute_shap_with_fallback(model, X_train)

    plt.figure(figsize=(11, 6))
    shap.summary_plot(shap_values, sample, show=False, max_display=12)
    plt.tight_layout()
    plt.savefig(ARTIFACT_PATHS["shap_summary"], dpi=220, bbox_inches="tight")
    plt.close()

    plt.figure(figsize=(11, 6))
    shap.summary_plot(shap_values, sample, plot_type="bar", show=False, max_display=12)
    plt.tight_layout()
    plt.savefig(ARTIFACT_PATHS["shap_bar"], dpi=220, bbox_inches="tight")
    plt.close()

    mean_abs = np.abs(shap_values).mean(axis=0)
    top_features = [
        {
            "feature": prettify_feature_name(name),
            "raw_feature": name,
            "mean_abs_shap": float(value),
        }
        for name, value in sorted(
            zip(sample.columns, mean_abs), key=lambda item: item[1], reverse=True
        )[:20]
    ]
    dump_json(ARTIFACT_PATHS["top_shap_features"], {"features": top_features})

    print(f"SHAP summary saved to {ARTIFACT_PATHS['shap_summary']}")
    print(f"SHAP bar summary saved to {ARTIFACT_PATHS['shap_bar']}")
    print(f"Top SHAP features saved to {ARTIFACT_PATHS['top_shap_features']}")


if __name__ == "__main__":
    main()
