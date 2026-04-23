from __future__ import annotations

import html
from pathlib import Path
from typing import Any

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as components

from utils.constants import DM_TO_INR_RATE, RISK_COLORS, format_inr


def render_hero(hero_state: dict[str, Any]) -> None:
    st.markdown(
        f"""
        <section class="hero-shell">
            <div class="hero-kicker">Credit Application</div>
            <h1 class="hero-title">{hero_state['headline']}</h1>
            <div class="hero-typewriter">{hero_state['micro_prompt']}</div>
            <p class="hero-copy">{hero_state['greeting']}</p>
            <p class="hero-subcopy">{hero_state['support_copy']}</p>
        </section>
        """,
        unsafe_allow_html=True,
    )


def apply_fintech_layout(fig: go.Figure, height: int = 400) -> go.Figure:
    fig.update_layout(
        height=height,
        margin=dict(l=10, r=10, t=52, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Manrope, sans-serif"),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            bgcolor="rgba(0,0,0,0)",
        ),
    )
    return fig


def apply_inr_axis(fig: go.Figure, axis: str = "x") -> go.Figure:
    fig.update_layout(
        **{
            f"{axis}axis": dict(
                tickprefix="Rs ",
                separatethousands=True,
            )
        }
    )
    return fig


def render_metric_row(prediction: dict[str, Any]) -> None:
    columns = st.columns(4)
    items = [
        ("Ensemble Probability", f"{prediction['probability'] * 100:.1f}%", "Weighted RF + XGB"),
        ("Confidence", f"{prediction['confidence_percent']:.1f}%", "Distance from the cutoff zone"),
        ("Random Forest", f"{prediction['model_breakdown']['random_forest']['probability'] * 100:.1f}%", "Validation-weighted"),
        ("XGBoost", f"{prediction['model_breakdown']['xgboost']['probability'] * 100:.1f}%", "Validation-weighted"),
    ]
    for column, (label, value, subtext) in zip(columns, items):
        column.markdown(
            f"""
            <div class="mini-card">
                <h4>{label}</h4>
                <div class="value">{value}</div>
                <div class="sub">{subtext}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_decision_panel(prediction: dict[str, Any]) -> None:
    rows = [
        ("LOW", "#21c48f", "Best fit for the synthetic policy. Typically backed by liquidity, stability, and moderate leverage."),
        ("MEDIUM", "#ff9f43", "Borderline zone that deserves a human review before approval terms are finalized."),
        ("HIGH", "#ff5a6f", "Multiple stress signals cluster together and raise repayment-risk concerns."),
    ]
    st.markdown('<div class="premium-card glow"><div class="section-label">Decision Bands</div></div>', unsafe_allow_html=True)
    for label, color, copy in rows:
        active = '<span class="active-pill">ACTIVE</span>' if label == prediction["risk_label"] else ""
        st.markdown(
            f"""
            <div class="band-row">
                <div class="band-dot" style="background:{color};"></div>
                <div class="band-copy">
                    <strong>{label} risk</strong>
                    <span>{copy}</span>
                </div>
                {active}
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_story_tiles(user_input: dict[str, Any], prediction: dict[str, Any]) -> None:
    stress_count = len(prediction["top_contributors"])
    requested_intensity = user_input["credit_amount"] / max(user_input["duration"], 1)
    st.markdown(
        f"""
        <div class="premium-card">
            <div class="section-label">Decision Story</div>
            <div class="story-grid">
                <div class="story-tile">
                    <div class="label">Risk Tier</div>
                    <div class="big" style="color:{prediction['risk_color']};">{prediction['risk_label']}</div>
                    <div class="small">The ensemble settles in this band after blending both model probabilities.</div>
                </div>
                <div class="story-tile">
                    <div class="label">Monthly Intensity</div>
                    <div class="big">{format_inr(requested_intensity)}</div>
                    <div class="small">Credit amount divided by duration provides a simple repayment-pressure signal.</div>
                </div>
                <div class="story-tile">
                    <div class="label">Stress Signals</div>
                    <div class="big">{stress_count}</div>
                    <div class="small">Narrative factors currently highlighted by the rules-driven explainer.</div>
                </div>
                <div class="story-tile">
                    <div class="label">Use Case</div>
                    <div class="big">{user_input['purpose'].title()}</div>
                    <div class="small">Purpose can shift the synthetic underwriting stance, especially in more volatile categories.</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_gauge(prediction: dict[str, Any]) -> None:
    color = RISK_COLORS[prediction["risk_label"]]
    percentage = round(prediction["probability"] * 100, 1)
    html = f"""
    <html>
    <head>
    <style>
    body {{
        margin: 0;
        background: transparent;
        font-family: Manrope, sans-serif;
        color: white;
    }}
    .shell {{
        background: rgba(255,255,255,0.06);
        border: 1px solid rgba(255,255,255,0.12);
        border-radius: 24px;
        padding: 18px;
        min-height: 370px;
        display: grid;
        grid-template-columns: 1.05fr 1fr;
        gap: 18px;
        align-items: center;
    }}
    .gauge {{
        width: 230px;
        height: 230px;
        margin: 0 auto;
        border-radius: 50%;
        background:
            radial-gradient(circle at center, rgba(5,10,17,0.95) 0 58%, transparent 58.5%),
            conic-gradient({color} 0deg, {color} calc(var(--deg) * 1deg), rgba(255,255,255,0.12) 0);
        display: grid;
        place-items: center;
        box-shadow: 0 0 0 12px rgba(255,255,255,0.03), 0 18px 48px rgba(0,0,0,0.26);
        position: relative;
        overflow: hidden;
    }}
    .gauge::before {{
        content: "";
        position: absolute;
        inset: -20%;
        background: conic-gradient(from 180deg, rgba(255,255,255,0.0), rgba(255,255,255,0.08), rgba(255,255,255,0.0));
        animation: orbit 5.2s linear infinite;
    }}
    .gauge::after {{
        content: "";
        position: absolute;
        inset: 18px;
        border-radius: 50%;
        border: 1px solid rgba(255,255,255,0.07);
    }}
    .gauge-value {{
        text-align: center;
        z-index: 2;
    }}
    .gauge-value .num {{
        font-size: 2.45rem;
        font-weight: 800;
        line-height: 1;
    }}
    .gauge-value .cap {{
        font-size: 0.82rem;
        letter-spacing: 0.12em;
        opacity: 0.75;
        text-transform: uppercase;
        margin-top: 0.35rem;
    }}
    .right {{
        display: flex;
        flex-direction: column;
        gap: 14px;
    }}
    .badge {{
        align-self: flex-start;
        padding: 0.45rem 0.9rem;
        border-radius: 999px;
        background: linear-gradient(135deg, {color}, rgba(255,255,255,0.15));
        box-shadow: 0 0 24px rgba(255,255,255,0.06);
        font-weight: 800;
        letter-spacing: 0.08em;
    }}
    .title {{
        font-size: 1.32rem;
        font-weight: 800;
        line-height: 1.25;
    }}
    .copy {{
        color: rgba(255,255,255,0.78);
        line-height: 1.6;
        font-size: 0.96rem;
    }}
    .bar-track {{
        background: rgba(255,255,255,0.08);
        border-radius: 999px;
        height: 14px;
        overflow: hidden;
    }}
    .bar-fill {{
        width: 0%;
        height: 100%;
        border-radius: 999px;
        background: linear-gradient(90deg, {color}, rgba(255,255,255,0.42));
        animation: fillBar 1.3s ease forwards;
    }}
    .grid {{
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 10px;
    }}
    .chip {{
        padding: 0.9rem;
        border-radius: 18px;
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.1);
    }}
    .chip small {{
        display: block;
        opacity: 0.72;
        margin-bottom: 6px;
    }}
    .chip strong {{
        font-size: 1.1rem;
    }}
    @keyframes fillBar {{
        from {{ width: 0%; }}
        to {{ width: {percentage}%; }}
    }}
    @keyframes orbit {{
        from {{ transform: rotate(0deg); }}
        to {{ transform: rotate(360deg); }}
    }}
    @media (max-width: 760px) {{
        .shell {{
            grid-template-columns: 1fr;
        }}
        .grid {{
            grid-template-columns: 1fr;
        }}
        .title {{
            font-size: 1.5rem;
        }}
    }}
    </style>
    </head>
    <body>
        <div class="shell" style="--deg:{percentage * 3.6};">
            <div class="gauge">
                <div class="gauge-value">
                    <div class="num" id="count">0%</div>
                    <div class="cap">Confidence</div>
                </div>
            </div>
            <div class="right">
                <div class="badge">{prediction["risk_label"]} RISK</div>
                <div class="title">{prediction["plain_english_explanation"]}</div>
                <div class="copy">This outcome combines both model opinions and then maps the final score into a three-tier underwriting signal.</div>
                <div class="bar-track"><div class="bar-fill"></div></div>
                <div class="grid">
                    <div class="chip"><small>Random Forest</small><strong>{prediction["model_breakdown"]["random_forest"]["probability"] * 100:.1f}%</strong></div>
                    <div class="chip"><small>XGBoost</small><strong>{prediction["model_breakdown"]["xgboost"]["probability"] * 100:.1f}%</strong></div>
                </div>
            </div>
        </div>
        <script>
        const target = {prediction["confidence_percent"]:.1f};
        let current = 0;
        const el = document.getElementById("count");
        const step = () => {{
            current += Math.max(1, (target - current) * 0.12);
            if (current >= target - 0.3) {{
                current = target;
            }}
            el.textContent = `${{current.toFixed(1)}}%`;
            if (current < target) {{
                requestAnimationFrame(step);
            }}
        }};
        requestAnimationFrame(step);
        </script>
    </body>
    </html>
    """
    components.html(html, height=395)


def render_top_contributors(prediction: dict[str, Any]) -> None:
    st.markdown('<div class="section-label">Primary Drivers</div>', unsafe_allow_html=True)
    for contributor in prediction["top_contributors"]:
        st.markdown(f'<div class="insight-note">{contributor}</div>', unsafe_allow_html=True)


def render_model_insights(metrics: dict[str, Any], shap_paths: dict[str, Path], top_shap: list[dict[str, Any]]) -> None:
    left, right = st.columns([1.1, 1.0])
    if shap_paths["summary"].exists():
        left.image(str(shap_paths["summary"]), use_container_width=True)
    else:
        left.info("SHAP summary asset not generated yet. Run `py explainer.py`.")
    if shap_paths["bar"].exists():
        right.image(str(shap_paths["bar"]), use_container_width=True)
    else:
        right.info("SHAP bar asset not generated yet. Run `py explainer.py`.")

    if top_shap:
        shap_df = pd.DataFrame(top_shap)
        fig = px.bar(
            shap_df.sort_values("mean_abs_shap", ascending=True).tail(12),
            x="mean_abs_shap",
            y="feature",
            orientation="h",
            color="mean_abs_shap",
            color_continuous_scale=["#20c7d9", "#21c48f", "#ff9f43"],
            labels={"mean_abs_shap": "Mean |SHAP|", "feature": "Feature"},
            title="Top SHAP Contributors",
        )
        apply_fintech_layout(fig, height=430)
        st.plotly_chart(fig, use_container_width=True)

    importance_frames = []
    for model_name, payload in metrics.items():
        importance = payload.get("feature_importance", [])
        if importance:
            frame = pd.DataFrame(importance).head(12)
            frame["model"] = model_name.replace("_", " ").title()
            importance_frames.append(frame)
    if importance_frames:
        merged = pd.concat(importance_frames, ignore_index=True)
        fig = px.bar(
            merged,
            x="importance",
            y="feature",
            color="model",
            facet_col="model",
            orientation="h",
            title="Encoded Feature Importance by Model",
        )
        apply_fintech_layout(fig, height=480)
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)


def render_model_comparison(metrics: dict[str, Any], roc_points: dict[str, Any]) -> None:
    comparison_fig = go.Figure()
    for model_name, values in roc_points.items():
        comparison_fig.add_trace(
            go.Scatter(
                x=values["fpr"],
                y=values["tpr"],
                mode="lines",
                name=model_name.replace("_", " ").title(),
                line=dict(width=3),
            )
        )
    comparison_fig.add_trace(
        go.Scatter(x=[0, 1], y=[0, 1], mode="lines", name="Baseline", line=dict(dash="dash"))
    )
    comparison_fig.update_layout(
        title="ROC Curve Comparison",
        xaxis_title="False Positive Rate",
        yaxis_title="True Positive Rate",
    )
    apply_fintech_layout(comparison_fig, height=420)
    st.plotly_chart(comparison_fig, use_container_width=True)

    metric_columns = st.columns(len(metrics))
    for column, (model_name, payload) in zip(metric_columns, metrics.items()):
        column.markdown(
            f"""
            <div class="premium-card">
                <div class="section-label">{model_name.replace('_', ' ').title()}</div>
                <div style="font-size:1.75rem;font-weight:800;">AUC {payload['roc_auc']:.3f}</div>
                <div style="margin-top:0.65rem;color:var(--muted);">
                    Accuracy {payload['accuracy']:.3f}<br/>
                    F1 Score {payload['f1']:.3f}<br/>
                    Precision {payload['precision']:.3f}<br/>
                    Recall {payload['recall']:.3f}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    heat_cols = st.columns(len(metrics))
    for column, (model_name, payload) in zip(heat_cols, metrics.items()):
        matrix = payload["confusion_matrix"]
        fig = go.Figure(
            data=go.Heatmap(
                z=matrix,
                x=["Pred Safe", "Pred Risky"],
                y=["Actual Safe", "Actual Risky"],
                colorscale=[[0, "#0c9a78"], [0.5, "#20c7d9"], [1, "#ff9f43"]],
                showscale=False,
                text=matrix,
                texttemplate="%{text}",
            )
        )
        fig.update_layout(
            title=f"{model_name.replace('_', ' ').title()} Confusion Matrix",
        )
        apply_fintech_layout(fig, height=320)
        column.plotly_chart(fig, use_container_width=True)


def render_data_explorer(df: pd.DataFrame) -> None:
    explorer_df = df.copy()
    explorer_df["credit_amount_rs"] = explorer_df["credit_amount"].apply(format_inr)
    explorer_df["credit_amount_inr"] = explorer_df["credit_amount"] * DM_TO_INR_RATE
    explorer_df["risk_segment"] = explorer_df["risk"].map({0: "Safe", 1: "Risky"})

    col1, col2 = st.columns(2)
    fig1 = px.histogram(
        explorer_df,
        x="credit_amount_inr",
        color="risk_segment",
        nbins=24,
        barmode="overlay",
        marginal="rug",
        title="Credit Amount Distribution by Risk Segment (Rs)",
        color_discrete_map={"Safe": "#21c48f", "Risky": "#ff5a6f"},
    )
    apply_fintech_layout(fig1, height=380)
    apply_inr_axis(fig1, axis="x")
    fig1.update_traces(
        hovertemplate="Risk segment=%{fullData.name}<br>Credit amount=%{x:,.0f} Rs<br>Count=%{y}<extra></extra>"
    )
    fig1.update_xaxes(title_text="Credit amount (Rs)")
    col1.plotly_chart(fig1, use_container_width=True)

    fig2 = px.scatter(
        explorer_df,
        x="age",
        y="credit_amount_inr",
        color="risk_segment",
        size="duration",
        hover_data={
            "purpose": True,
            "housing": True,
            "job": True,
            "duration": True,
            "credit_amount_inr": ":,.0f",
            "age": True,
        },
        title="Age vs Credit Amount (Rs)",
        color_discrete_map={"Safe": "#20c7d9", "Risky": "#ff9f43"},
    )
    fig2.update_traces(marker=dict(opacity=0.82, line=dict(width=0.6, color="rgba(255,255,255,0.35)")))
    apply_fintech_layout(fig2, height=380)
    apply_inr_axis(fig2, axis="y")
    fig2.update_yaxes(title_text="Credit amount (Rs)")
    col2.plotly_chart(fig2, use_container_width=True)

    col3, col4 = st.columns(2)
    purpose_counts = (
        explorer_df.groupby(["purpose", "risk_segment"], observed=True)
        .size()
        .reset_index(name="count")
    )
    fig3 = px.bar(
        purpose_counts,
        x="purpose",
        y="count",
        color="risk_segment",
        barmode="stack",
        title="Purpose Mix Across Segments",
        color_discrete_map={"Safe": "#21c48f", "Risky": "#ff5a6f"},
    )
    apply_fintech_layout(fig3, height=380)
    col3.plotly_chart(fig3, use_container_width=True)

    fig4 = px.sunburst(
        explorer_df,
        path=["housing", "saving_accounts", "risk_segment"],
        values=None,
        title="Housing and Savings Composition",
        color="risk_segment",
        color_discrete_map={"Safe": "#20c7d9", "Risky": "#ff9f43"},
    )
    apply_fintech_layout(fig4, height=380)
    col4.plotly_chart(fig4, use_container_width=True)

    risk_by_job = explorer_df.groupby(["job", "risk_segment"], observed=True).size().reset_index(name="count")
    fig5 = px.bar(
        risk_by_job,
        x="job",
        y="count",
        color="risk_segment",
        title="Risk Segment by Job Category",
        color_discrete_map={"Safe": "#21c48f", "Risky": "#ff9f43"},
    )
    apply_fintech_layout(fig5, height=380)
    fig5.update_layout(xaxis_title="")
    st.plotly_chart(fig5, use_container_width=True)


def render_setup_message(missing_items: list[str]) -> None:
    st.error(
        "The dashboard is missing trained artifacts: "
        + ", ".join(missing_items)
        + ". Run `py data_prep.py`, `py preprocess.py`, `py train.py`, and `py explainer.py` from `credit_risk_system/`."
    )
