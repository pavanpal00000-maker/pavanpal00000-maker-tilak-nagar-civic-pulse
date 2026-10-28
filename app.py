from pathlib import Path
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import hashlib
import hmac

from utils.data_cleaning import (
    load_and_clean_data,
    RATING_COLUMNS,
    OVERALL_COLUMN,
    LOCALITY_COLUMN,
    SUGGESTION_COLUMN,
)
from utils.image_handler import save_complaint_photo
from utils.complaint_tracker import COMPLAINT_STATUSES, make_complaint_id, current_time
from utils.department_mapping import DEPARTMENT_MAPPING
from database.db import (
    setup_database,
    save_complaint,
    find_complaint,
    get_complaint_history,
    update_complaint_status,
    get_all_complaints,
    update_complaint_full,
    delete_complaint,
)

# Page configuration
st.set_page_config(
    page_title="Civic Pulse | Tilak Nagar, Mumbai",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Initialize database schema
setup_database()

# Session State Initialization
if "nav_page" not in st.session_state:
    st.session_state["nav_page"] = "Home"
if "admin_unlocked" not in st.session_state:
    st.session_state["admin_unlocked"] = False
if "tracking_search_id" not in st.session_state:
    st.session_state["tracking_search_id"] = ""
if "location_input" not in st.session_state:
    st.session_state["location_input"] = ""

# Standard civic categories
CIVIC_CATEGORIES = [
    "Water supply",
    "Garbage collection",
    "Public cleanliness",
    "Roads and footpaths",
    "Street lighting",
    "Drainage and sewage",
    "Public toilets",
    "Online municipal services",
    "Other",
]

# Glassmorphic Design System & Custom CSS
st.markdown("""
<style>
    /* ── Hide Streamlit default toolbar (Share, GitHub, Star, Edit buttons) ── */
    [data-testid="stToolbar"]       { display: none !important; }
    [data-testid="stHeader"]        { display: none !important; }
    [data-testid="stDecoration"]    { display: none !important; }
    .stDeployButton                 { display: none !important; }
    header                          { display: none !important; }
    /* ─────────────────────────────────────────────────────────────────────── */

    :root {
        --forest: #1b4d3e;
        --forest-dark: #103328;
        --forest-light: #e6f3ec;
        --glass-bg: rgba(255, 255, 255, 0.75);
        --glass-bg-hover: rgba(255, 255, 255, 0.90);
        --glass-border: rgba(255, 255, 255, 0.70);
        --glass-shadow: 0 8px 32px 0 rgba(16, 51, 40, 0.08);
        --ink: #19241e;
        --muted: #56685d;
        --coral: #c7795a;
        --ochre: #e5b358;
        --emerald: #245b45;
    }

    /* Ambient Aurora background */
    .stApp {
        background: 
            radial-gradient(at 0% 0%, rgba(36, 91, 69, 0.08) 0px, transparent 50%),
            radial-gradient(at 100% 0%, rgba(229, 179, 88, 0.07) 0px, transparent 50%),
            radial-gradient(at 50% 100%, rgba(36, 91, 69, 0.06) 0px, transparent 50%),
            #f7f6f0;
        color: var(--ink);
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    }

    .block-container {
        padding-top: 1.2rem;
        padding-bottom: 3.5rem;
        max-width: 1380px;
    }

    [data-testid="stHeader"] {
        background: rgba(247, 246, 240, 0.85);
        backdrop-filter: blur(14px);
        -webkit-backdrop-filter: blur(14px);
    }

    h1, h2, h3, h4 {
        color: var(--forest-dark);
        font-weight: 800;
        letter-spacing: -0.025em;
    }

    /* Top Brand Bar with Tilak Nagar Civic Logo */
    .brand-container {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0.85rem 1.4rem;
        background: var(--glass-bg);
        backdrop-filter: blur(16px) saturate(180%);
        -webkit-backdrop-filter: blur(16px) saturate(180%);
        border: 1px solid var(--glass-border);
        border-radius: 20px;
        box-shadow: var(--glass-shadow), inset 0 1px 1px rgba(255, 255, 255, 0.8);
        margin-bottom: 1.25rem;
    }

    .brand-title-box {
        display: flex;
        align-items: center;
        gap: 0.95rem;
    }

    .brand-emblem {
        font-size: 2.1rem;
        background: linear-gradient(135deg, #e6f3ec 0%, #d1e8dc 100%);
        padding: 0.35rem 0.75rem;
        border-radius: 14px;
        box-shadow: 0 4px 12px rgba(27, 77, 62, 0.12);
        border: 1px solid rgba(27, 77, 62, 0.18);
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .brand-name {
        font-size: 1.5rem;
        font-weight: 850;
        color: var(--forest-dark);
        letter-spacing: -0.02em;
        line-height: 1.2;
    }

    .brand-sub {
        font-size: 0.88rem;
        color: var(--muted);
        font-weight: 500;
    }

    .brand-tag {
        display: inline-flex;
        align-items: center;
        gap: 0.45rem;
        background: rgba(36, 91, 69, 0.12);
        color: var(--forest);
        font-size: 0.82rem;
        font-weight: 700;
        padding: 0.4rem 0.85rem;
        border-radius: 999px;
        border: 1px solid rgba(36, 91, 69, 0.22);
    }

    /* Hero Banner */
    .hero-banner {
        background: linear-gradient(135deg, rgba(16, 51, 40, 0.95) 0%, rgba(27, 77, 62, 0.92) 55%, rgba(41, 109, 89, 0.88) 100%);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        padding: 2.5rem 2.8rem;
        border-radius: 24px;
        color: #ffffff;
        box-shadow: 0 16px 40px rgba(16, 51, 40, 0.18), inset 0 1px 1px rgba(255, 255, 255, 0.25);
        border: 1px solid rgba(255, 255, 255, 0.18);
        position: relative;
        overflow: hidden;
        margin-bottom: 1.8rem;
    }

    .hero-kicker {
        font-size: 0.82rem;
        font-weight: 800;
        letter-spacing: 0.16em;
        text-transform: uppercase;
        color: #a4e5c4;
        margin-bottom: 0.4rem;
    }

    .hero-title {
        font-size: 2.35rem;
        font-weight: 850;
        line-height: 1.25;
        margin: 0.35rem 0 0.85rem;
        color: #ffffff !important;
        letter-spacing: -0.03em;
    }

    .hero-desc {
        font-size: 1.05rem;
        line-height: 1.7;
        max-width: 860px;
        color: #e4efe9 !important;
        margin-bottom: 1.25rem;
    }

    /* Glass KPI Metric Cards */
    [data-testid="stMetric"] {
        background: var(--glass-bg) !important;
        backdrop-filter: blur(16px) saturate(180%) !important;
        -webkit-backdrop-filter: blur(16px) saturate(180%) !important;
        border: 1px solid var(--glass-border) !important;
        padding: 1.35rem 1.5rem !important;
        border-radius: 20px !important;
        box-shadow: var(--glass-shadow), inset 0 1px 1px rgba(255, 255, 255, 0.8) !important;
        transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1) !important;
    }

    [data-testid="stMetric"]:hover {
        transform: translateY(-3px) scale(1.01) !important;
        background: var(--glass-bg-hover) !important;
        box-shadow: 0 14px 38px 0 rgba(16, 51, 40, 0.12), inset 0 1px 1px rgba(255, 255, 255, 0.9) !important;
    }

    [data-testid="stMetricLabel"] p {
        font-size: 0.88rem !important;
        font-weight: 750 !important;
        color: var(--muted) !important;
        text-transform: uppercase;
        letter-spacing: 0.04em;
    }

    [data-testid="stMetricValue"] {
        font-size: 2.2rem !important;
        font-weight: 850 !important;
        color: var(--forest-dark) !important;
    }

    .glass-card {
        background: var(--glass-bg);
        backdrop-filter: blur(16px) saturate(180%);
        -webkit-backdrop-filter: blur(16px) saturate(180%);
        border: 1px solid var(--glass-border);
        border-radius: 20px;
        padding: 1.4rem 1.6rem;
        box-shadow: var(--glass-shadow), inset 0 1px 1px rgba(255, 255, 255, 0.8);
        transition: all 0.25s ease;
    }

    .spotlight-card {
        background: var(--glass-bg);
        backdrop-filter: blur(16px) saturate(180%);
        -webkit-backdrop-filter: blur(16px) saturate(180%);
        border: 1px solid var(--glass-border);
        border-radius: 20px;
        padding: 1.35rem 1.6rem;
        box-shadow: var(--glass-shadow), inset 0 1px 1px rgba(255, 255, 255, 0.8);
        height: 100%;
        position: relative;
    }

    .spotlight-top {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.75rem;
    }

    .spotlight-title {
        font-size: 0.85rem;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 0.08em;
    }

    .spotlight-val {
        font-size: 1.4rem;
        font-weight: 850;
        color: var(--forest-dark);
        margin: 0.35rem 0;
    }

    .spotlight-sub {
        font-size: 0.88rem;
        color: var(--muted);
    }

    /* Stepper */
    .stepper-container {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: var(--glass-bg);
        backdrop-filter: blur(16px) saturate(180%);
        -webkit-backdrop-filter: blur(16px) saturate(180%);
        padding: 1.8rem 2.2rem;
        border-radius: 20px;
        border: 1px solid var(--glass-border);
        box-shadow: var(--glass-shadow), inset 0 1px 1px rgba(255, 255, 255, 0.8);
        margin: 1.5rem 0 2rem;
        position: relative;
    }

    .step-item {
        display: flex;
        flex-direction: column;
        align-items: center;
        position: relative;
        z-index: 2;
        flex: 1;
        text-align: center;
    }

    .step-circle {
        width: 44px;
        height: 44px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 800;
        font-size: 1rem;
        margin-bottom: 0.6rem;
        transition: all 0.25s ease;
    }

    .step-active .step-circle {
        background: linear-gradient(135deg, #1b4d3e 0%, #245b45 100%);
        color: #ffffff;
        box-shadow: 0 0 0 6px rgba(36, 91, 69, 0.22);
    }

    .step-done .step-circle {
        background: #16a34a;
        color: #ffffff;
        box-shadow: 0 4px 12px rgba(22, 163, 74, 0.3);
    }

    .step-pending .step-circle {
        background: rgba(241, 245, 249, 0.8);
        color: #94a3b8;
        border: 2px dashed #cbd5e1;
    }

    .step-label {
        font-size: 0.85rem;
        font-weight: 700;
        color: var(--ink);
    }

    .step-pending .step-label {
        color: #94a3b8;
    }

    .step-line {
        position: absolute;
        top: 40px;
        left: 8%;
        right: 8%;
        height: 4px;
        background: rgba(203, 213, 225, 0.6);
        z-index: 1;
    }

    /* Suggestion Quote Cards */
    .quote-card {
        background: var(--glass-bg);
        backdrop-filter: blur(14px);
        -webkit-backdrop-filter: blur(14px);
        border: 1px solid var(--glass-border);
        border-left: 5px solid var(--forest);
        padding: 1.15rem 1.35rem;
        border-radius: 16px;
        margin-bottom: 0.95rem;
        box-shadow: 0 4px 16px rgba(16, 51, 40, 0.04), inset 0 1px 1px rgba(255, 255, 255, 0.8);
    }

    .quote-text {
        font-size: 0.96rem;
        color: var(--ink);
        line-height: 1.6;
        font-style: italic;
    }

    .quote-author {
        font-size: 0.8rem;
        font-weight: 700;
        color: var(--muted);
        margin-top: 0.55rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    /* Buttons */
    div.stButton > button, div[data-testid="stFormSubmitButton"] > button {
        background: linear-gradient(135deg, #1b4d3e 0%, #245b45 100%) !important;
        color: #ffffff !important;
        border: 1px solid rgba(255, 255, 255, 0.25) !important;
        border-radius: 12px !important;
        padding: 0.55rem 1.35rem !important;
        font-weight: 700 !important;
        box-shadow: 0 4px 14px rgba(27, 77, 62, 0.2) !important;
        transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1) !important;
    }

    div.stButton > button:hover, div[data-testid="stFormSubmitButton"] > button:hover {
        background: linear-gradient(135deg, #103328 0%, #1b4d3e 100%) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 22px rgba(27, 77, 62, 0.3) !important;
    }

    /* Plotly Chart Container */
    [data-testid="stPlotlyChart"] {
        background: var(--glass-bg) !important;
        backdrop-filter: blur(16px) saturate(180%) !important;
        -webkit-backdrop-filter: blur(16px) saturate(180%) !important;
        border: 1px solid var(--glass-border) !important;
        border-radius: 20px !important;
        padding: 14px !important;
        box-shadow: var(--glass-shadow), inset 0 1px 1px rgba(255, 255, 255, 0.8) !important;
    }

    .section-kicker {
        font-size: 0.82rem;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 0.14em;
        color: var(--forest);
        margin-bottom: 0.25rem;
    }

    .info-badge {
        display: inline-block;
        padding: 0.38rem 0.82rem;
        border-radius: 999px;
        font-size: 0.82rem;
        font-weight: 700;
        background: rgba(36, 91, 69, 0.12);
        color: #103328;
        border: 1px solid rgba(36, 91, 69, 0.22);
    }

    .emergency-card {
        background: rgba(255, 255, 255, 0.85);
        border: 1px solid rgba(220, 38, 38, 0.25);
        border-left: 5px solid #dc2626;
        border-radius: 14px;
        padding: 1rem 1.25rem;
        margin-bottom: 0.75rem;
        box-shadow: 0 3px 12px rgba(220, 38, 38, 0.05);
    }
</style>
""", unsafe_allow_html=True)

# Read clean survey dataset
data = load_and_clean_data()

# -------------------------------------------------------------
# TOP BRAND BAR (TILAK NAGAR CIVIC LOGO INCLUDED)
# -------------------------------------------------------------
brand_col, auth_col = st.columns([3.3, 1.2])

with brand_col:
    st.markdown("""
    <div class="brand-container">
        <div class="brand-title-box">
            <div class="brand-emblem">🏛️</div>
            <div>
                <div class="brand-name">Tilak Nagar Civic Pulse</div>
                <div class="brand-sub">Resident Satisfaction & Community Issue Portal · Ward L / M-West</div>
            </div>
        </div>
        <div class="brand-tag">🟢 Operational</div>
    </div>
    """, unsafe_allow_html=True)

def render_admin_login_dialog():
    st.markdown("### Administrator Verification")
    st.caption("Access complaint management, edit records, and prepare municipal escalation reports.")
    try:
        admin_password_hash = st.secrets["ADMIN_PASSWORD_SHA256"]
    except Exception:
        # Fallback hash for default password 'admin123'
        admin_password_hash = "240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9"

    pwd_input = st.text_input("Admin Password", type="password", key="dialog_admin_pwd", placeholder="Enter password (default: admin123)")
    st.caption("Default password is **admin123** (Configurable in `.streamlit/secrets.toml`)")
    if st.button("Unlock Admin Suite", type="primary", use_container_width=True):
        entered_hash = hashlib.sha256(pwd_input.encode("utf-8")).hexdigest()
        if hmac.compare_digest(entered_hash, admin_password_hash):
            st.session_state["admin_unlocked"] = True
            st.success("Admin controls unlocked successfully.")
            st.rerun()
        else:
            st.error("Invalid administrator password.")


if hasattr(st, "dialog"):
    @st.dialog("Administrator Access")
    def open_admin_dialog():
        render_admin_login_dialog()

with auth_col:
    st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
    if st.session_state.get("admin_unlocked", False):
        st.markdown(
            "<div style='background:rgba(22, 163, 74, 0.12);border:1px solid rgba(22, 163, 74, 0.3);border-radius:14px;padding:8px 14px;text-align:center;'>"
            "<span style='font-size:0.86rem;font-weight:700;color:#15803d;'>Admin Session Active</span>"
            "</div>",
            unsafe_allow_html=True
        )
        if st.button("Logout", key="btn_admin_logout", use_container_width=True):
            st.session_state["admin_unlocked"] = False
            st.rerun()
    else:
        if st.button("Admin Login", key="btn_open_admin_modal", use_container_width=True):
            if hasattr(st, "dialog"):
                open_admin_dialog()
            else:
                st.session_state["show_admin_login_fallback"] = not st.session_state.get("show_admin_login_fallback", False)

if not hasattr(st, "dialog") and st.session_state.get("show_admin_login_fallback", False) and not st.session_state.get("admin_unlocked", False):
    with st.container(border=True):
        render_admin_login_dialog()

# -------------------------------------------------------------
# MAIN NAVIGATION
# -------------------------------------------------------------
nav_options = ["Home", "Dashboard", "Report Issue", "Track Issue", "Admin Portal", "About"]
selected_nav = st.segmented_control(
    "Navigation",
    nav_options,
    default=st.session_state["nav_page"],
    label_visibility="collapsed",
    key="main_nav_selector",
)

if selected_nav and selected_nav != st.session_state["nav_page"]:
    st.session_state["nav_page"] = selected_nav
    st.rerun()

st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)


