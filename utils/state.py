from __future__ import annotations

from typing import Any

import streamlit as st

from utils.constants import DEFAULT_INPUTS


def build_defaults(bundle: dict[str, Any] | None) -> dict[str, Any]:
    defaults = dict(DEFAULT_INPUTS)
    return defaults


def initialize_session_state(bundle: dict[str, Any] | None = None) -> None:
    defaults = build_defaults(bundle)
    if "theme_mode" not in st.session_state:
        st.session_state.theme_mode = "dark"
    if "form_defaults" not in st.session_state:
        st.session_state.form_defaults = defaults
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


def reset_form(bundle: dict[str, Any] | None = None) -> None:
    defaults = build_defaults(bundle)
    st.session_state.form_defaults = defaults
    for key, value in defaults.items():
        st.session_state[key] = value
