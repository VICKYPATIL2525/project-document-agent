"""
Streamlit Web Interface - Student Project Documentation Generator
Provides a user-friendly form for inputs and handles document generation.
"""
import os
import json
import time
import threading
import streamlit as st
from datetime import datetime
from pipeline import run_pipeline, get_tracker
from config import OUTPUT_DIR, TRACKING_DIR, MAX_PAGES, MIN_PAGES


# ─── Page Configuration ──────────────────────────────────────────────────────

st.set_page_config(
    page_title="DocForge — Project Report Generator",
    page_icon="📐",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ─── Custom CSS ───────────────────────────────────────────────────────────────

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=Geist+Mono:wght@300;400;500;600&family=Outfit:wght@200;300;400;500;600;700&display=swap');

    :root {
        --bg-primary: #f6f1eb;
        --bg-secondary: #ede7df;
        --bg-tertiary: #e4ddd3;
        --bg-card: #faf8f5;
        --bg-inset: #f0ebe4;
        --ink-primary: #1a1d2e;
        --ink-secondary: #3d4055;
        --ink-muted: #7d7f91;
        --ink-faint: #a8a9b8;
        --ink-ghost: #c8c9d4;
        --accent-primary: #2d5a8a;
        --accent-hover: #1e4570;
        --accent-light: #d4e3f3;
        --accent-wash: #eaf1f8;
        --stamp-red: #c0392b;
        --stamp-red-bg: rgba(192,57,43,0.06);
        --stamp-green: #1e7a4a;
        --stamp-green-bg: rgba(30,122,74,0.06);
        --stamp-amber: #b37e2a;
        --stamp-amber-bg: rgba(179,126,42,0.06);
        --grid-line: rgba(45,90,138,0.06);
        --border-light: rgba(26,29,46,0.08);
        --border-medium: rgba(26,29,46,0.13);
        --border-strong: rgba(26,29,46,0.22);
        --shadow-sm: 0 1px 3px rgba(26,29,46,0.05), 0 1px 2px rgba(26,29,46,0.03);
        --shadow-md: 0 4px 12px rgba(26,29,46,0.06), 0 2px 4px rgba(26,29,46,0.04);
        --shadow-lg: 0 12px 36px rgba(26,29,46,0.08), 0 4px 12px rgba(26,29,46,0.04);
        --radius-sm: 3px;
        --radius-md: 6px;
        --radius-lg: 10px;
    }

    /* ── Global ── */
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
        -webkit-font-smoothing: antialiased;
    }

    .stApp {
        background-color: var(--bg-primary);
        background-image:
            linear-gradient(var(--grid-line) 1px, transparent 1px),
            linear-gradient(90deg, var(--grid-line) 1px, transparent 1px);
        background-size: 28px 28px;
        color: var(--ink-primary);
    }

    /* ── Hide Streamlit Branding ── */
    #MainMenu, footer, header { visibility: hidden; }
    .stDeployButton { display: none; }

    /* ── Sidebar ── */
    [data-testid="stSidebar"] {
        background: var(--bg-card) !important;
        border-right: 2px solid var(--border-medium) !important;
        box-shadow: 4px 0 20px rgba(26,29,46,0.04) !important;
    }
    [data-testid="stSidebar"] * {
        color: var(--ink-secondary) !important;
    }
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] strong {
        color: var(--ink-primary) !important;
        font-family: 'Instrument Serif', serif !important;
    }
    [data-testid="stSidebar"] .stMarkdown p {
        font-size: 0.82rem;
        line-height: 1.7;
    }

    /* ── Hero Header ── */
    .hero-wrap {
        position: relative;
        padding: 3rem 2.8rem 2.5rem;
        margin-bottom: 2rem;
        background: var(--bg-card);
        border: 2px solid var(--border-medium);
        border-radius: var(--radius-md);
        box-shadow: var(--shadow-md);
        overflow: hidden;
    }
    .hero-wrap::before {
        content: '';
        position: absolute;
        top: 0; left: 0;
        width: 100%; height: 4px;
        background: linear-gradient(90deg, var(--accent-primary) 0%, var(--accent-primary) 35%, transparent 35%, transparent 37%, var(--stamp-red) 37%, var(--stamp-red) 100%);
    }
    .hero-wrap::after {
        content: 'DOCFORGE';
        position: absolute;
        top: 28px; right: 32px;
        font-family: 'Geist Mono', monospace;
        font-size: 0.55rem;
        letter-spacing: 0.35em;
        color: var(--ink-ghost);
        writing-mode: horizontal-tb;
    }
    .hero-eyebrow {
        font-family: 'Geist Mono', monospace;
        font-size: 0.62rem;
        letter-spacing: 0.22em;
        color: var(--accent-primary);
        text-transform: uppercase;
        margin-bottom: 0.8rem;
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.3rem 0.7rem;
        background: var(--accent-wash);
        border: 1px solid var(--accent-light);
        border-radius: 2px;
    }
    .hero-title {
        font-family: 'Instrument Serif', serif;
        font-size: 3rem;
        font-weight: 400;
        color: var(--ink-primary);
        line-height: 1.08;
        letter-spacing: -0.025em;
        margin-bottom: 0.8rem;
    }
    .hero-title em {
        font-style: italic;
        color: var(--accent-primary);
    }
    .hero-subtitle {
        font-family: 'Outfit', sans-serif;
        font-size: 0.92rem;
        color: var(--ink-muted);
        font-weight: 300;
        max-width: 580px;
        line-height: 1.65;
    }
    .hero-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        margin-top: 1.5rem;
        padding: 0.4rem 0.85rem;
        background: var(--bg-inset);
        border: 1.5px solid var(--border-medium);
        border-radius: 2px;
        font-family: 'Geist Mono', monospace;
        font-size: 0.6rem;
        color: var(--ink-muted);
        letter-spacing: 0.08em;
    }
    .hero-badge-dot {
        width: 6px; height: 6px;
        background: var(--stamp-green);
        border-radius: 50%;
        animation: beacon 2.5s ease-in-out infinite;
    }
    @keyframes beacon {
        0%, 100% { opacity: 1; transform: scale(1); }
        50% { opacity: 0.4; transform: scale(0.85); }
    }

    /* ── Section Labels ── */
    .section-label {
        font-family: 'Geist Mono', monospace;
        font-size: 0.58rem;
        letter-spacing: 0.2em;
        color: var(--accent-primary);
        text-transform: uppercase;
        margin-bottom: 0.8rem;
        padding-bottom: 0.5rem;
        border-bottom: 1.5px solid var(--border-light);
        display: flex;
        align-items: center;
        gap: 0.6rem;
    }
    .section-label::before {
        content: '';
        width: 8px; height: 8px;
        border: 1.5px solid var(--accent-primary);
        border-radius: 1px;
        transform: rotate(45deg);
        flex-shrink: 0;
    }

    /* ── Card Containers ── */
    .card {
        background: var(--bg-card);
        border: 1.5px solid var(--border-medium);
        border-radius: var(--radius-md);
        padding: 1.5rem;
        margin-bottom: 1rem;
        position: relative;
        box-shadow: var(--shadow-sm);
    }
    .card::before {
        content: '';
        position: absolute;
        top: -1.5px; left: 16px; right: 16px;
        height: 3px;
        background: var(--accent-primary);
        border-radius: 0 0 2px 2px;
    }
    .card-title {
        font-family: 'Instrument Serif', serif;
        font-size: 1rem;
        color: var(--ink-primary);
        margin-bottom: 0.3rem;
        font-weight: 400;
    }
    .card-desc {
        font-size: 0.78rem;
        color: var(--ink-muted);
        margin-bottom: 1rem;
    }

    /* ── Input Overrides ── */
    .stTextInput input,
    .stTextArea textarea,
    .stSelectbox select {
        background-color: var(--bg-card) !important;
        border: 1.5px solid var(--border-medium) !important;
        border-radius: var(--radius-sm) !important;
        color: var(--ink-primary) !important;
        font-family: 'Outfit', sans-serif !important;
        font-size: 0.88rem !important;
        font-weight: 400 !important;
        transition: border-color 0.2s, box-shadow 0.2s !important;
    }
    .stTextInput input:focus,
    .stTextArea textarea:focus {
        border-color: var(--accent-primary) !important;
        box-shadow: 0 0 0 3px rgba(45,90,138,0.1) !important;
    }
    .stTextInput input::placeholder,
    .stTextArea textarea::placeholder {
        color: var(--ink-ghost) !important;
        font-weight: 300 !important;
    }
    .stTextInput label,
    .stTextArea label,
    .stSlider label,
    .stRadio label,
    .stFileUploader label {
        color: var(--ink-secondary) !important;
        font-size: 0.8rem !important;
        font-weight: 500 !important;
        letter-spacing: 0.02em !important;
        font-family: 'Outfit', sans-serif !important;
    }

    /* ── Slider ── */
    .stSlider [data-baseweb="slider"] {
        padding-top: 0.5rem !important;
    }
    .stSlider [data-testid="stTickBarMin"],
    .stSlider [data-testid="stTickBarMax"] {
        color: var(--ink-muted) !important;
        font-size: 0.75rem !important;
        font-family: 'Geist Mono', monospace !important;
    }
    .stSlider [data-baseweb="slider"] [role="slider"] {
        background: var(--accent-primary) !important;
        border-color: var(--accent-primary) !important;
    }

    /* ── Tabs ── */
    .stTabs [data-baseweb="tab-list"] {
        background: transparent !important;
        border-bottom: 2px solid var(--border-light) !important;
        gap: 0 !important;
    }
    .stTabs [data-baseweb="tab"] {
        background: transparent !important;
        border: none !important;
        color: var(--ink-muted) !important;
        font-family: 'Geist Mono', monospace !important;
        font-size: 0.72rem !important;
        font-weight: 500 !important;
        padding: 0.7rem 1.3rem !important;
        letter-spacing: 0.1em !important;
        text-transform: uppercase !important;
        border-bottom: 2.5px solid transparent !important;
        transition: all 0.2s !important;
    }
    .stTabs [aria-selected="true"] {
        color: var(--accent-primary) !important;
        border-bottom: 2.5px solid var(--accent-primary) !important;
    }
    .stTabs [data-baseweb="tab"]:hover {
        color: var(--ink-secondary) !important;
    }
    .stTabs [data-baseweb="tab-panel"] {
        padding-top: 1.5rem !important;
    }

    /* ── Primary Button ── */
    .stButton > button[kind="primary"],
    .stButton > button {
        background: var(--accent-primary) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: var(--radius-sm) !important;
        font-family: 'Outfit', sans-serif !important;
        font-weight: 600 !important;
        font-size: 0.88rem !important;
        letter-spacing: 0.03em !important;
        padding: 0.7rem 1.6rem !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 2px 8px rgba(45,90,138,0.2), inset 0 1px 0 rgba(255,255,255,0.1) !important;
        position: relative !important;
        overflow: hidden !important;
    }
    .stButton > button:hover {
        background: var(--accent-hover) !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 16px rgba(45,90,138,0.25), inset 0 1px 0 rgba(255,255,255,0.1) !important;
    }
    .stButton > button:active {
        transform: translateY(0) !important;
    }
    .stButton > button[kind="secondary"] {
        background: transparent !important;
        color: var(--ink-secondary) !important;
        border: 1.5px solid var(--border-medium) !important;
        box-shadow: none !important;
    }
    .stButton > button[kind="secondary"]:hover {
        border-color: var(--accent-primary) !important;
        color: var(--accent-primary) !important;
        background: var(--accent-wash) !important;
    }

    /* ── Download Button ── */
    .stDownloadButton > button {
        background: var(--accent-primary) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: var(--radius-sm) !important;
        font-family: 'Outfit', sans-serif !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        letter-spacing: 0.03em !important;
        padding: 0.85rem 2rem !important;
        box-shadow: 0 4px 16px rgba(45,90,138,0.2), inset 0 1px 0 rgba(255,255,255,0.1) !important;
        transition: all 0.2s ease !important;
    }
    .stDownloadButton > button:hover {
        background: var(--accent-hover) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 28px rgba(45,90,138,0.25) !important;
    }

    /* ── Toggle ── */
    .stCheckbox, .stToggle {
        color: var(--ink-secondary) !important;
    }

    /* ── Radio ── */
    .stRadio [data-testid="stMarkdownContainer"] p {
        color: var(--ink-secondary) !important;
        font-size: 0.85rem !important;
    }

    /* ── Metrics ── */
    [data-testid="metric-container"] {
        background: var(--bg-card) !important;
        border: 1.5px solid var(--border-medium) !important;
        border-radius: var(--radius-md) !important;
        padding: 1.1rem !important;
        box-shadow: var(--shadow-sm) !important;
        position: relative !important;
        overflow: hidden !important;
    }
    [data-testid="metric-container"]::before {
        content: '' !important;
        position: absolute !important;
        top: 0; left: 0; right: 0 !important;
        height: 2.5px !important;
        background: var(--accent-primary) !important;
    }
    [data-testid="metric-container"] label {
        color: var(--ink-muted) !important;
        font-family: 'Geist Mono', monospace !important;
        font-size: 0.6rem !important;
        letter-spacing: 0.12em !important;
        text-transform: uppercase !important;
    }
    [data-testid="metric-container"] [data-testid="stMetricValue"] {
        color: var(--ink-primary) !important;
        font-family: 'Instrument Serif', serif !important;
        font-size: 1.6rem !important;
        font-weight: 400 !important;
    }

    /* ── Progress Bar ── */
    .stProgress > div > div > div {
        background: linear-gradient(90deg, var(--accent-primary) 0%, #4a8bc2 100%) !important;
        border-radius: 2px !important;
    }
    .stProgress > div > div {
        background: var(--bg-tertiary) !important;
        border-radius: 2px !important;
        height: 5px !important;
    }

    /* ── Code Block ── */
    .stCode, [data-testid="stCode"] {
        background: var(--ink-primary) !important;
        border: 1.5px solid var(--border-strong) !important;
        border-radius: var(--radius-sm) !important;
        font-family: 'Geist Mono', monospace !important;
        font-size: 0.73rem !important;
    }

    /* ── Expander ── */
    .streamlit-expanderHeader {
        background: var(--bg-card) !important;
        border: 1.5px solid var(--border-medium) !important;
        border-radius: var(--radius-sm) !important;
        color: var(--ink-secondary) !important;
        font-size: 0.82rem !important;
        font-family: 'Outfit', sans-serif !important;
        font-weight: 500 !important;
    }
    .streamlit-expanderHeader:hover {
        border-color: var(--accent-primary) !important;
        color: var(--accent-primary) !important;
    }
    .streamlit-expanderContent {
        background: var(--bg-card) !important;
        border: 1.5px solid var(--border-medium) !important;
        border-top: none !important;
    }

    /* ── Alert / Success / Error ── */
    .stSuccess {
        background: var(--stamp-green-bg) !important;
        border: 1.5px solid rgba(30,122,74,0.2) !important;
        border-radius: var(--radius-sm) !important;
        color: var(--stamp-green) !important;
    }
    .stError {
        background: var(--stamp-red-bg) !important;
        border: 1.5px solid rgba(192,57,43,0.2) !important;
        border-radius: var(--radius-sm) !important;
        color: var(--stamp-red) !important;
    }
    .stInfo {
        background: var(--accent-wash) !important;
        border: 1.5px solid var(--accent-light) !important;
        border-radius: var(--radius-sm) !important;
        color: var(--ink-secondary) !important;
    }
    .stWarning {
        background: var(--stamp-amber-bg) !important;
        border: 1.5px solid rgba(179,126,42,0.2) !important;
        color: var(--stamp-amber) !important;
    }

    /* ── Divider ── */
    hr {
        border: none !important;
        border-top: 1.5px solid var(--border-light) !important;
        margin: 1.5rem 0 !important;
    }

    /* ── Custom Components ── */
    .stat-row {
        display: flex;
        gap: 1rem;
        margin: 1rem 0;
    }
    .stat-box {
        flex: 1;
        background: var(--bg-card);
        border: 1.5px solid var(--border-medium);
        border-radius: var(--radius-md);
        padding: 1rem;
        text-align: center;
        box-shadow: var(--shadow-sm);
        position: relative;
    }
    .stat-box::before {
        content: '';
        position: absolute;
        top: 0; left: 14px; right: 14px;
        height: 2.5px;
        background: var(--accent-primary);
        border-radius: 0 0 2px 2px;
    }
    .stat-label {
        font-family: 'Geist Mono', monospace;
        font-size: 0.58rem;
        color: var(--ink-muted);
        letter-spacing: 0.14em;
        text-transform: uppercase;
        margin-bottom: 0.35rem;
    }
    .stat-value {
        font-family: 'Instrument Serif', serif;
        font-size: 1.5rem;
        color: var(--ink-primary);
        font-weight: 400;
    }

    .step-row {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        padding: 0.65rem 0.9rem;
        border-radius: var(--radius-sm);
        margin: 0.3rem 0;
        font-size: 0.8rem;
        font-family: 'Outfit', sans-serif;
    }
    .step-completed {
        background: var(--stamp-green-bg);
        border: 1.5px solid rgba(30,122,74,0.15);
        color: var(--stamp-green);
    }
    .step-failed {
        background: var(--stamp-red-bg);
        border: 1.5px solid rgba(192,57,43,0.15);
        color: var(--stamp-red);
    }
    .step-running {
        background: var(--accent-wash);
        border: 1.5px solid var(--accent-light);
        color: var(--accent-primary);
    }
    .step-icon {
        font-size: 0.8rem;
        min-width: 18px;
        font-weight: 600;
    }
    .step-name {
        font-weight: 500;
        flex: 1;
    }
    .step-meta {
        font-family: 'Geist Mono', monospace;
        font-size: 0.62rem;
        opacity: 0.65;
    }

    .success-banner {
        background: var(--bg-card);
        border: 2px solid rgba(30,122,74,0.25);
        border-radius: var(--radius-md);
        padding: 2rem 2rem 1.5rem;
        margin-bottom: 1.5rem;
        position: relative;
        overflow: hidden;
        box-shadow: var(--shadow-md);
    }
    .success-banner::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 4px;
        background: linear-gradient(90deg, var(--stamp-green) 0%, #2ecc71 100%);
    }
    .success-banner::after {
        content: 'COMPLETE';
        position: absolute;
        top: 16px; right: 20px;
        font-family: 'Geist Mono', monospace;
        font-size: 0.5rem;
        letter-spacing: 0.3em;
        color: var(--stamp-green);
        opacity: 0.5;
        border: 1px solid rgba(30,122,74,0.2);
        padding: 0.15rem 0.5rem;
        border-radius: 1px;
    }
    .success-banner-title {
        font-family: 'Instrument Serif', serif;
        font-size: 1.5rem;
        color: var(--stamp-green);
        font-weight: 400;
        margin-bottom: 0.3rem;
    }
    .success-banner-sub {
        font-size: 0.82rem;
        color: var(--ink-muted);
    }

    .progress-wrap {
        background: var(--bg-card);
        border: 1.5px solid var(--border-medium);
        border-radius: var(--radius-md);
        padding: 2rem;
        margin-bottom: 1.5rem;
        position: relative;
        box-shadow: var(--shadow-md);
        overflow: hidden;
    }
    .progress-wrap::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 3px;
        background: linear-gradient(90deg, var(--accent-primary), #6da1d4, var(--accent-primary));
        background-size: 200% 100%;
        animation: shimmer 2s linear infinite;
    }
    @keyframes shimmer {
        0% { background-position: -200% 0; }
        100% { background-position: 200% 0; }
    }
    .progress-title {
        font-family: 'Instrument Serif', serif;
        font-size: 1.4rem;
        color: var(--ink-primary);
        margin-bottom: 0.3rem;
    }
    .progress-sub {
        font-size: 0.75rem;
        color: var(--ink-muted);
        margin-bottom: 1.5rem;
        font-family: 'Geist Mono', monospace;
    }

    .console-header {
        font-family: 'Geist Mono', monospace;
        font-size: 0.62rem;
        letter-spacing: 0.14em;
        color: var(--ink-muted);
        text-transform: uppercase;
        margin-bottom: 0.5rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.4rem 0;
        border-bottom: 1px solid var(--border-light);
    }
    .console-dot { width: 7px; height: 7px; border-radius: 50%; }
    .dot-red { background: var(--stamp-red); }
    .dot-yellow { background: var(--stamp-amber); }
    .dot-green { background: var(--stamp-green); }

    .prev-job-item {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.4rem 0.6rem;
        border-radius: var(--radius-sm);
        font-size: 0.72rem;
        font-family: 'Geist Mono', monospace;
        color: var(--ink-muted) !important;
        border: 1px solid transparent;
        margin: 0.2rem 0;
        transition: all 0.15s;
    }
    .prev-job-item:hover {
        background: var(--bg-inset);
        color: var(--ink-secondary) !important;
        border-color: var(--border-light);
    }
    .job-dot { width: 6px; height: 6px; border-radius: 50%; }
    .job-completed { background: var(--stamp-green); }
    .job-failed { background: var(--stamp-red); }
    .job-running { background: var(--accent-primary); animation: beacon 2.5s infinite; }

    .capability-item {
        display: flex;
        align-items: center;
        gap: 0.55rem;
        padding: 0.35rem 0;
        font-size: 0.78rem;
        color: var(--ink-muted) !important;
        border-bottom: 1px dashed var(--border-light);
    }
    .capability-item:last-child { border-bottom: none; }
    .cap-check {
        color: var(--accent-primary);
        font-size: 0.55rem;
        min-width: 14px;
        font-family: 'Geist Mono', monospace;
    }

    .how-step {
        display: flex;
        gap: 0.75rem;
        padding: 0.5rem 0;
        align-items: flex-start;
        border-bottom: 1px dashed var(--border-light);
    }
    .how-step:last-child { border-bottom: none; }
    .how-num {
        font-family: 'Instrument Serif', serif;
        font-size: 1.05rem;
        color: var(--accent-primary);
        font-weight: 400;
        min-width: 20px;
        font-style: italic;
    }
    .how-text {
        font-size: 0.77rem;
        color: var(--ink-muted) !important;
        line-height: 1.5;
    }

    /* ── File Uploader ── */
    [data-testid="stFileUploader"] {
        background: var(--bg-card) !important;
        border: 1.5px dashed var(--border-medium) !important;
        border-radius: var(--radius-sm) !important;
    }
    [data-testid="stFileUploader"]:hover {
        border-color: var(--accent-primary) !important;
    }

    /* ── Scrollbar ── */
    ::-webkit-scrollbar { width: 5px; height: 5px; }
    ::-webkit-scrollbar-track { background: var(--bg-primary); }
    ::-webkit-scrollbar-thumb { background: var(--border-medium); border-radius: 3px; }
    ::-webkit-scrollbar-thumb:hover { background: var(--accent-primary); }

    /* ── Sidebar Section Headers ── */
    .sidebar-section-title {
        font-family: 'Geist Mono', monospace;
        font-size: 0.56rem;
        letter-spacing: 0.2em;
        color: var(--ink-ghost);
        text-transform: uppercase;
        margin-bottom: 0.75rem;
        padding-bottom: 0.35rem;
        border-bottom: 1px solid var(--border-light);
    }

    /* ── Sidebar Brand ── */
    .sidebar-brand {
        padding: 0.8rem 0 0.5rem;
    }
    .sidebar-brand-name {
        font-family: 'Instrument Serif', serif;
        font-size: 1.4rem;
        color: var(--ink-primary);
        font-weight: 400;
        letter-spacing: -0.02em;
    }
    .sidebar-brand-name em {
        font-style: italic;
        color: var(--accent-primary);
    }
    .sidebar-brand-version {
        font-family: 'Geist Mono', monospace;
        font-size: 0.53rem;
        color: var(--ink-ghost);
        letter-spacing: 0.18em;
        text-transform: uppercase;
        margin-top: 0.15rem;
    }
    .sidebar-divider {
        border: none;
        border-top: 1px solid var(--border-light);
        margin: 0.75rem 0 1rem;
    }
    .sidebar-footer {
        margin-top: 2rem;
        padding-top: 1rem;
        border-top: 1px solid var(--border-light);
        text-align: center;
    }
    .sidebar-footer-text {
        font-family: 'Geist Mono', monospace;
        font-size: 0.53rem;
        color: var(--ink-ghost);
        line-height: 1.7;
        letter-spacing: 0.05em;
    }
</style>
""", unsafe_allow_html=True)


# ─── Session State Init ──────────────────────────────────────────────────────

if "generation_started" not in st.session_state:
    st.session_state.generation_started = False
if "result" not in st.session_state:
    st.session_state.result = None
if "job_id" not in st.session_state:
    st.session_state.job_id = None


# ─── Test Data (auto-fill) ────────────────────────────────────────────────────

_TEST_DATA = {
    "project_title": "Smart Attendance System using Face Recognition",
    "tech_stack": "Python, OpenCV, Flask, SQLite, HTML/CSS, JavaScript",
    "target_pages": 60,
    "project_summary": (
        "The Smart Attendance System is an AI-powered application that automates "
        "student attendance tracking using real-time face recognition. The system "
        "captures live video from a webcam, detects faces using Haar Cascade classifiers, "
        "and recognizes students by comparing facial embeddings generated with the "
        "dlib/face_recognition library against a pre-enrolled database stored in SQLite. "
        "Once a student is identified, their attendance is automatically logged with "
        "a timestamp. The backend is built with Flask and exposes REST APIs for "
        "enrollment, attendance retrieval, and report generation. The frontend is a "
        "responsive web dashboard built with HTML, CSS, and JavaScript that allows "
        "teachers to view attendance records, generate class-wise and date-wise reports, "
        "and export data as CSV/PDF. Key modules include: Face Detection Module, "
        "Face Recognition & Encoding Module, Attendance Logger, Admin Dashboard, "
        "and Report Generator. The system solves the problem of proxy attendance and "
        "manual errors in traditional roll-call methods, improving accuracy and saving time."
    ),
    "additional_info": (
        "Database schema: students(id, name, roll_no, department, face_encoding), "
        "attendance(id, student_id, timestamp, status). "
        "API endpoints: POST /enroll, GET /attendance, GET /report. "
        "Uses face_recognition library with 128-dimensional encodings. "
        "Threshold for match: 0.6 Euclidean distance."
    ),
    "project_code": (
        '# app.py - Main Flask Application\n'
        'from flask import Flask, render_template, request, jsonify\n'
        'import face_recognition, cv2, sqlite3, os\n'
        'from datetime import datetime\n\n'
        'app = Flask(__name__)\n\n'
        'def get_db():\n'
        '    conn = sqlite3.connect("attendance.db")\n'
        '    return conn\n\n'
        '@app.route("/")\n'
        'def index():\n'
        '    return render_template("dashboard.html")\n\n'
        '@app.route("/enroll", methods=["POST"])\n'
        'def enroll_student():\n'
        '    name = request.form["name"]\n'
        '    roll_no = request.form["roll_no"]\n'
        '    image = request.files["photo"]\n'
        '    img = face_recognition.load_image_file(image)\n'
        '    encoding = face_recognition.face_encodings(img)[0]\n'
        '    db = get_db()\n'
        '    db.execute("INSERT INTO students (name, roll_no, face_encoding) VALUES (?, ?, ?)",\n'
        '              (name, roll_no, encoding.tobytes()))\n'
        '    db.commit()\n'
        '    return jsonify({"status": "enrolled"})\n\n'
        '@app.route("/mark_attendance")\n'
        'def mark_attendance():\n'
        '    cap = cv2.VideoCapture(0)\n'
        '    ret, frame = cap.read()\n'
        '    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)\n'
        '    face_locations = face_recognition.face_locations(rgb)\n'
        '    face_encs = face_recognition.face_encodings(rgb, face_locations)\n'
        '    # Compare with enrolled students...\n'
        '    cap.release()\n'
        '    return jsonify({"marked": len(face_encs)})\n'
    ),
    "college_format": "",
    "student_name": "Rahul Sharma",
    "roll_number": "CS-2022-042",
    "college_name": "Mumbai Institute of Technology",
    "department": "Department of Computer Science & Engineering",
    "guide_name": "Prof. Anita Deshmukh",
    "year": "2025-2026",
}


# ─── Sidebar ──────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("""
    <div class="sidebar-brand">
        <div class="sidebar-brand-name">Doc<em>Forge</em></div>
        <div class="sidebar-brand-version">v2.0 &middot; Anthropic Claude</div>
    </div>
    <hr class="sidebar-divider">
    """, unsafe_allow_html=True)

    test_mode = st.toggle("Quick Test Mode", value=False, help="Auto-fill all fields with sample project data")

    st.markdown("<hr class='sidebar-divider'>", unsafe_allow_html=True)

    st.markdown("""
    <div class="sidebar-section-title">How It Works</div>
    <div class="how-step"><div class="how-num">1</div><div class="how-text">Fill in your project details and tech stack</div></div>
    <div class="how-step"><div class="how-num">2</div><div class="how-text">Paste or upload source code (optional)</div></div>
    <div class="how-step"><div class="how-num">3</div><div class="how-text">Set target page count (10 – 250)</div></div>
    <div class="how-step"><div class="how-num">4</div><div class="how-text">Click Generate and monitor live logs</div></div>
    <div class="how-step"><div class="how-num">5</div><div class="how-text">Download your formatted .docx report</div></div>
    """, unsafe_allow_html=True)

    st.markdown("<hr class='sidebar-divider'>", unsafe_allow_html=True)

    st.markdown("""
    <div class="sidebar-section-title">Capabilities</div>
    <div class="capability-item"><span class="cap-check">//</span> Up to 250 pages output</div>
    <div class="capability-item"><span class="cap-check">//</span> Professional academic formatting</div>
    <div class="capability-item"><span class="cap-check">//</span> Parallel chapter generation (12x)</div>
    <div class="capability-item"><span class="cap-check">//</span> Auto word-count calibration</div>
    <div class="capability-item"><span class="cap-check">//</span> Code blocks &amp; diagram placeholders</div>
    <div class="capability-item"><span class="cap-check">//</span> Auto Table of Contents</div>
    <div class="capability-item"><span class="cap-check">//</span> IEEE-format references</div>
    <div class="capability-item"><span class="cap-check">//</span> Title &amp; Certificate pages</div>
    """, unsafe_allow_html=True)

    st.markdown("<hr class='sidebar-divider'>", unsafe_allow_html=True)

    st.markdown("""
    <div class="sidebar-section-title">Recent Jobs</div>
    """, unsafe_allow_html=True)

    if os.path.exists(TRACKING_DIR):
        tracking_files = sorted(
            [f for f in os.listdir(TRACKING_DIR) if f.endswith(".json")],
            reverse=True,
        )[:5]
        if tracking_files:
            for tf in tracking_files:
                try:
                    with open(os.path.join(TRACKING_DIR, tf), "r") as f:
                        data = json.load(f)
                    status = data.get("status", "unknown")
                    dot_class = "job-completed" if status == "completed" else "job-failed" if status == "failed" else "job-running"
                    short_id = data['job_id'].replace("doc_", "")
                    st.markdown(
                        f'<div class="prev-job-item"><span class="job-dot {dot_class}"></span>{short_id}</div>',
                        unsafe_allow_html=True,
                    )
                except Exception:
                    pass
        else:
            st.markdown('<div style="font-size:0.73rem; color:var(--ink-ghost); font-family:Geist Mono,monospace;">No jobs yet</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div style="font-size:0.73rem; color:var(--ink-ghost); font-family:Geist Mono,monospace;">No jobs yet</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="sidebar-footer">
        <div class="sidebar-footer-text">
            Powered by Claude Sonnet + Haiku<br>via Anthropic API
        </div>
    </div>
    """, unsafe_allow_html=True)