# =============================================================
# CHART GENERATION FUNCTIONS (ALL CHARTS INCLUDED)
# =============================================================
def show_rating_chart(chart_data, title="Average rating by civic service"):
    average_ratings = []
    for service_name in RATING_COLUMNS:
        if service_name in chart_data.columns:
            average_rating = chart_data[service_name].mean()
            average_ratings.append({
                "Service": service_name,
                "Average rating": average_rating,
            })

    rating_frame = pd.DataFrame(average_ratings).dropna()
    if rating_frame.empty:
        st.info("There are no service ratings to show yet.")
        return

    chart = px.bar(
        rating_frame.sort_values("Average rating"),
        x="Average rating",
        y="Service",
        orientation="h",
        range_x=[0, 5.2],
        title=title,
        color="Average rating",
        color_continuous_scale=["#b7cfc0", "#245b45"],
        text="Average rating",
    )
    chart.update_traces(
        texttemplate="<b>%{x:.2f}</b> / 5",
        textposition="outside",
        hovertemplate="<b>%{y}</b><br>Average Rating: %{x:.2f} / 5<extra></extra>",
        marker_line_width=0,
    )
    chart.update_layout(
        height=420,
        coloraxis_showscale=False,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#19241e", family="sans-serif"),
        title=dict(text=title, font=dict(color="#103328", size=15, weight="bold")),
        margin=dict(l=15, r=35, t=55, b=25),
        xaxis=dict(gridcolor="rgba(203, 213, 225, 0.4)", zeroline=False),
        yaxis=dict(gridcolor="rgba(0,0,0,0)"),
    )
    st.plotly_chart(chart, use_container_width=True)


