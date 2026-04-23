from __future__ import annotations

import streamlit as st

from utils.constants import THEMES


def inject_global_styles(theme_mode: str) -> None:
    theme = THEMES[theme_mode]
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&display=swap');

        :root {{
            --bg: {theme['bg']};
            --bg-secondary: {theme['bg_secondary']};
            --surface: {theme['surface']};
            --surface-strong: {theme['surface_strong']};
            --text: {theme['text']};
            --muted: {theme['muted']};
            --border: {theme['border']};
            --accent: {theme['accent']};
            --accent-alt: {theme['accent_alt']};
            --warning: {theme['warning']};
            --danger: {theme['danger']};
            --shadow: {theme['shadow']};
            --hero-gradient: {theme['hero_gradient']};
        }}

        html, body, [class*="css"] {{
            font-family: 'Manrope', sans-serif;
        }}

        .stApp {{
            background:
                radial-gradient(circle at top left, rgba(32, 199, 217, 0.08), transparent 28%),
                radial-gradient(circle at 80% 10%, rgba(255, 159, 67, 0.14), transparent 22%),
                linear-gradient(180deg, var(--bg) 0%, var(--bg-secondary) 100%);
            color: var(--text);
        }}

        [data-testid="stHeader"] {{
            background: transparent;
        }}

        [data-testid="stAppViewContainer"] > .main {{
            padding-top: 1.4rem;
        }}

        [data-testid="stSidebar"] {{
            background:
                radial-gradient(circle at top, rgba(32, 199, 217, 0.18), transparent 18%),
                linear-gradient(180deg, rgba(6, 17, 29, 0.97), rgba(7, 25, 38, 0.90));
            border-right: 1px solid rgba(255, 255, 255, 0.06);
        }}

        [data-testid="stSidebar"] * {{
            color: #eff7ff !important;
        }}

        [data-testid="stSidebar"] .stSlider,
        [data-testid="stSidebar"] .stSelectbox,
        [data-testid="stSidebar"] .stToggle,
        [data-testid="stSidebar"] .stButton,
        [data-testid="stSidebar"] .stDownloadButton {{
            padding: 0.25rem 0;
        }}

        [data-testid="stSidebar"] [data-baseweb="select"] > div,
        [data-testid="stSidebar"] [data-baseweb="base-input"] > div {{
            background: rgba(255, 255, 255, 0.06) !important;
            border: 1px solid rgba(255, 255, 255, 0.08) !important;
            border-radius: 16px !important;
        }}

        [data-testid="stSidebar"] .stSlider [data-baseweb="slider"] {{
            padding-top: 0.35rem;
        }}

        [data-testid="stSidebar"] .stSlider [role="slider"] {{
            background: linear-gradient(135deg, var(--accent), var(--accent-alt)) !important;
            box-shadow: 0 0 0 6px rgba(32, 199, 217, 0.12);
        }}

        .hero-shell {{
            position: relative;
            overflow: hidden;
            border-radius: 28px;
            padding: 1.8rem 1.9rem;
            margin-bottom: 1.2rem;
            background: var(--hero-gradient);
            box-shadow: var(--shadow);
            border: 1px solid rgba(255, 255, 255, 0.14);
            animation: floatIn 0.9s ease-out;
        }}

        .hero-grid {{
            display: grid;
            grid-template-columns: minmax(0, 1.5fr) minmax(320px, 0.9fr);
            gap: 1.1rem;
            align-items: stretch;
            position: relative;
            z-index: 2;
        }}

        .hero-main {{
            display: flex;
            flex-direction: column;
            justify-content: center;
        }}

        .hero-panel {{
            border-radius: 24px;
            padding: 1.1rem;
            background: rgba(6, 18, 31, 0.22);
            border: 1px solid rgba(255, 255, 255, 0.12);
            backdrop-filter: blur(18px);
            box-shadow: 0 18px 50px rgba(0, 0, 0, 0.16);
        }}

        .hero-panel-top {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 0.8rem;
            margin-bottom: 0.9rem;
        }}

        .hero-status-badge {{
            display: inline-flex;
            align-items: center;
            gap: 0.45rem;
            padding: 0.38rem 0.8rem;
            border-radius: 999px;
            background: rgba(255,255,255,0.12);
            border: 1px solid rgba(255,255,255,0.14);
            font-size: 0.74rem;
            letter-spacing: 0.12em;
            text-transform: uppercase;
            font-weight: 800;
        }}

        .hero-dial {{
            width: 88px;
            height: 88px;
            border-radius: 50%;
            background:
                radial-gradient(circle at center, rgba(7, 19, 31, 0.92) 0 58%, transparent 58.5%),
                conic-gradient(rgba(32, 199, 217, 0.98) 0deg, rgba(33, 196, 143, 0.98) calc(var(--dial-deg) * 1deg), rgba(255,255,255,0.12) 0);
            display: grid;
            place-items: center;
            position: relative;
            flex: 0 0 88px;
            box-shadow: 0 0 0 8px rgba(255,255,255,0.04);
            animation: dialPulse 2.8s ease-in-out infinite;
        }}

        .hero-dial::after {{
            content: "";
            position: absolute;
            inset: 8px;
            border-radius: 50%;
            border: 1px solid rgba(255,255,255,0.09);
        }}

        .hero-dial-value {{
            position: relative;
            z-index: 2;
            text-align: center;
            line-height: 1;
        }}

        .hero-dial-value strong {{
            display: block;
            font-size: 1.25rem;
            font-weight: 800;
        }}

        .hero-dial-value span {{
            display: block;
            margin-top: 0.18rem;
            font-size: 0.62rem;
            letter-spacing: 0.12em;
            text-transform: uppercase;
            color: rgba(255,255,255,0.72);
        }}

        .hero-progress-track {{
            position: relative;
            height: 14px;
            border-radius: 999px;
            background: rgba(255,255,255,0.10);
            overflow: hidden;
            margin: 0.9rem 0 1rem;
        }}

        .hero-progress-fill {{
            height: 100%;
            width: 0%;
            border-radius: 999px;
            background: linear-gradient(90deg, rgba(32, 199, 217, 0.95), rgba(33, 196, 143, 0.95), rgba(255, 159, 67, 0.95));
            box-shadow: 0 0 28px rgba(32, 199, 217, 0.35);
            animation: progressFlow 1s ease forwards;
        }}

        .hero-progress-track::after {{
            content: "";
            position: absolute;
            top: 0;
            left: -24%;
            width: 22%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.45), transparent);
            animation: railSweep 2.8s linear infinite;
        }}

        .hero-stage-row {{
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 0.55rem;
            margin-bottom: 1rem;
        }}

        .hero-stage {{
            border-radius: 16px;
            padding: 0.8rem 0.75rem;
            background: rgba(255,255,255,0.07);
            border: 1px solid rgba(255,255,255,0.10);
            transition: transform 180ms ease, border-color 180ms ease;
        }}

        .hero-stage:hover {{
            transform: translateY(-2px);
        }}

        .hero-stage.active {{
            background: rgba(255,255,255,0.14);
            border-color: rgba(255,255,255,0.20);
        }}

        .hero-stage.ready {{
            background: rgba(33, 196, 143, 0.18);
            border-color: rgba(33, 196, 143, 0.35);
        }}

        .hero-stage .eyebrow {{
            display: block;
            color: rgba(255,255,255,0.70);
            font-size: 0.68rem;
            letter-spacing: 0.12em;
            text-transform: uppercase;
            margin-bottom: 0.28rem;
        }}

        .hero-stage strong {{
            display: block;
            color: white;
            font-size: 0.92rem;
            line-height: 1.2;
        }}

        .hero-next {{
            border-radius: 18px;
            padding: 0.95rem 1rem;
            background: rgba(255,255,255,0.08);
            border: 1px solid rgba(255,255,255,0.10);
        }}

        .hero-next .label {{
            font-size: 0.7rem;
            text-transform: uppercase;
            letter-spacing: 0.14em;
            color: rgba(255,255,255,0.70);
            margin-bottom: 0.38rem;
        }}

        .hero-next .message {{
            font-size: 0.97rem;
            line-height: 1.55;
            color: rgba(255,255,255,0.94);
            font-weight: 700;
        }}

        .hero-main .hero-subcopy {{
            margin-top: 1rem;
            max-width: 700px;
            color: rgba(255,255,255,0.80);
            line-height: 1.6;
            font-size: 0.97rem;
        }}

        .hero-shell::before,
        .hero-shell::after {{
            content: "";
            position: absolute;
            border-radius: 999px;
            filter: blur(10px);
            opacity: 0.5;
        }}

        .hero-shell::before {{
            width: 180px;
            height: 180px;
            right: -25px;
            top: -55px;
            background: rgba(255, 255, 255, 0.18);
        }}

        .hero-shell::after {{
            width: 140px;
            height: 140px;
            left: -35px;
            bottom: -45px;
            background: rgba(33, 196, 143, 0.22);
        }}

        .hero-kicker {{
            letter-spacing: 0.18em;
            text-transform: uppercase;
            font-size: 0.74rem;
            opacity: 0.82;
            margin-bottom: 0.7rem;
        }}

        .hero-title {{
            font-size: clamp(2.1rem, 4vw, 3.4rem);
            font-weight: 800;
            line-height: 1.05;
            margin: 0;
        }}

        .hero-copy {{
            max-width: 720px;
            font-size: 1rem;
            margin: 0.8rem 0 0;
            color: rgba(255, 255, 255, 0.88);
        }}

        .hero-typewriter {{
            display: inline-block;
            margin-top: 0.95rem;
            max-width: 100%;
            overflow: hidden;
            white-space: nowrap;
            color: rgba(255,255,255,0.95);
            font-size: 0.95rem;
            font-weight: 700;
            letter-spacing: 0.02em;
            animation: typing 2.4s steps(48, end);
        }}

        .premium-card {{
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 24px;
            padding: 1.1rem 1.2rem;
            box-shadow: var(--shadow);
            backdrop-filter: blur(24px);
            transition: transform 180ms ease, border-color 180ms ease, box-shadow 180ms ease;
        }}

        .premium-card:hover {{
            transform: translateY(-4px);
            border-color: rgba(255, 255, 255, 0.18);
            box-shadow: 0 22px 70px rgba(0, 0, 0, 0.16);
        }}

        .premium-card.glow {{
            position: relative;
            overflow: hidden;
        }}

        .premium-card.glow::before {{
            content: "";
            position: absolute;
            inset: -1px;
            background: linear-gradient(135deg, rgba(32, 199, 217, 0.22), transparent 36%, rgba(255, 159, 67, 0.18));
            opacity: 0.65;
            pointer-events: none;
        }}

        .stat-chip {{
            display: inline-flex;
            align-items: center;
            gap: 0.45rem;
            border-radius: 999px;
            padding: 0.35rem 0.75rem;
            background: rgba(255, 255, 255, 0.14);
            color: white;
            font-size: 0.82rem;
            margin-right: 0.5rem;
            margin-top: 0.6rem;
        }}

        .section-label {{
            text-transform: uppercase;
            letter-spacing: 0.12em;
            color: var(--muted);
            font-size: 0.74rem;
            margin-bottom: 0.45rem;
        }}

        .mini-card {{
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 22px;
            padding: 1rem;
            min-height: 110px;
            position: relative;
            overflow: hidden;
        }}

        .mini-card::after {{
            content: "";
            position: absolute;
            inset: 0;
            background: linear-gradient(120deg, transparent 0%, rgba(255,255,255,0.06) 38%, transparent 68%);
            transform: translateX(-120%);
            animation: shimmer 4.6s linear infinite;
            pointer-events: none;
        }}

        .mini-card h4 {{
            margin: 0 0 0.35rem;
            font-size: 0.85rem;
            color: var(--muted);
            font-weight: 600;
        }}

        .mini-card .value {{
            font-size: 1.55rem;
            font-weight: 800;
            color: var(--text);
        }}

        .mini-card .sub {{
            font-size: 0.86rem;
            color: var(--muted);
        }}

        .stTabs [data-baseweb="tab-list"] {{
            gap: 0.55rem;
            background: rgba(255, 255, 255, 0.04);
            border-radius: 18px;
            padding: 0.4rem;
            margin-bottom: 1rem;
        }}

        .stTabs [data-baseweb="tab"] {{
            border-radius: 14px;
            padding: 0.85rem 1rem;
            color: var(--muted);
            font-weight: 700;
        }}

        .stTabs [aria-selected="true"] {{
            background: rgba(255, 255, 255, 0.08) !important;
            color: var(--text) !important;
        }}

        .stButton > button, .stDownloadButton > button {{
            border-radius: 999px !important;
            border: 1px solid rgba(255, 255, 255, 0.12) !important;
            padding: 0.7rem 1.05rem !important;
            background: linear-gradient(135deg, rgba(33, 196, 143, 0.22), rgba(32, 199, 217, 0.18)) !important;
            color: var(--text) !important;
            font-weight: 700 !important;
            transition: transform 160ms ease, box-shadow 160ms ease !important;
        }}

        .stButton > button:hover, .stDownloadButton > button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 18px 42px rgba(0, 0, 0, 0.15);
        }}

        .insight-note {{
            padding: 0.9rem 1rem;
            border-radius: 18px;
            background: rgba(255, 255, 255, 0.06);
            border: 1px solid var(--border);
            color: var(--muted);
        }}

        .sidebar-brand {{
            border-radius: 24px;
            padding: 1rem 1rem 1.1rem;
            margin-bottom: 0.9rem;
            background: linear-gradient(145deg, rgba(12, 107, 118, 0.34), rgba(8, 20, 35, 0.72));
            border: 1px solid rgba(255, 255, 255, 0.08);
            box-shadow: 0 18px 55px rgba(0, 0, 0, 0.18);
        }}

        .sidebar-brand .eyebrow {{
            text-transform: uppercase;
            letter-spacing: 0.16em;
            font-size: 0.7rem;
            opacity: 0.72;
            margin-bottom: 0.45rem;
        }}

        .sidebar-brand .brand-title {{
            font-size: 1.25rem;
            font-weight: 800;
            line-height: 1.08;
            margin-bottom: 0.45rem;
        }}

        .sidebar-brand .brand-copy {{
            font-size: 0.84rem;
            line-height: 1.55;
            color: rgba(239, 247, 255, 0.76);
        }}

        .sidebar-meta {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 0.5rem;
            margin-top: 0.85rem;
        }}

        .sidebar-meta div {{
            border-radius: 14px;
            padding: 0.7rem;
            background: rgba(255, 255, 255, 0.06);
            border: 1px solid rgba(255, 255, 255, 0.06);
            font-size: 0.78rem;
        }}

        .sidebar-progress {{
            border-radius: 22px;
            padding: 0.95rem;
            margin-bottom: 0.95rem;
            background: rgba(255,255,255,0.05);
            border: 1px solid rgba(255,255,255,0.08);
        }}

        .sidebar-progress-top {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 0.7rem;
            margin-bottom: 0.7rem;
        }}

        .sidebar-progress-top strong {{
            font-size: 0.9rem;
            color: #ffffff;
        }}

        .sidebar-progress-top span {{
            font-size: 0.76rem;
            letter-spacing: 0.12em;
            text-transform: uppercase;
            color: rgba(239,247,255,0.72);
        }}

        .sidebar-progress-bar {{
            height: 10px;
            border-radius: 999px;
            background: rgba(255,255,255,0.10);
            overflow: hidden;
            margin-bottom: 0.85rem;
        }}

        .sidebar-progress-fill {{
            height: 100%;
            width: 0%;
            border-radius: 999px;
            background: linear-gradient(90deg, rgba(32, 199, 217, 0.95), rgba(33, 196, 143, 0.95), rgba(255, 159, 67, 0.95));
            animation: progressFlow 1s ease forwards;
        }}

        .sidebar-step-list {{
            display: grid;
            gap: 0.48rem;
            margin-bottom: 0.8rem;
        }}

        .sidebar-step {{
            display: flex;
            align-items: center;
            gap: 0.7rem;
            border-radius: 16px;
            padding: 0.72rem 0.78rem;
            background: rgba(255,255,255,0.05);
            border: 1px solid rgba(255,255,255,0.08);
        }}

        .sidebar-step .dot {{
            width: 12px;
            height: 12px;
            border-radius: 50%;
            flex: 0 0 12px;
            background: rgba(255,255,255,0.28);
            box-shadow: 0 0 0 6px rgba(255,255,255,0.03);
        }}

        .sidebar-step .text {{
            flex: 1;
            font-size: 0.82rem;
            line-height: 1.35;
            color: rgba(239,247,255,0.82);
        }}

        .sidebar-step.active {{
            border-color: rgba(255,255,255,0.20);
            background: rgba(255,255,255,0.10);
        }}

        .sidebar-step.active .dot {{
            background: rgba(255, 159, 67, 1);
        }}

        .sidebar-step.ready {{
            border-color: rgba(33, 196, 143, 0.30);
            background: rgba(33, 196, 143, 0.14);
        }}

        .sidebar-step.ready .dot {{
            background: rgba(33, 196, 143, 1);
        }}

        .sidebar-next {{
            border-radius: 16px;
            padding: 0.75rem 0.82rem;
            background: rgba(255,255,255,0.07);
            border: 1px solid rgba(255,255,255,0.08);
            font-size: 0.8rem;
            line-height: 1.45;
            color: rgba(239,247,255,0.86);
        }}

        .band-stack {{
            display: grid;
            gap: 0.8rem;
        }}

        .band-row {{
            display: flex;
            align-items: center;
            gap: 0.9rem;
            padding: 0.95rem 1rem;
            border-radius: 18px;
            background: rgba(255,255,255,0.05);
            border: 1px solid var(--border);
        }}

        .band-dot {{
            width: 14px;
            height: 14px;
            border-radius: 50%;
            flex: 0 0 14px;
            box-shadow: 0 0 0 8px rgba(255,255,255,0.03);
        }}

        .band-copy {{
            flex: 1;
        }}

        .band-copy strong {{
            display: block;
            color: var(--text);
            font-size: 0.95rem;
            margin-bottom: 0.15rem;
        }}

        .band-copy span {{
            color: var(--muted);
            font-size: 0.85rem;
            line-height: 1.45;
        }}

        .active-pill {{
            padding: 0.32rem 0.7rem;
            border-radius: 999px;
            background: rgba(255,255,255,0.1);
            font-size: 0.74rem;
            font-weight: 800;
            letter-spacing: 0.08em;
        }}

        .story-grid {{
            display: grid;
            grid-template-columns: repeat(2, minmax(0, 1fr));
            gap: 0.85rem;
        }}

        .story-tile {{
            border-radius: 18px;
            padding: 1rem;
            background: rgba(255,255,255,0.05);
            border: 1px solid var(--border);
        }}

        .story-tile .label {{
            color: var(--muted);
            font-size: 0.78rem;
            letter-spacing: 0.12em;
            text-transform: uppercase;
            margin-bottom: 0.45rem;
        }}

        .story-tile .big {{
            color: var(--text);
            font-size: 1.4rem;
            font-weight: 800;
            line-height: 1.1;
        }}

        .story-tile .small {{
            margin-top: 0.4rem;
            color: var(--muted);
            font-size: 0.84rem;
            line-height: 1.5;
        }}

        .plot-shell {{
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 22px;
            padding: 0.55rem 0.55rem 0.2rem;
            box-shadow: var(--shadow);
        }}

        @keyframes floatIn {{
            0% {{ opacity: 0; transform: translateY(24px) scale(0.98); }}
            100% {{ opacity: 1; transform: translateY(0) scale(1); }}
        }}

        @keyframes shimmer {{
            0% {{ transform: translateX(-120%); }}
            100% {{ transform: translateX(120%); }}
        }}

        @keyframes progressFlow {{
            from {{ width: 0%; }}
            to {{ width: var(--progress-width); }}
        }}

        @keyframes typing {{
            from {{ width: 0; }}
            to {{ width: 100%; }}
        }}

        @keyframes railSweep {{
            0% {{ transform: translateX(0); }}
            100% {{ transform: translateX(560%); }}
        }}

        @keyframes dialPulse {{
            0%, 100% {{ transform: scale(1); }}
            50% {{ transform: scale(1.03); }}
        }}

        @media (max-width: 1024px) {{
            .hero-grid {{
                grid-template-columns: 1fr;
            }}
            .story-grid {{
                grid-template-columns: 1fr;
            }}
            .hero-typewriter {{
                white-space: normal;
                border-right: 0;
                animation: none;
            }}
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )
