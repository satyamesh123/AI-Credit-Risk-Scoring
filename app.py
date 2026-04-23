from __future__ import annotations

from pathlib import Path

import streamlit as st

from components.dashboard import (
    render_data_explorer,
    render_decision_panel,
    render_gauge,
    render_hero,
    render_metric_row,
    render_model_comparison,
    render_model_insights,
    render_story_tiles,
    render_setup_message,
    render_top_contributors,
)
from components.styling import inject_global_styles
from scorer import load_artifacts, predict_credit_risk
from utils.constants import CHOOSE_OPTION, dm_to_inr, format_inr
from utils.reporting import build_export_record, create_prediction_pdf, record_to_csv_bytes
from utils.state import initialize_session_state, reset_form

st.set_page_config(
    page_title="AI Credit Risk Command Center",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)


def _fallback_bundle() -> dict:
    return {
        "feature_bounds": {
            "age": {"min": 19, "max": 75, "median": 35},
            "credit_amount": {"min": 250, "max": 18424, "median": 3972},
            "duration": {"min": 4, "max": 72, "median": 18},
        },
        "categorical_levels": {
            "sex": ["male", "female", "Unknown"],
            "job": [
                "unskilled and non-resident",
                "unskilled and resident",
                "skilled",
                "highly skilled",
                "Unknown",
            ],
            "housing": ["own", "rent", "free", "Unknown"],
            "saving_accounts": ["Unknown", "little", "moderate", "quite rich", "rich"],
            "checking_account": ["Unknown", "little", "moderate", "quite rich", "rich"],
            "purpose": [
                "car",
                "furniture/equipment",
                "radio/TV",
                "domestic appliances",
                "repairs",
                "education",
                "business",
                "vacation/others",
                "Unknown",
            ],
        },
    }


def _select_options(options: list[str]) -> list[str]:
    return [CHOOSE_OPTION, *options]


def _display_value(value: str | int) -> str:
    if value == CHOOSE_OPTION:
        return "Not selected"
    if value == 0:
        return "0"
    return str(value).title() if isinstance(value, str) else str(value)


def _is_form_complete(user_input: dict) -> bool:
    numeric_ready = all(user_input[column] > 0 for column in ["age", "credit_amount", "duration"])
    categorical_ready = all(
        user_input[column] != CHOOSE_OPTION
        for column in ["sex", "job", "housing", "saving_accounts", "checking_account", "purpose"]
    )
    return numeric_ready and categorical_ready


def _build_hero_state(user_input: dict) -> dict:
    fields = [
        ("age", user_input["age"] > 0),
        ("credit_amount", user_input["credit_amount"] > 0),
        ("duration", user_input["duration"] > 0),
        ("sex", user_input["sex"] != CHOOSE_OPTION),
        ("job", user_input["job"] != CHOOSE_OPTION),
        ("housing", user_input["housing"] != CHOOSE_OPTION),
        ("saving_accounts", user_input["saving_accounts"] != CHOOSE_OPTION),
        ("checking_account", user_input["checking_account"] != CHOOSE_OPTION),
        ("purpose", user_input["purpose"] != CHOOSE_OPTION),
    ]
    completed = sum(1 for _, is_done in fields if is_done)
    total = len(fields)
    completion_percent = int(round((completed / total) * 100)) if total else 0
    missing_map = {
        "age": "set the applicant's age",
        "credit_amount": "enter the requested credit amount",
        "duration": "set the repayment duration",
        "sex": "choose the applicant's sex",
        "job": "choose the job category",
        "housing": "choose the housing type",
        "saving_accounts": "select the savings profile",
        "checking_account": "select the checking account level",
        "purpose": "choose the loan purpose",
    }
    missing_fields = [missing_map[key] for key, is_done in fields if not is_done]

    if completion_percent == 0:
        headline = "Credit Risk Scoring System"
        greeting = "Enter your details to begin the application. Your result will appear automatically once the required fields are completed."
        status_label = "Awaiting Input"
        support_copy = "Use the sidebar to fill the applicant profile. The progress panel will guide you to the next required step."
        micro_prompt = "Begin with age, loan amount, or repayment duration."
    elif completion_percent < 50:
        headline = "Application In Progress"
        greeting = "Your application has started. Continue filling the remaining applicant details to move toward a live result."
        status_label = "Profile Building"
        support_copy = "As each field is completed, the application status updates instantly and prepares the result view."
        micro_prompt = "Good progress. Complete the remaining required details."
    elif completion_percent < 100:
        headline = "Almost Ready"
        greeting = "Most details are already filled in. Complete the last remaining fields to unlock the result."
        status_label = "Nearly Ready"
        support_copy = "Once the final required item is entered, the application will open the full result dashboard automatically."
        micro_prompt = "Just a little more. Finish the remaining fields."
    else:
        headline = "Your Application Is Ready"
        greeting = "All required details are complete. Your credit result is now ready to review below."
        status_label = "Scoring Live"
        support_copy = "Review the result, confidence, and explanation below, then download the application summary if needed."
        micro_prompt = "Application complete. Review your result below."

    next_action = (
        f"Next step: {missing_fields[0].capitalize()}."
        if missing_fields
        else "All required fields are complete. Review the live decision outputs below."
    )

    stages = [
        {
            "eyebrow": "Stage 1",
            "label": "Start Profile",
            "state": "ready" if completion_percent >= 1 else "active",
        },
        {
            "eyebrow": "Stage 2",
            "label": "Complete Inputs",
            "state": "ready" if completion_percent == 100 else ("active" if completion_percent > 0 else "idle"),
        },
        {
            "eyebrow": "Stage 3",
            "label": "View Decision",
            "state": "ready" if completion_percent == 100 else "idle",
        },
    ]

    return {
        "headline": headline,
        "greeting": greeting,
        "status_label": status_label,
        "support_copy": support_copy,
        "micro_prompt": micro_prompt,
        "next_action": next_action,
        "completion_percent": completion_percent,
        "stages": stages,
    }