def show_rating_distribution(chart_data):
    rating_counts = chart_data["Overall rating"].dropna().value_counts().sort_index()
    if rating_counts.empty:
        st.info("There are no overall ratings to show yet.")
        return

    rating_labels = {
        1: "1 - Very dissatisfied",
        2: "2 - Dissatisfied",
        3: "3 - Neutral",
        4: "4 - Satisfied",
        5: "5 - Very satisfied"
    }
    rating_frame = pd.DataFrame({
        "Rating": [rating_labels.get(int(value), str(value)) for value in rating_counts.index],
        "Responses": rating_counts.values,
    })

    chart = px.bar(
        rating_frame,
        x="Rating",
        y="Responses",
        title="Overall satisfaction rating distribution",
        text="Responses",
        color="Responses",
        color_continuous_scale=["#b7cfc0", "#245b45"],
    )
    chart.update_traces(
        textposition="outside",
        hovertemplate="<b>%{x}</b><br>Responses: %{y}<extra></extra>",
        marker_line_width=0,
    )
    chart.update_layout(
        height=380,
        coloraxis_showscale=False,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#19241e", family="sans-serif"),
        title=dict(text="Overall satisfaction rating distribution", font=dict(color="#103328", size=15, weight="bold")),
        margin=dict(l=15, r=15, t=55, b=25),
        xaxis=dict(title=None, gridcolor="rgba(0,0,0,0)"),
        yaxis=dict(title="Responses", gridcolor="rgba(203, 213, 225, 0.4)"),
    )
    st.plotly_chart(chart, use_container_width=True)


def show_suggestions(chart_data):
    suggestions = chart_data[SUGGESTION_COLUMN].dropna().astype(str).str.strip()
    suggestions = suggestions[suggestions != ""]
    if suggestions.empty:
        st.info("No written suggestions have been provided yet.")
        return

    for suggestion in suggestions.head(6):
        st.markdown(f"""
        <div class="quote-card">
            <div class="quote-text">"{suggestion}"</div>
            <div class="quote-author">
                <span>Resident Voice</span>
                <span class="info-badge">Verified Survey</span>
            </div>
        </div>
        """, unsafe_allow_html=True)