# ─── Main Form ────────────────────────────────────────────────────────────────

if not st.session_state.generation_started:

    # Hero
    st.markdown("""
    <div class="hero-wrap">
        <div class="hero-eyebrow">AI-Powered Academic Documentation</div>
        <div class="hero-title">Generate your<br>Project <em>Report</em></div>
        <div class="hero-subtitle">
            Transform your project details into a fully formatted Black Book, Synopsis,
            or Thesis in minutes — with chapters, diagrams, IEEE references, and more.
        </div>
        <div class="hero-badge">
            <div class="hero-badge-dot"></div>
            Claude Sonnet &middot; Claude Haiku &middot; LangGraph Pipeline
        </div>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["PROJECT DETAILS", "STUDENT & COLLEGE INFO"])

    with tab1:

        # Row 1: Title + Tech
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('<div class="section-label">01 — Project Identity</div>', unsafe_allow_html=True)
            project_title = st.text_input(
                "Project Title *",
                value=_TEST_DATA["project_title"] if test_mode else "",
                placeholder="e.g., Online Examination System using MERN Stack",
            )
            tech_stack = st.text_input(
                "Technology Stack *",
                value=_TEST_DATA["tech_stack"] if test_mode else "",
                placeholder="e.g., React, Node.js, MongoDB, Express.js",
            )
            target_pages = st.slider(
                "Target Page Count",
                min_value=MIN_PAGES,
                max_value=MAX_PAGES,
                value=_TEST_DATA["target_pages"] if test_mode else 60,
                step=5,
                help="Total pages including title, certificate, TOC, chapters, and references",
            )

        with col2:
            st.markdown('<div class="section-label">02 — Project Description</div>', unsafe_allow_html=True)
            project_summary = st.text_area(
                "Project Summary / Description *",
                value=_TEST_DATA["project_summary"] if test_mode else "",
                placeholder="Describe your project in detail: what it does, features, modules, how it works, problem it solves. The more detail, the better the output.",
                height=215,
            )

        st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
        st.markdown('<div class="section-label">03 — Additional Context</div>', unsafe_allow_html=True)
        additional_info = st.text_area(
            "Additional Information (optional)",
            value=_TEST_DATA["additional_info"] if test_mode else "",
            placeholder="DB schema, API endpoints, specific requirements, methodologies, datasets used, etc.",
            height=90,
        )

        st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
        st.markdown('<div class="section-label">04 — Source Code</div>', unsafe_allow_html=True)

        code_upload_method = st.radio(
            "Provide code via",
            ["Paste Code", "Upload File", "No Code"],
            horizontal=True,
        )

        project_code = ""
        if code_upload_method == "Paste Code":
            project_code = st.text_area(
                "Paste your main source code",
                value=_TEST_DATA["project_code"] if test_mode else "",
                placeholder="Paste your important source code files here...",
                height=240,
            )
        elif code_upload_method == "Upload File":
            uploaded_files = st.file_uploader(
                "Upload source files",
                type=["py", "js", "ts", "java", "cpp", "c", "html", "css", "jsx", "tsx", "php", "rb", "go", "rs", "kt"],
                accept_multiple_files=True,
            )
            if uploaded_files:
                code_parts = []
                for uf in uploaded_files:
                    content = uf.read().decode("utf-8", errors="ignore")
                    code_parts.append(f"// ===== File: {uf.name} =====\n{content}\n")
                project_code = "\n".join(code_parts)
                st.success(f"{len(uploaded_files)} file(s) loaded successfully")

        st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
        st.markdown('<div class="section-label">05 — College Format</div>', unsafe_allow_html=True)
        college_format = st.text_area(
            "College Format Template (optional)",
            value=_TEST_DATA["college_format"] if test_mode else "",
            placeholder="Paste your college's required document structure if any — e.g., Chapter 1 must be Introduction with sections 1.1 Background...",
            height=80,
        )

    with tab2:
        st.markdown('<div class="section-label">Student Information</div>', unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        with col1:
            student_name = st.text_input("Student Name", value=_TEST_DATA["student_name"] if test_mode else "Student Name")
            roll_number = st.text_input("Roll Number", value=_TEST_DATA["roll_number"] if test_mode else "000")
        with col2:
            college_name = st.text_input("College / University", value=_TEST_DATA["college_name"] if test_mode else "University")
            department = st.text_input("Department", value=_TEST_DATA["department"] if test_mode else "Department of Computer Science")
        with col3:
            guide_name = st.text_input("Guide / Mentor Name", value=_TEST_DATA["guide_name"] if test_mode else "Prof. Guide")
            year = st.text_input("Academic Year", value=_TEST_DATA["year"] if test_mode else "2025-2026")

    st.markdown("<hr>", unsafe_allow_html=True)

    col_l, col_m, col_r = st.columns([1.5, 2, 1.5])
    with col_m:
        if st.button("Generate Documentation", type="primary", use_container_width=True):
            if not project_title:
                st.error("Project title is required.")
            elif not project_summary:
                st.error("Project summary is required.")
            elif not tech_stack:
                st.error("Technology stack is required.")
            elif len(project_summary.split()) < 20:
                st.error("Please provide a more detailed project summary (at least 20 words).")
            else:
                st.session_state.generation_started = True
                st.session_state.inputs = {
                    "project_title": project_title,
                    "project_summary": project_summary,
                    "project_code": project_code,
                    "tech_stack": tech_stack,
                    "target_pages": target_pages,
                    "college_format": college_format,
                    "additional_info": additional_info,
                    "student_name": student_name,
                    "roll_number": roll_number,
                    "college_name": college_name,
                    "department": department,
                    "guide_name": guide_name,
                    "year": year,
                }
                st.rerun()


# ─── Generation in Progress ──────────────────────────────────────────────────

else:
    if st.session_state.result is None:

        inputs = st.session_state.inputs

        st.markdown(f"""
        <div class="progress-wrap">
            <div class="progress-title">Generating your report...</div>
            <div class="progress-sub">
                {inputs['project_title']} &nbsp;&middot;&nbsp; {inputs['target_pages']} pages &nbsp;&middot;&nbsp; {len(inputs['project_summary'].split())} words of context
            </div>
        </div>
        """, unsafe_allow_html=True)

        progress_bar = st.progress(0, text="Initialising pipeline...")

        st.markdown("""
        <div class="console-header">
            <span class="console-dot dot-red"></span>
            <span class="console-dot dot-yellow"></span>
            <span class="console-dot dot-green"></span>
            &nbsp;Live Output
        </div>
        """, unsafe_allow_html=True)
        log_container = st.empty()

        pipeline_result = [None]
        pipeline_error = [None]

        def _run():
            try:
                pipeline_result[0] = run_pipeline(
                    project_title=inputs["project_title"],
                    project_summary=inputs["project_summary"],
                    project_code=inputs["project_code"],
                    tech_stack=inputs["tech_stack"],
                    target_pages=inputs["target_pages"],
                    college_format=inputs["college_format"],
                    additional_info=inputs["additional_info"],
                    student_name=inputs["student_name"],
                    roll_number=inputs["roll_number"],
                    college_name=inputs["college_name"],
                    department=inputs["department"],
                    guide_name=inputs["guide_name"],
                    year=inputs["year"],
                )
            except Exception as exc:
                pipeline_error[0] = exc

        worker = threading.Thread(target=_run, daemon=True)
        worker.start()

        prev_log_count = 0
        while worker.is_alive():
            time.sleep(1)
            from pipeline import _trackers
            tracker = None
            if _trackers:
                tracker = list(_trackers.values())[-1]
            if tracker:
                logs = tracker.get_logs()
                if len(logs) != prev_log_count:
                    prev_log_count = len(logs)
                    log_container.code("\n".join(logs), language="text")
                progress = tracker.get_progress()
                pct = min(progress.get("progress_pct", 0), 95)
                elapsed = progress.get("duration_seconds", 0)
                progress_bar.progress(
                    max(5, pct),
                    text=f"{progress.get('current_step', 'Processing...')}  |  {elapsed:.0f}s elapsed",
                )

        worker.join()

        from pipeline import _trackers
        tracker = list(_trackers.values())[-1] if _trackers else None
        if tracker:
            log_container.code("\n".join(tracker.get_logs()), language="text")

        if pipeline_error[0]:
            st.error(f"Generation failed: {str(pipeline_error[0])}")
            st.session_state.generation_started = False
        elif pipeline_result[0]:
            progress_bar.progress(100, text="Complete")
            st.session_state.result = pipeline_result[0]
            st.rerun()


    # ─── Results Display ──────────────────────────────────────────────────────

    else:
        result = st.session_state.result

        if result["status"] == "completed":

            inputs = st.session_state.get("inputs", {})
            tokens = result.get("total_tokens", {})
            total_tok = tokens.get("total", 0)
            cost = result.get("cost_usd", 0)
            duration = result.get("duration_seconds", 0)
            mins = int(duration // 60)
            secs = int(duration % 60)
            dur_str = f"{mins}m {secs}s" if mins > 0 else f"{secs}s"

            st.markdown(f"""
            <div class="success-banner">
                <div class="success-banner-title">Report Generated</div>
                <div class="success-banner-sub">{inputs.get('project_title', 'Your project')} — ready to download</div>
            </div>
            """, unsafe_allow_html=True)

            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Status", "Complete")
            col2.metric("Total Tokens", f"{total_tok:,}")
            col3.metric("Cost (USD)", f"${cost:.4f}")
            col4.metric("Duration", dur_str)

            st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

            output_file = result.get("output_file", "")
            if output_file and os.path.exists(output_file):
                with open(output_file, "rb") as f:
                    file_data = f.read()

                col_l, col_m, col_r = st.columns([1.5, 2, 1.5])
                with col_m:
                    safe_title = inputs.get("project_title", "Project").replace(" ", "_")
                    st.download_button(
                        label="Download Report (.docx)",
                        data=file_data,
                        file_name=f"{safe_title}_Report.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        type="primary",
                        use_container_width=True,
                    )

            st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

            tracking_file = result.get("tracking_file", "")
            if tracking_file and os.path.exists(tracking_file):
                with st.expander("Pipeline Breakdown", expanded=False):
                    with open(tracking_file, "r") as f:
                        tracking_data = json.load(f)

                    for step in tracking_data.get("steps", []):
                        status = step["status"]
                        icon = "✓" if status == "completed" else "✗" if status == "failed" else "⟳"
                        css_class = "step-completed" if status == "completed" else "step-failed" if status == "failed" else "step-running"
                        st.markdown(
                            f"""<div class="step-row {css_class}">
                                <span class="step-icon">{icon}</span>
                                <span class="step-name">{step['step_name']}</span>
                                <span class="step-meta">{step['tokens']['total']:,} tok &nbsp;&middot;&nbsp; {step['duration_seconds']:.1f}s &nbsp;&middot;&nbsp; {step['llm_calls']} call(s)</span>
                            </div>""",
                            unsafe_allow_html=True,
                        )

                    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
                    with st.expander("Raw Tracking JSON", expanded=False):
                        st.json(tracking_data)

            logs = result.get("logs", [])
            if logs:
                with st.expander("Full Console Log", expanded=False):
                    st.code("\n".join(logs), language="text")

        else:
            st.error(f"Generation failed: {result.get('error', 'Unknown error')}")

        st.markdown("<hr>", unsafe_allow_html=True)
        col_l, col_m, col_r = st.columns([1.5, 2, 1.5])
        with col_m:
            if st.button("Generate Another Document", use_container_width=True):
                st.session_state.generation_started = False
                st.session_state.result = None
                st.session_state.job_id = None
                st.rerun()