def _render_sidebar_progress(hero_state: dict) -> None:
    st.markdown(
        f"""
        <div class="sidebar-progress" style="--progress-width:{hero_state['completion_percent']}%;">
            <div class="sidebar-progress-top">
                <strong>Application Status</strong>
                <span>{hero_state['completion_percent']}% Complete</span>
            </div>
            <div class="sidebar-progress-bar">
                <div class="sidebar-progress-fill"></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    for stage in hero_state["stages"]:
        class_name = "sidebar-step"
        if stage["state"] == "ready":
            class_name += " ready"
        elif stage["state"] == "active":
            class_name += " active"
        st.markdown(
            f"""
            <div class="{class_name}">
                <div class="dot"></div>
                <div class="text"><b>{stage['eyebrow']}</b><br/>{stage['label']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    st.markdown(
        f'<div class="sidebar-next">{hero_state["next_action"]}</div>',
        unsafe_allow_html=True,
    )


def render_sidebar(bundle: dict, hero_state: dict) -> dict:
    bounds = bundle["feature_bounds"]
    options = bundle["categorical_levels"]
    credit_bounds_inr = {
        "min": dm_to_inr(bounds["credit_amount"]["min"]),
        "max": dm_to_inr(bounds["credit_amount"]["max"]),
    }

    with st.sidebar:
        st.markdown(
            """
            <div class="sidebar-brand">
                <div class="eyebrow">Fintech Decision Lab</div>
                <div class="brand-title">Applicant Studio</div>
                <div class="brand-copy">
                    Shape a borrower profile in real time and watch the ensemble underwriting signal respond instantly.
                </div>
                <div class="sidebar-meta">
                    <div><b>RF + XGB</b><br/>stacked scoring</div>
                    <div><b>SHAP</b><br/>explainability built in</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        _render_sidebar_progress(hero_state)
        if st.button("Reset profile", use_container_width=True):
            reset_form(bundle)
            st.rerun()

        theme_dark = st.toggle(
            "Dark mode",
            value=st.session_state.theme_mode == "dark",
            help="Switch between the dark fintech command center and a brighter executive mode.",
        )
        st.session_state.theme_mode = "dark" if theme_dark else "light"

        st.caption("Applicant demographics")
        st.slider(
            "Age",
            min_value=0,
            max_value=bounds["age"]["max"],
            key="age",
            help="Set the applicant age in years. Starts at 0 until the applicant enters details.",
        )
        st.selectbox(
            "Sex",
            options=_select_options(options["sex"]),
            key="sex",
            help="Reported applicant sex in the source dataset.",
        )
        st.selectbox(
            "Job category",
            options=_select_options(options["job"]),
            key="job",
            help="Use the descriptive job label, not the numeric code.",
        )
        st.selectbox(
            "Housing",
            options=_select_options(options["housing"]),
            key="housing",
            help="Applicant housing situation.",
        )

        st.caption("Financial profile")
        st.slider(
            "Credit amount (Rs)",
            min_value=0,
            max_value=credit_bounds_inr["max"],
            key="credit_amount",
            help="Requested loan amount in Indian Rupees. The model converts this back to the historical DM scale internally.",
        )
        st.slider(
            "Duration (months)",
            min_value=0,
            max_value=bounds["duration"]["max"],
            key="duration",
            help="Loan term length in months. Starts at 0 until entered by the applicant.",
        )
        st.selectbox(
            "Saving accounts",
            options=_select_options(options["saving_accounts"]),
            key="saving_accounts",
            help="Observed saving account level. Unknown is handled explicitly.",
        )
        st.selectbox(
            "Checking account",
            options=_select_options(options["checking_account"]),
            key="checking_account",
            help="Observed checking account level. Unknown is handled explicitly.",
        )
        st.selectbox(
            "Purpose",
            options=_select_options(options["purpose"]),
            key="purpose",
            help="Primary loan purpose from the original dataset taxonomy.",
        )

    return {
        "age": st.session_state.age,
        "sex": st.session_state.sex,
        "job": st.session_state.job,
        "housing": st.session_state.housing,
        "saving_accounts": st.session_state.saving_accounts,
        "checking_account": st.session_state.checking_account,
        "credit_amount": st.session_state.credit_amount,
        "duration": st.session_state.duration,
        "purpose": st.session_state.purpose,
    }


def render_profile_snapshot(user_input: dict) -> None:
    st.markdown('<div class="section-label">Applicant Snapshot</div>', unsafe_allow_html=True)
    left, right = st.columns(2)
    left.markdown(
        f"""
            <div class="premium-card">
            <div style="font-size:0.78rem;letter-spacing:0.12em;text-transform:uppercase;color:var(--muted);">Core Profile</div>
            <div style="margin-top:0.8rem;line-height:1.9;">
                <b>Age</b> {_display_value(user_input['age'])}<br/>
                <b>Sex</b> {_display_value(user_input['sex'])}<br/>
                <b>Job</b> {_display_value(user_input['job'])}<br/>
                <b>Housing</b> {_display_value(user_input['housing'])}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    right.markdown(
        f"""
        <div class="premium-card">
            <div style="font-size:0.78rem;letter-spacing:0.12em;text-transform:uppercase;color:var(--muted);">Facility Details</div>
            <div style="margin-top:0.8rem;line-height:1.9;">
                <b>Credit</b> {format_inr(user_input['credit_amount'])}<br/>
                <b>Duration</b> {_display_value(user_input['duration'])} months<br/>
                <b>Savings</b> {_display_value(user_input['saving_accounts'])}<br/>
                <b>Purpose</b> {_display_value(user_input['purpose'])}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def main() -> None:
    try:
        artifacts = load_artifacts()
        bundle = artifacts["bundle"]
    except FileNotFoundError as exc:
        artifacts = None
        bundle = _fallback_bundle()
        st.session_state.setdefault("artifact_error", str(exc))

    initialize_session_state(bundle)
    current_input = {
        "age": st.session_state.age,
        "sex": st.session_state.sex,
        "job": st.session_state.job,
        "housing": st.session_state.housing,
        "saving_accounts": st.session_state.saving_accounts,
        "checking_account": st.session_state.checking_account,
        "credit_amount": st.session_state.credit_amount,
        "duration": st.session_state.duration,
        "purpose": st.session_state.purpose,
    }
    hero_state = _build_hero_state(current_input)
    user_input = render_sidebar(bundle, hero_state)
    inject_global_styles(st.session_state.theme_mode)
    render_hero(_build_hero_state(user_input))

    if artifacts is None:
        render_setup_message(["training artifacts"])
        st.info(st.session_state.get("artifact_error", "Run the pipeline to unlock live scoring."))
        st.stop()

    form_complete = _is_form_complete(user_input)
    prediction = None
    csv_bytes = None
    pdf_bytes = None
    if form_complete:
        try:
            with st.spinner("Scoring applicant profile..."):
                scoring_input = {**user_input, "credit_amount_inr": user_input["credit_amount"]}
                prediction = predict_credit_risk(scoring_input)
        except Exception as exc:  # noqa: BLE001
            st.error(f"Prediction failed: {exc}")
            st.stop()

        st.session_state.last_prediction = prediction
        export_record = build_export_record(user_input, prediction)
        csv_bytes = record_to_csv_bytes(export_record)
        pdf_bytes = create_prediction_pdf(user_input, prediction, artifacts["metrics"])

    with st.sidebar:
        st.markdown("## Export")
        st.download_button(
            "Download CSV snapshot",
            data=csv_bytes or b"",
            file_name="credit_risk_snapshot.csv",
            mime="text/csv",
            use_container_width=True,
            disabled=not form_complete,
        )
        st.download_button(
            "Download PDF report",
            data=pdf_bytes or b"",
            file_name="credit_risk_report.pdf",
            mime="application/pdf",
            use_container_width=True,
            disabled=not form_complete,
        )

    tabs = st.tabs(["Risk Dashboard", "Model Insights", "Model Comparison", "Data Explorer"])

    with tabs[0]:
        if not form_complete:
            st.info(
                "Enter age, credit amount, duration, and choose all dropdown values to activate live scoring."
            )
            render_profile_snapshot(user_input)
        else:
            render_metric_row(prediction)
            render_gauge(prediction)
            overview_left, overview_right = st.columns([1.05, 0.95])
            with overview_left:
                render_profile_snapshot(user_input)
                render_story_tiles(user_input, prediction)
            with overview_right:
                render_decision_panel(prediction)
                render_top_contributors(prediction)

    with tabs[1]:
        if not form_complete:
            st.info("Model insights unlock after the applicant completes the form.")
        else:
            render_model_insights(artifacts["metrics"], artifacts["shap_paths"], artifacts["top_shap"])

    with tabs[2]:
        if not form_complete:
            st.info("Model comparison unlocks after the applicant completes the form.")
        else:
            render_model_comparison(artifacts["metrics"], artifacts["roc_points"])

    with tabs[3]:
        render_data_explorer(artifacts["bundle"]["cleaned_df"])


if __name__ == "__main__":
    main()