# =============================================================
# PAGE 1: HOME
# =============================================================
if st.session_state["nav_page"] == "Home":
    st.markdown("""
    <div class="hero-banner">
        <div class="hero-kicker">TILAK NAGAR · MUMBAI · WARD L & M-WEST</div>
        <div class="hero-title">A better neighbourhood starts with listening.</div>
        <div class="hero-desc">
            Civic Pulse brings resident feedback into one clear, transparent view—helping community members, 
            coordinators, and local representatives understand what is working, what needs urgent attention, 
            and how to systematically track and escalate community issues.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Fast Action Buttons
    c_btn1, c_btn2, c_btn3 = st.columns(3)
    with c_btn1:
        if st.button("Register a Civic Issue", use_container_width=True):
            st.session_state["nav_page"] = "Report Issue"
            st.rerun()
    with c_btn2:
        if st.button("Explore All Charts & Data", use_container_width=True):
            st.session_state["nav_page"] = "Dashboard"
            st.rerun()
    with c_btn3:
        if st.button("Track Existing Complaint", use_container_width=True):
            st.session_state["nav_page"] = "Track Issue"
            st.rerun()

    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

    # Quantitative Metrics with KPI Icons
    complaints_list = get_all_complaints()
    total_complaints = len(complaints_list)
    resolved_count = sum(1 for c in complaints_list if c["status"] == "Resolved")
    tilak_residents = int((data[LOCALITY_COLUMN].astype(str).str.lower() == "tilak nagar").sum())
    overall_avg = data["Overall rating"].mean() if data["Overall rating"].notna().any() else 0

    first_metric, second_metric, third_metric, fourth_metric = st.columns(4)
    first_metric.metric("📊 Survey Responses", len(data), help="Total resident survey submissions collected.")
    second_metric.metric("🏘️ Tilak Nagar Residents", f"{tilak_residents}", f"{(tilak_residents/len(data)*100):.0f}% of sample" if len(data)>0 else "0%")
    third_metric.metric("⭐ Satisfaction Score", f"{overall_avg:.2f} / 5", "Scale 1 to 5")
    fourth_metric.metric("📋 Tracked Civic Issues", f"{total_complaints}", f"{resolved_count} resolved")

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    # Spotlight with Icons
    ratings_dict = {}
    for service_name in RATING_COLUMNS:
        if service_name in data.columns and data[service_name].notna().any():
            ratings_dict[service_name] = data[service_name].mean()

    if ratings_dict:
        best_service = max(ratings_dict, key=ratings_dict.get)
        worst_service = min(ratings_dict, key=ratings_dict.get)

        sp1, sp2 = st.columns(2)
        with sp1:
            st.markdown(f"""
            <div class="spotlight-card" style="border-top: 5px solid #16a34a;">
                <div class="spotlight-top">
                    <span class="spotlight-title" style="color:#16a34a;">🏆 Best Performing Service</span>
                    <span class="info-badge">High Satisfaction</span>
                </div>
                <div class="spotlight-val">{best_service}</div>
                <div class="spotlight-sub">Average rating: <b>{ratings_dict[best_service]:.2f} / 5.0</b> based on resident feedback.</div>
            </div>
            """, unsafe_allow_html=True)
        with sp2:
            st.markdown(f"""
            <div class="spotlight-card" style="border-top: 5px solid #c7795a;">
                <div class="spotlight-top">
                    <span class="spotlight-title" style="color:#c7795a;">⚠️ Needs Most Urgent Attention</span>
                    <span class="info-badge" style="background:rgba(199, 121, 90, 0.15);color:#9a3412;">Priority Action</span>
                </div>
                <div class="spotlight-val">{worst_service}</div>
                <div class="spotlight-sub">Average rating: <b>{ratings_dict[worst_service]:.2f} / 5.0</b> — residents frequently request improvements here.</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    # Core Charts on Home
    st.markdown("<div class='section-kicker'>At a glance</div>", unsafe_allow_html=True)
    st.markdown("### How residents rate local services")
    show_rating_chart(data, "Average rating by civic service")

    left, right = st.columns(2)
    with left:
        show_rating_distribution(data)
    with right:
        st.markdown("<div class='section-kicker'>Community Voices</div>", unsafe_allow_html=True)
        st.markdown("### What residents suggested")
        show_suggestions(data)

    st.caption("These findings describe this survey sample. They should not be treated as representative of every resident in Tilak Nagar.")


# =============================================================
# PAGE 2: DASHBOARD (ALL CHARTS DIRECTLY VISIBLE)
# =============================================================
elif st.session_state["nav_page"] == "Dashboard":
    st.markdown("<div class='section-kicker'>Community Insights & Analytics</div>", unsafe_allow_html=True)
    st.markdown("## Resident satisfaction dashboard")
    st.write("Explore how residents rate services, what needs attention, and how people interact with local complaint systems.")

    # Filter Bar
    locality_values = ["All localities"] + sorted(data[LOCALITY_COLUMN].dropna().astype(str).unique().tolist())
    age_col = "3. What is your age group?"
    reported_column = "13. Have you ever reported a local civic problem?"

    with st.container():
        f1, f2, f3 = st.columns([1.5, 1.5, 1])
        with f1:
            selected_locality = st.selectbox("Filter by locality", locality_values, key="dash_loc_sel")
        with f2:
            age_options = ["All age groups"]
            if age_col in data.columns:
                age_options += sorted(data[age_col].dropna().astype(str).unique().tolist())
            selected_age = st.selectbox("Filter by age group", age_options, key="dash_age_sel")
        with f3:
            st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
            if st.button("Reset Filters", use_container_width=True):
                st.session_state["dash_loc_sel"] = "All localities"
                st.session_state["dash_age_sel"] = "All age groups"
                st.rerun()

    # Filtered Data
    dashboard_data = data.copy()
    if selected_locality != "All localities":
        dashboard_data = dashboard_data[dashboard_data[LOCALITY_COLUMN] == selected_locality]
    if selected_age != "All age groups" and age_col in dashboard_data.columns:
        dashboard_data = dashboard_data[dashboard_data[age_col] == selected_age]

    st.markdown(f"<div style='margin-bottom:14px;color:#56685d;'>Showing <b>{len(dashboard_data)}</b> survey responses · updates live from raw survey data</div>", unsafe_allow_html=True)

    # 4 KPI Metrics with Icons
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("📊 Survey Responses", len(dashboard_data))
    k2.metric("⭐ Average Overall Rating", f"{dashboard_data['Overall rating'].mean():.2f} / 5" if dashboard_data['Overall rating'].notna().any() else "N/A")
    k3.metric("📈 Positive Ratings", f"{(dashboard_data['Overall rating'] >= 4).mean() * 100:.0f}%" if dashboard_data['Overall rating'].notna().any() else "N/A")
    yes_reports = dashboard_data[reported_column].astype(str).str.lower().str.startswith("yes").sum() if reported_column in dashboard_data.columns else 0
    k4.metric("📢 Residents Reported Issues", f"{yes_reports}")

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    # 1. Service Performance (Side by Side)
    st.markdown("## Service performance")
    c1, c2 = st.columns(2)
    with c1:
        show_rating_chart(dashboard_data, "Average rating by service")
    with c2:
        show_rating_distribution(dashboard_data)

    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

    # 2. Satisfaction Patterns Across Civic Services (Full width stacked bar chart)
    st.markdown("## Satisfaction patterns")
    service_rows = []
    for service in RATING_COLUMNS:
        if service in dashboard_data.columns:
            vals = dashboard_data[service].dropna()
            if len(vals) > 0:
                service_rows.extend([
                    {"Service": service, "Rating group": "Needs attention (1–2)", "Responses": int((vals <= 2).sum())},
                    {"Service": service, "Rating group": "Neutral (3)", "Responses": int((vals == 3).sum())},
                    {"Service": service, "Rating group": "Satisfied (4–5)", "Responses": int((vals >= 4).sum())},
                ])
    if service_rows:
        satisfaction_frame = pd.DataFrame(service_rows)
        satisfaction_chart = px.bar(
            satisfaction_frame,
            x="Service",
            y="Responses",
            color="Rating group",
            barmode="stack",
            title="Rating groups across civic services",
            color_discrete_map={
                "Needs attention (1–2)": "#c7795a",
                "Neutral (3)": "#e5c878",
                "Satisfied (4–5)": "#4b8768"
            }
        )
        satisfaction_chart.update_layout(
            height=430,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#19241e", family="sans-serif"),
            title=dict(font=dict(color="#103328", size=15, weight="bold")),
            xaxis=dict(tickangle=-25, gridcolor="rgba(0,0,0,0)"),
            yaxis=dict(gridcolor="rgba(203, 213, 225, 0.4)"),
            legend=dict(title_text="Resident rating", orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            margin=dict(l=20, r=20, t=65, b=90)
        )
        st.plotly_chart(satisfaction_chart, use_container_width=True)

    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

    # 3. Demographics & Geography
    st.markdown("## Demographics & locality representation")
    c3, c4 = st.columns(2)
    with c3:
        locality_frame = dashboard_data[LOCALITY_COLUMN].fillna("Not provided").value_counts().rename_axis("Locality").reset_index(name="Responses")
        locality_chart = px.pie(
            locality_frame,
            names="Locality",
            values="Responses",
            hole=0.55,
            title="Where survey responses came from",
            color_discrete_sequence=["#245b45", "#52997b", "#7da58a", "#d7c99b", "#c7795a", "#b7cfc0"]
        )
        locality_chart.update_layout(
            height=370,
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#19241e", family="sans-serif"),
            title=dict(font=dict(color="#103328", size=15, weight="bold")),
            margin=dict(l=15, r=15, t=60, b=20)
        )
        st.plotly_chart(locality_chart, use_container_width=True)

    with c4:
        if age_col in dashboard_data.columns:
            age_frame = dashboard_data[age_col].fillna("Not provided").value_counts().rename_axis("Age group").reset_index(name="Responses")
            age_chart = px.bar(
                age_frame,
                x="Age group",
                y="Responses",
                title="Responses by age group",
                text="Responses",
                color_discrete_sequence=["#4b8768"]
            )
            age_chart.update_traces(
                textposition="outside",
                hovertemplate="<b>Age: %{x}</b><br>Responses: %{y}<extra></extra>",
            )
            age_chart.update_layout(
                height=370,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#19241e", family="sans-serif"),
                title=dict(font=dict(color="#103328", size=15, weight="bold")),
                margin=dict(l=15, r=15, t=60, b=35),
                xaxis=dict(gridcolor="rgba(0,0,0,0)"),
                yaxis=dict(gridcolor="rgba(203, 213, 225, 0.4)"),
            )
            st.plotly_chart(age_chart, use_container_width=True)

    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

    # 4. Civic Reporting Habits
    if reported_column in dashboard_data.columns:
        st.markdown("## Prior civic reporting experience")
        report_counts = dashboard_data[reported_column].fillna("No answer").value_counts().rename_axis("Answer").reset_index(name="Responses")
        report_chart = px.bar(
            report_counts,
            x="Answer",
            y="Responses",
            title="Have residents reported a civic problem?",
            text="Responses",
            color_discrete_sequence=["#245b45"]
        )
        report_chart.update_traces(
            textposition="outside",
            hovertemplate="<b>Answer: %{x}</b><br>Count: %{y}<extra></extra>",
        )
        report_chart.update_layout(
            height=340,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#19241e", family="sans-serif"),
            title=dict(font=dict(color="#103328", size=15, weight="bold")),
            margin=dict(l=20, r=20, t=60, b=30),
            xaxis=dict(gridcolor="rgba(0,0,0,0)"),
            yaxis=dict(gridcolor="rgba(203, 213, 225, 0.4)"),
        )
        st.plotly_chart(report_chart, use_container_width=True)

    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

    # 5. Written Suggestions & Search Filter
    st.markdown("## Residents’ suggestions")
    sugg_search = st.text_input("Search written suggestions by keyword", placeholder="e.g. water, pothole, garbage, park, light")
    
    sugg_filtered = dashboard_data[[LOCALITY_COLUMN, SUGGESTION_COLUMN]].dropna()
    sugg_filtered = sugg_filtered[sugg_filtered[SUGGESTION_COLUMN].astype(str).str.strip() != ""]
    if sugg_search.strip():
        sugg_filtered = sugg_filtered[sugg_filtered[SUGGESTION_COLUMN].astype(str).str.contains(sugg_search.strip(), case=False, na=False)]

    if sugg_filtered.empty:
        st.info("No suggestions matched your query.")
    else:
        for _, row in sugg_filtered.head(10).iterrows():
            loc_label = row[LOCALITY_COLUMN] if pd.notna(row[LOCALITY_COLUMN]) else "Tilak Nagar"
            st.markdown(f"""
            <div class="quote-card">
                <div class="quote-text">"{row[SUGGESTION_COLUMN]}"</div>
                <div class="quote-author">
                    <span>{loc_label}</span>
                    <span class="info-badge">Resident Voice</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

    # 6. Download Filtered CSV
    st.markdown("## Download data")
    st.caption("Download the filtered responses for your report or further analysis.")
    csv_data = dashboard_data.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Download Filtered Survey Data (CSV)",
        data=csv_data,
        file_name="survey_responses_filtered.csv",
        mime="text/csv",
        key="btn_dash_csv_download"
    )


# =============================================================
# PAGE 3: REPORT ISSUE & TILAK NAGAR EMERGENCY DIRECTORY
# =============================================================
elif st.session_state["nav_page"] == "Report Issue":
    st.markdown("<div class='section-kicker'>Citizen Reporting & Emergency Information</div>", unsafe_allow_html=True)
    st.markdown("## Register a local issue")
    st.caption("Document community concerns for water, sanitation, road quality, and electrical repairs in Tilak Nagar.")

    form_col, emerg_col = st.columns([1.6, 1.2])

    with form_col:
        st.markdown("""
        <div style="background:var(--glass-bg);backdrop-filter:blur(14px);-webkit-backdrop-filter:blur(14px);border:1px solid var(--glass-border);border-left:5px solid var(--forest);border-radius:16px;padding:1rem 1.4rem;margin-bottom:1.5rem;box-shadow:var(--glass-shadow);">
            <div style="font-size:0.92rem;color:#103328;line-height:1.55;">
                <b>Community Portal Note:</b> This portal records community issues for localized prioritization and coordinator handover. 
                Complaints saved here are audited by the community administrator, who compiles and reports them directly to BMC.
            </div>
        </div>
        """, unsafe_allow_html=True)

        with st.container():
            st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
            st.markdown("#### 1. Issue Category")
            category = st.selectbox(
                "Issue category",
                CIVIC_CATEGORIES,
                key="complaint_form_cat"
            )

            mapped_dept = DEPARTMENT_MAPPING.get(category, "General Municipal Services")
            st.markdown(f"""
            <div style="background:rgba(36, 91, 69, 0.08);border:1px solid rgba(36, 91, 69, 0.2);padding:0.6rem 1rem;border-radius:12px;font-size:0.88rem;color:#103328;margin:0.5rem 0 1.2rem;">
                <b>Likely Municipal Service Area:</b> <span style="font-weight:750;color:#1b4d3e;">{mapped_dept}</span>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("#### 2. Location")
            st.caption("Click a quick Tilak Nagar landmark chip or type an exact address:")
            
            l1, l2, l3, l4, l5 = st.columns(5)
            with l1:
                if st.button("Tilak Nagar Stn", key="c_stn", use_container_width=True):
                    st.session_state["location_input"] = "Near Tilak Nagar Railway Station"
            with l2:
                if st.button("Sahakar Nagar", key="c_sahakar", use_container_width=True):
                    st.session_state["location_input"] = "Sahakar Nagar, Tilak Nagar"
            with l3:
                if st.button("Shell Colony", key="c_shell", use_container_width=True):
                    st.session_state["location_input"] = "Shell Colony Road, Tilak Nagar"
            with l4:
                if st.button("Pestom Sagar", key="c_pestom", use_container_width=True):
                    st.session_state["location_input"] = "Pestom Sagar Colony"
            with l5:
                if st.button("Tilak Nagar Ground", key="c_ground", use_container_width=True):
                    st.session_state["location_input"] = "Near Tilak Nagar Municipal Ground"

            location = st.text_input(
                "Issue location *",
                value=st.session_state.get("location_input", ""),
                placeholder="Example: Near Shell Colony market, Tilak Nagar",
                key="complaint_loc_val"
            )

            st.markdown("#### 3. Description")
            description = st.text_area(
                "Describe the issue *",
                placeholder="Explain what happened and where it can be seen.",
                key="complaint_desc_val",
                height=120
            )

            st.markdown("#### 4. Photo Evidence (Optional)")
            photo_choice = st.pills(
                "Photo Input Option",
                ["Upload Photo", "Take a Picture", "No Photo"],
                default="Upload Photo",
                key="pills_photo_choice"
            )

            uploaded_photo = None
            if photo_choice == "Upload Photo":
                uploaded_photo = st.file_uploader(
                    "Upload a photo (optional)",
                    type=["jpg", "jpeg", "png", "webp"],
                    help="Use a photo up to 5 MB. Avoid including faces or personal details.",
                    key="form_upload_widget"
                )
            elif photo_choice == "Take a Picture":
                uploaded_photo = st.camera_input("Or take a picture with camera", key="form_camera_widget")

            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
            consent = st.checkbox(
                "I understand this complaint will be stored in this project portal for community review and coordinator reporting to BMC.",
                key="complaint_consent_box"
            )

            submitted = st.button("Register Complaint", type="primary", use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

        if submitted:
            if not location.strip() or not description.strip():
                st.error("Please enter the issue location and description.")
            elif not consent:
                st.error("Please confirm how this project portal handles complaints.")
            else:
                try:
                    photo_name = save_complaint_photo(uploaded_photo)
                    complaint_id = make_complaint_id()
                    created_at = current_time()

                    save_complaint({
                        "complaint_id": complaint_id,
                        "created_at": created_at,
                        "category": category,
                        "description": description.strip(),
                        "location": location.strip(),
                        "photo_name": photo_name,
                        "status": "Submitted",
                        "updated_at": created_at,
                    })

                    st.session_state["location_input"] = ""

                    receipt_html = (
                        f'<div style="background:var(--glass-bg);backdrop-filter:blur(16px);-webkit-backdrop-filter:blur(16px);border:2px solid #86efac;border-radius:20px;padding:1.6rem 2rem;margin-top:1.5rem;box-shadow:var(--glass-shadow);">'
                        f'<div style="font-size:1.35rem;font-weight:850;color:#15803d;margin-bottom:0.4rem;">Your complaint has been saved in this project portal.</div>'
                        f'<div style="font-size:0.9rem;color:#56685d;">A unique civic tracking reference has been generated.</div>'
                        f'<div style="background:rgba(255,255,255,0.85);padding:1.1rem 1.5rem;border-radius:14px;border:1px solid #cbd5e1;margin:1rem 0;">'
                        f'<div style="font-size:0.8rem;text-transform:uppercase;font-weight:800;color:#64748b;">Save this Complaint ID to track status</div>'
                        f'<div style="font-size:1.8rem;font-weight:900;color:#1b4d3e;letter-spacing:0.04em;">{complaint_id}</div>'
                        f'</div>'
                        f'<div style="font-size:0.9rem;color:#334155;line-height:1.6;">'
                        f'• <b>Service Area:</b> {category} ({mapped_dept})<br>'
                        f'• <b>Location:</b> {location}<br>'
                        f'• <b>Initial Status:</b> <span class="info-badge">Submitted</span>'
                        f'</div></div>'
                    )
                    st.markdown(receipt_html, unsafe_allow_html=True)

                    if st.button(f"Track Complaint ({complaint_id}) Now", type="primary", use_container_width=True):
                        st.session_state["tracking_search_id"] = complaint_id
                        st.session_state["nav_page"] = "Track Issue"
                        st.rerun()

                except ValueError as error:
                    st.error(str(error))
                except Exception:
                    st.error("The complaint could not be saved. Please try again.")

    # RIGHT COLUMN: EMERGENCY DIRECTORY
    with emerg_col:
        st.markdown("<div class='section-kicker'>Urgent Contacts</div>", unsafe_allow_html=True)
        st.markdown("### Tilak Nagar Emergency Directory")
        st.caption("For immediate life hazards, medical emergencies, or live wire/gas leaks, contact official services directly:")

        with st.container():
            st.markdown("""
            <div class="emergency-card">
                <div style="font-weight:800;color:#b91c1c;font-size:0.95rem;text-transform:uppercase;">Hospitals & Medical Emergency</div>
                <div style="font-size:0.88rem;color:#19241e;margin-top:0.35rem;line-height:1.55;">
                    <b>Rajawadi Municipal Hospital (24x7 Casualty):</b> 022-25094140 / 25094141<br>
                    <b>Surana Sethia Hospital (Chembur):</b> 022-67865100 / 33783378<br>
                    <b>Tilak Nagar Maternity & BMC Dispensary:</b> 022-25221234<br>
                    <b>National Ambulance Helpline:</b> 108 / 102
                </div>
            </div>

            <div class="emergency-card" style="border-left-color: #2563eb; border-color: rgba(37, 99, 235, 0.25);">
                <div style="font-weight:800;color:#1d4ed8;font-size:0.95rem;text-transform:uppercase;">Police & Citizen Safety</div>
                <div style="font-size:0.88rem;color:#19241e;margin-top:0.35rem;line-height:1.55;">
                    <b>Tilak Nagar Police Station:</b> 022-25224322 / 25227705<br>
                    <b>Police Control Room:</b> 100 / 112<br>
                    <b>Mumbai Women Helpline:</b> 103 / 1091<br>
                    <b>Senior Citizen Helpline:</b> 1090
                </div>
            </div>

            <div class="emergency-card" style="border-left-color: #d97706; border-color: rgba(217, 119, 6, 0.25);">
                <div style="font-weight:800;color:#b45309;font-size:0.95rem;text-transform:uppercase;">Fire & Disaster Management</div>
                <div style="font-size:0.88rem;color:#19241e;margin-top:0.35rem;line-height:1.55;">
                    <b>Chembur Fire Station:</b> 022-25226161 / 101<br>
                    <b>Kurla Fire Station:</b> 022-26500101<br>
                    <b>BMC Disaster Control Room:</b> 1916 / 022-22694725
                </div>
            </div>

            <div class="emergency-card" style="border-left-color: #1b4d3e; border-color: rgba(27, 77, 62, 0.25);">
                <div style="font-weight:800;color:#1b4d3e;font-size:0.95rem;text-transform:uppercase;">Municipal Ward Offices & Utilities</div>
                <div style="font-size:0.88rem;color:#19241e;margin-top:0.35rem;line-height:1.55;">
                    <b>BMC Ward L Office (Kurla):</b> 022-26505103 / 26505109<br>
                    <b>BMC Ward M-West Office (Chembur):</b> 022-25284000<br>
                    <b>BMC Water Supply Complaints:</b> 1916<br>
                    <b>Adani Electricity Outage Helpline:</b> 19122 / 1800 532 9998<br>
                    <b>Mahanagar Gas Emergency (Gas Leak):</b> 1917 / 022-24012400
                </div>
            </div>
            """, unsafe_allow_html=True)


# =============================================================
# PAGE 4: TRACK ISSUE
# =============================================================
elif st.session_state["nav_page"] == "Track Issue":
    st.markdown("<div class='section-kicker'>Transparency & Resolution</div>", unsafe_allow_html=True)
    st.markdown("## Track a complaint")
    st.caption("Search for a registered community issue using its unique project portal ID.")

    all_recent = get_all_complaints()
    if all_recent:
        st.markdown("<div style='font-size:0.84rem;font-weight:700;color:#56685d;margin-bottom:6px;'>Sample IDs to test:</div>", unsafe_allow_html=True)
        s_cols = st.columns(min(len(all_recent), 3))
        for idx, sample in enumerate(all_recent[:3]):
            with s_cols[idx]:
                if st.button(f"{sample['complaint_id']}", key=f"chip_track_{sample['complaint_id']}", use_container_width=True):
                    st.session_state["tracking_search_id"] = sample['complaint_id']
                    st.rerun()

    s_box, b_box = st.columns([3.5, 1])
    with s_box:
        complaint_id_input = st.text_input(
            "Complaint ID",
            value=st.session_state.get("tracking_search_id", ""),
            placeholder="Example: TNC-20261014-1234",
            label_visibility="collapsed",
            key="track_id_field"
        )
    with b_box:
        find_clicked = st.button("Find Complaint", type="primary", use_container_width=True)

    query_id = complaint_id_input.strip().upper()

    if query_id or find_clicked:
        if not query_id:
            st.warning("Enter a complaint ID first.")
        else:
            complaint = find_complaint(query_id)
            if complaint is None:
                st.error("No complaint was found with that ID.")
            else:
                curr_status = complaint["status"]
                dept_mapped = DEPARTMENT_MAPPING.get(complaint["category"], "Municipal Services")

                stages = ["Submitted", "Under Review", "In Progress", "Resolved", "Closed"]
                try:
                    active_idx = stages.index(curr_status)
                except ValueError:
                    active_idx = 0

                stepper_items = []
                for i, st_name in enumerate(stages):
                    if i < active_idx:
                        cls = "step-item step-done"
                        icon_txt = "Done"
                    elif i == active_idx:
                        cls = "step-item step-active"
                        icon_txt = str(i + 1)
                    else:
                        cls = "step-item step-pending"
                        icon_txt = str(i + 1)
                    stepper_items.append(f'<div class="{cls}"><div class="step-circle">{icon_txt}</div><div class="step-label">{st_name}</div></div>')

                stepper_html = f"<div class='stepper-container'><div class='step-line'></div>{''.join(stepper_items)}</div>"
                st.markdown(stepper_html, unsafe_allow_html=True)

                # Dossier Card
                dossier_html = (
                    f'<div class="glass-card" style="margin-bottom:1.5rem;">'
                    f'<div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:1rem;margin-bottom:1.2rem;">'
                    f'<div><div style="font-size:0.8rem;font-weight:800;color:#56685d;text-transform:uppercase;">Registered Case Record</div>'
                    f'<div style="font-size:1.6rem;font-weight:900;color:#103328;">{complaint["complaint_id"]}</div></div>'
                    f'<div><span class="info-badge" style="font-size:0.95rem;padding:0.45rem 1rem;">Current Status: <b>{curr_status}</b></span></div>'
                    f'</div>'
                    f'<div style="display:grid;grid-template-columns:repeat(auto-fit, minmax(210px, 1fr));gap:1rem;background:rgba(255,255,255,0.7);padding:1rem 1.4rem;border-radius:14px;border:1px solid rgba(27,77,62,0.12);">'
                    f'<div><span style="font-size:0.75rem;color:#64748b;font-weight:700;text-transform:uppercase;">Category</span><div style="font-size:0.96rem;font-weight:750;color:#19241e;">{complaint["category"]}</div></div>'
                    f'<div><span style="font-size:0.75rem;color:#64748b;font-weight:700;text-transform:uppercase;">Likely Service Wing</span><div style="font-size:0.96rem;font-weight:750;color:#1b4d3e;">{dept_mapped}</div></div>'
                    f'<div><span style="font-size:0.75rem;color:#64748b;font-weight:700;text-transform:uppercase;">Registered At</span><div style="font-size:0.92rem;font-weight:600;color:#19241e;">{complaint["created_at"]}</div></div>'
                    f'<div><span style="font-size:0.75rem;color:#64748b;font-weight:700;text-transform:uppercase;">Last Updated</span><div style="font-size:0.92rem;font-weight:600;color:#19241e;">{complaint["updated_at"]}</div></div>'
                    f'</div></div>'
                )
                st.markdown(dossier_html, unsafe_allow_html=True)

                if complaint["photo_name"]:
                    photo_file = Path(__file__).resolve().parent / "complaints" / "uploads" / complaint["photo_name"]
                    if photo_file.exists():
                        with st.expander("View Attached Photo Evidence", expanded=False):
                            st.image(str(photo_file), caption=f"Evidence for {complaint['complaint_id']}", use_container_width=True)

                st.markdown("### Status history")
                history = get_complaint_history(complaint["complaint_id"])
                for item in history:
                    note_text = item['note'] if item['note'] else 'Complaint update logged into system.'
                    history_html = (
                        f'<div style="display:flex;gap:1.2rem;margin-bottom:1rem;position:relative;">'
                        f'<div style="display:flex;flex-direction:column;align-items:center;">'
                        f'<div style="width:14px;height:14px;border-radius:50%;background:#1b4d3e;border:3px solid #86efac;"></div>'
                        f'<div style="width:2px;flex-grow:1;background:rgba(203, 213, 225, 0.7);margin-top:4px;"></div>'
                        f'</div>'
                        f'<div class="glass-card" style="padding:0.9rem 1.35rem;flex:1;">'
                        f'<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.35rem;">'
                        f'<span style="font-size:0.96rem;font-weight:800;color:#103328;">Status: {item["status"]}</span>'
                        f'<span style="font-size:0.8rem;color:#64748b;font-weight:600;">Timestamp: {item["changed_at"]}</span>'
                        f'</div>'
                        f'<div style="font-size:0.9rem;color:#334155;line-height:1.5;">{note_text}</div>'
                        f'</div></div>'
                    )
                    st.markdown(history_html, unsafe_allow_html=True)



# =============================================================
# PAGE 5: ADMIN PORTAL (COMPLAINT HANDOVER & MANAGEMENT SUITE)
# =============================================================
elif st.session_state["nav_page"] == "Admin Portal":
    st.markdown("<div class='section-kicker'>Project Handover & Governance Suite</div>", unsafe_allow_html=True)
    st.markdown("## Community Complaints Management & BMC Escalation")

    if not st.session_state.get("admin_unlocked", False):
        st.warning("Access Restricted: Please enter the administrator password to manage complaints.")
        with st.container(border=True):
            render_admin_login_dialog()
    else:
        all_comp = get_all_complaints()
        tot = len(all_comp)
        c_sub = sum(1 for c in all_comp if c["status"] == "Submitted")
        c_rev = sum(1 for c in all_comp if c["status"] == "Under Review")
        c_prog = sum(1 for c in all_comp if c["status"] == "In Progress")
        c_res = sum(1 for c in all_comp if c["status"] == "Resolved")

        # Admin KPI Metrics with Icons
        ak1, ak2, ak3, ak4 = st.columns(4)
        ak1.metric("🗂️ Total Complaints", tot)
        ak2.metric("⏳ Pending Review", f"{c_sub + c_rev}")
        ak3.metric("🔧 In Progress", f"{c_prog}")
        ak4.metric("✅ Resolved Cases", f"{c_res}")

        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

        if not all_comp:
            st.info("No complaints registered yet in the database.")
        else:
            admin_tab_list, admin_tab_manage = st.tabs([
                "View and Export All Complaints",
                "Edit and Escalate to BMC"
            ])
            
            with admin_tab_list:
                df_admin = pd.DataFrame([dict(c) for c in all_comp])
                
                f_c1, f_c2 = st.columns([1.5, 2])
                with f_c1:
                    f_status = st.selectbox("Filter complaints by status", ["All"] + COMPLAINT_STATUSES, key="adm_status_filter_table")
                if f_status != "All":
                    df_admin = df_admin[df_admin["status"] == f_status]

                st.dataframe(
                    df_admin,
                    column_config={
                        "complaint_id": st.column_config.TextColumn("Complaint ID", width="medium"),
                        "created_at": st.column_config.DatetimeColumn("Registered", format="YYYY-MM-DD HH:mm"),
                        "category": "Category",
                        "location": "Location",
                        "description": "Description",
                        "status": "Current Status",
                        "updated_at": "Last Updated",
                    },
                    hide_index=True,
                    use_container_width=True,
                )

                # Export CSV button specifically for BMC submission handover
                st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
                csv_for_bmc = df_admin.to_csv(index=False).encode("utf-8")
                st.download_button(
                    label="Export Complaints Report for BMC Submission (CSV)",
                    data=csv_for_bmc,
                    file_name="tilak_nagar_complaints_for_bmc.csv",
                    mime="text/csv",
                    key="btn_export_bmc_csv"
                )

            with admin_tab_manage:
                st.markdown("#### Complaint Editor & BMC Handover Action Center")
                st.caption("Select any complaint to review, edit details, attach BMC reference tokens, or prepare official escalation notices.")
                
                complaint_id_list = [c["complaint_id"] for c in all_comp]
                selected_adm_id = st.selectbox("Select Complaint to Edit / Manage", complaint_id_list, key="adm_select_case_box")
                
                target_case = find_complaint(selected_adm_id)
                if target_case:
                    e_col1, e_col2 = st.columns([1.3, 1.7])
                    
                    with e_col1:
                        st.markdown(f"""
                        <div class="glass-card" style="margin-bottom:1rem;">
                            <div style="font-size:1.15rem;font-weight:800;color:#103328;">Complaint: {target_case['complaint_id']}</div>
                            <div style="font-size:0.88rem;color:#56685d;margin-top:0.2rem;">Registered on: {target_case['created_at']}</div>
                            <div style="margin-top:0.75rem;">
                                <span class="info-badge">Current Status: {target_case['status']}</span>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                        if target_case["photo_name"]:
                            p_path = Path(__file__).resolve().parent / "complaints" / "uploads" / target_case["photo_name"]
                            if p_path.exists():
                                st.image(str(p_path), caption="Attached Photo Evidence", use_container_width=True)

                        with st.expander("Delete or Archive This Complaint", expanded=False):
                            st.caption("Use this only if the complaint is spam, duplicate, or a test submission.")
                            if st.button("Permanently Delete Complaint", key="btn_del_complaint"):
                                delete_complaint(selected_adm_id)
                                st.success(f"Complaint {selected_adm_id} deleted.")
                                st.rerun()

                    with e_col2:
                        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
                        st.markdown("##### 1. Edit Complaint Fields")
                        
                        edit_cat_idx = CIVIC_CATEGORIES.index(target_case["category"]) if target_case["category"] in CIVIC_CATEGORIES else 0
                        new_cat = st.selectbox("Category", CIVIC_CATEGORIES, index=edit_cat_idx, key="edit_field_cat")
                        
                        new_loc = st.text_input("Location", value=target_case["location"], key="edit_field_loc")
                        new_desc = st.text_area("Description", value=target_case["description"], key="edit_field_desc", height=100)
                        
                        current_status_idx = COMPLAINT_STATUSES.index(target_case["status"]) if target_case["status"] in COMPLAINT_STATUSES else 0
                        new_status = st.selectbox(
                            "Resolution Status",
                            COMPLAINT_STATUSES,
                            index=current_status_idx,
                            key="adm_new_status_box"
                        )

                        st.markdown("##### 2. BMC Reporting & Handover Details")
                        st.caption("When you report this issue to BMC, record the action note or reference number below:")
                        
                        qn_col1, qn_col2 = st.columns(2)
                        with qn_col1:
                            if st.button("Reported to BMC 1916", key="qn_bmc1916", use_container_width=True):
                                st.session_state["adm_audit_note_field"] = "Reported to BMC 1916 Helpline for urgent ward escalation."
                        with qn_col2:
                            if st.button("Field Resolved", key="qn_resolved", use_container_width=True):
                                st.session_state["adm_audit_note_field"] = "Verified on site: Issue repaired and resolved by municipal staff."

                        update_note = st.text_input(
                            "Administrative Action / BMC Escalation Note",
                            value=st.session_state.get("adm_audit_note_field", ""),
                            placeholder="e.g. Forwarded to Ward L inspection supervisor. BMC Token: WARD-L-9821",
                            key="adm_audit_note_field"
                        )

                        if st.button("Save All Updates to Database", type="primary", use_container_width=True):
                            now_time = current_time()
                            update_complaint_full(
                                selected_adm_id,
                                new_cat,
                                new_loc.strip(),
                                new_desc.strip(),
                                new_status,
                                update_note.strip() if update_note.strip() else f"Status updated to {new_status}",
                                now_time
                            )
                            st.success(f"Complaint {selected_adm_id} updated successfully.")
                            st.rerun()

                        st.markdown("</div>", unsafe_allow_html=True)

                    st.markdown("---")
                    st.markdown("##### Generate Formal BMC Escalation Letter")
                    st.caption("The coordinator can copy or print this formatted draft letter to hand over or submit directly to the BMC Ward Office:")
                    
                    mapped_wing = DEPARTMENT_MAPPING.get(new_cat, "General Municipal Services")
                    bmc_letter_draft = f"""TO:
The Assistant Municipal Commissioner,
Municipal Corporation of Greater Mumbai (BMC),
Ward L / Ward M-West Administrative Office,
Mumbai, Maharashtra.

SUBJECT: Escalation of Civic Grievance - {new_cat} at {new_loc}
REFERENCE ID: {selected_adm_id}
DATE: {datetime.now().strftime("%d-%B-%Y")}

Respected Sir / Madam,

This formal representation is submitted on behalf of the residents of Tilak Nagar regarding an unresolved local civic grievance registered in our community monitoring portal:

1. Complaint Reference ID: {selected_adm_id}
2. Service Area: {new_cat} (Responsible Wing: {mapped_wing})
3. Exact Location: {new_loc}
4. Date Reported: {target_case['created_at']}
5. Current Status in Community Portal: {new_status}

ISSUE DESCRIPTION:
"{new_desc}"

Kindly assign your ward inspection and maintenance crew to address this issue at the earliest to ensure public health and citizen safety in Tilak Nagar.

Sincerely,
Tilak Nagar Civic Pulse Community Coordinator / Representative
Mumbai, Ward L / M-West"""

                    st.text_area("BMC Escalation Letter Draft", bmc_letter_draft, height=260)
                    st.download_button(
                        label="Download BMC Letter Draft (.txt)",
                        data=bmc_letter_draft.encode("utf-8"),
                        file_name=f"BMC_Escalation_{selected_adm_id}.txt",
                        mime="text/plain",
                        key="btn_download_bmc_letter"
                    )


# =============================================================
# PAGE 6: ABOUT
# =============================================================
elif st.session_state["nav_page"] == "About":
    st.markdown("<div class='section-kicker'>Project Scope & Purpose</div>", unsafe_allow_html=True)
    st.markdown("## About this project")
    
    st.markdown("""
    <div class="glass-card" style="margin-bottom:1.5rem;">
        <h3 style="margin-top:0;color:#103328;">Tilak Nagar Civic Pulse</h3>
        <p style="font-size:1.02rem;color:#334155;line-height:1.75;">
            Resident Satisfaction with Local Services in Tilak Nagar, Mumbai, is an independent data science and community governance project. 
            It uses survey data to summarize residents' views about local services and provides an accountable, centralized portal 
            for community coordinators to document, audit, and systematically escalate civic issues to municipal authorities.
        </p>
    </div>
    """, unsafe_allow_html=True)

    col_a1, col_a2, col_a3 = st.columns(3)
    with col_a1:
        st.markdown("""
        <div class="spotlight-card">
            <div style="font-weight:800;font-size:1.15rem;color:#103328;margin-bottom:0.4rem;">Survey Analysis</div>
            <div style="font-size:0.9rem;color:#56685d;line-height:1.55;">
                Clean and analyze survey responses with interactive charts that update automatically from the CSV data.
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_a2:
        st.markdown("""
        <div class="spotlight-card">
            <div style="font-weight:800;font-size:1.15rem;color:#103328;margin-bottom:0.4rem;">Issue Tracking</div>
            <div style="font-size:0.9rem;color:#56685d;line-height:1.55;">
                Store community complaints in a separate SQLite database with a 5-stage visual resolution tracker and audit timeline.
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_a3:
        st.markdown("""
        <div class="spotlight-card">
            <div style="font-weight:800;font-size:1.15rem;color:#103328;margin-bottom:0.4rem;">Admin Control & Handover</div>
            <div style="font-size:0.9rem;color:#56685d;line-height:1.55;">
                Enables full complaint editing, audit note logging, and one-click BMC escalation letter generation for project handover.
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
    st.markdown("""
    <div style="background:rgba(254, 243, 199, 0.7);backdrop-filter:blur(14px);-webkit-backdrop-filter:blur(14px);border:1px solid #fcd34d;border-radius:16px;padding:1.1rem 1.5rem;font-size:0.92rem;color:#92400e;line-height:1.65;box-shadow:var(--glass-shadow);">
        <b>Important Note:</b> This portal is an independent community prototype. It does not automatically dispatch crews; 
        rather, it empowers community coordinators to document and formally escalate issues to BMC Ward L / M-West offices.
    </div>
    """, unsafe_allow_html=True)
