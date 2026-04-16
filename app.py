import streamlit as st
import pandas as pd
from datetime import datetime

# Safe Import for Plotly
try:
    import plotly.express as px
    import plotly.graph_objects as go
except ImportError:
    px = None
    go = None

# Project Imports
from src.services.billing import explain_anomaly_reason, explain_charge, interpret_anomaly
from src.data.database import init_db, save_charges, load_history
from src.services.analytics import history_to_df
from src.data.parser import extract_charges, extract_charges_from_pdf
from src.ml.anomaly_model import AnomalyModel

init_db()

# ================= PAGE CONFIG =================
st.set_page_config(
    page_title="Explain My Bill — AI",
    layout="wide",
    page_icon="⚡"
)

# ================= PROFESSIONAL CSS =================
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=DM+Mono:wght@400;500&display=swap');

    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif;
    }

    /* Background */
    .stApp {
        background: #0f1117;
        color: #e8eaf0;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: #16191f !important;
        border-right: 1px solid #2a2d36;
    }

    /* Metric cards */
    [data-testid="stMetric"] {
        background: #1c1f27;
        border: 1px solid #2a2d36;
        border-radius: 12px;
        padding: 20px 24px;
        transition: border-color 0.2s;
    }
    [data-testid="stMetric"]:hover {
        border-color: #4f8ef7;
    }
    [data-testid="stMetricLabel"] {
        font-size: 0.75rem;
        font-weight: 600;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        color: #7a7f8e !important;
    }
    [data-testid="stMetricValue"] {
        font-size: 1.8rem;
        font-weight: 700;
        color: #e8eaf0 !important;
        font-family: 'DM Mono', monospace;
    }

    /* Expanders */
    [data-testid="stExpander"] {
        background: #1c1f27 !important;
        border: 1px solid #2a2d36 !important;
        border-radius: 12px !important;
        margin-bottom: 12px;
    }
    [data-testid="stExpander"]:hover {
        border-color: #4f8ef7 !important;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        background: #16191f;
        border-radius: 10px;
        padding: 4px;
        gap: 4px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        color: #7a7f8e;
        font-weight: 500;
        padding: 8px 20px;
    }
    .stTabs [aria-selected="true"] {
        background: #4f8ef7 !important;
        color: white !important;
    }

    /* Info/Warning boxes */
    .stInfo {
        background: #1c1f27;
        border-left: 3px solid #4f8ef7;
        border-radius: 8px;
    }

    /* Dataframe */
    [data-testid="stDataFrame"] {
        border-radius: 12px;
        overflow: hidden;
    }

    /* Divider */
    hr {
        border-color: #2a2d36;
        margin: 24px 0;
    }

    /* Title styling */
    h1 { font-weight: 700; letter-spacing: -0.02em; }
    h2, h3 { font-weight: 600; color: #c8cbda; }

    /* Progress bar */
    .stProgress > div > div {
        background: linear-gradient(90deg, #4f8ef7, #7c4dff);
        border-radius: 99px;
    }
    .stProgress > div {
        background: #2a2d36;
        border-radius: 99px;
    }

    /* Upload area */
    [data-testid="stFileUploader"] {
        background: #1c1f27;
        border: 1.5px dashed #2a2d36;
        border-radius: 12px;
        padding: 8px;
    }
    </style>
""", unsafe_allow_html=True)

# ================= HEADER =================
col_title, col_badge = st.columns([6, 1])
with col_title:
    st.markdown("## ⚡ Explain My Bill")
    st.caption("AI-powered anomaly detection & cost breakdown for utility bills")

st.markdown("---")

# ================= MODEL & DATA =================
@st.cache_resource
def load_model():
    return AnomalyModel()

model = load_model()
history = load_history()
df_all = history_to_df(history, model)
model.train(history)

# ================= SIDEBAR =================
with st.sidebar:
    st.markdown("### 📤 Upload Your Bill")
    st.markdown("<small style='color:#7a7f8e'>Supports `.txt` and `.pdf` formats</small>", unsafe_allow_html=True)
    st.markdown("")
    uploaded_file = st.file_uploader("Choose file", type=["txt", "pdf"], label_visibility="collapsed")

    st.markdown("---")
    st.markdown("### 📊 Dataset Stats")
    if not df_all.empty:
        st.metric("Total Records", len(df_all))
        st.metric("Charge Types", df_all["charge"].nunique())
        st.metric("Date Range", f"{df_all['timestamp'].min().strftime('%b %Y')} → {df_all['timestamp'].max().strftime('%b %Y')}" if not df_all.empty else "—")
    else:
        st.info("No data yet.")

    st.markdown("---")
    st.markdown("<small style='color:#4a4f5e'>Built with Streamlit · IsolationForest · pdfplumber</small>", unsafe_allow_html=True)

# ================= MAIN CONTENT =================
if uploaded_file:
    with st.spinner("Parsing your bill..."):
        if uploaded_file.name.endswith(".pdf"):
            charges = extract_charges_from_pdf(uploaded_file)
        else:
            content = uploaded_file.read().decode("utf-8")
            charges = extract_charges(content)

    if not charges:
        st.error("❌ Could not extract any charges from this file. Please check the format.")
        st.stop()

    save_charges(charges)
    st.toast("Bill processed successfully!", icon="⚡")

    # Refresh after save
    history = load_history()
    df_all = history_to_df(history, model)
    model.train(history)

    # Compute base total (exclude 'total' key to avoid double counting)
    base_total = sum(v for k, v in charges.items() if k != "total")

    tab_analysis, tab_history = st.tabs(["🔍 Analysis", "📈 History & Trends"])

    # ───────── TAB 1: ANALYSIS ─────────
    with tab_analysis:
        st.markdown("#### Current Bill Summary")

        # Metric row
        charge_keys = [k for k in ["electricity", "water", "gas"] if k in charges]
        cols = st.columns(len(charge_keys) + 1)
        cols[0].metric("Grand Total", f"€{base_total:.2f}")
        icons = {"electricity": "⚡", "water": "💧", "gas": "🔥"}
        for i, key in enumerate(charge_keys):
            cols[i + 1].metric(f"{icons.get(key, '📦')} {key.title()}", f"€{charges[key]:.2f}")

        st.markdown("---")
        st.markdown("#### Charge Breakdown")

        for name, value in charges.items():
            if name == "total":
                continue

            explanation = explain_charge(name, value)
            anomaly = model.predict(value)
            reason = explain_anomaly_reason(df_all, name, value)
            percent = (value / base_total * 100) if base_total > 0 else 0

            is_anomaly = anomaly == "Anomaly detected"
            status_color = "#ff4b4b" if is_anomaly else "#00c48c"
            status_label = "🔴 Anomaly" if is_anomaly else "🟢 Normal"

            with st.expander(f"{icons.get(name, '📦')} {name.title()}  —  €{value:.2f}  ·  {status_label}", expanded=is_anomaly):
                left, right = st.columns([1, 2])
                with left:
                    st.metric("Amount", f"€{value:.2f}")
                    st.caption(f"**{percent:.1f}%** of total bill")
                    st.progress(min(percent / 100, 1.0))
                    st.markdown(f"<span style='color:{status_color}; font-weight:600'>{status_label}</span>", unsafe_allow_html=True)
                with right:
                    st.markdown("**AI Analysis**")
                    st.info(reason)
                    st.caption(explanation)

        # Donut chart for current bill
        if px and len(charges) > 1:
            st.markdown("---")
            st.markdown("#### Bill Distribution")
            bill_items = {k: v for k, v in charges.items() if k != "total" and v > 0}
            if bill_items:
                fig_donut = px.pie(
                    values=list(bill_items.values()),
                    names=[k.title() for k in bill_items.keys()],
                    hole=0.6,
                    color_discrete_sequence=["#4f8ef7", "#00c48c", "#ff9f40", "#ff4b4b"],
                    template="plotly_dark"
                )
                fig_donut.update_traces(textposition="outside", textinfo="percent+label")
                fig_donut.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(family="DM Sans", color="#e8eaf0"),
                    showlegend=False,
                    margin=dict(t=20, b=20, l=20, r=20),
                    height=340
                )
                st.plotly_chart(fig_donut, use_container_width=True)

    # ───────── TAB 2: HISTORY ─────────
    with tab_history:
        if not df_all.empty:
            st.markdown("#### Spending Over Time")

            if px:
                fig_line = px.line(
                    df_all,
                    x="timestamp",
                    y="value",
                    color="charge",
                    markers=True,
                    template="plotly_dark",
                    color_discrete_sequence=["#4f8ef7", "#00c48c", "#ff9f40", "#ff4b4b", "#c77dff"],
                    labels={"charge": "Utility", "value": "Cost (€)", "timestamp": "Date"}
                )
                fig_line.update_traces(line=dict(width=2.5), marker=dict(size=7))
                fig_line.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(family="DM Sans", color="#e8eaf0"),
                    legend=dict(bgcolor="rgba(0,0,0,0)"),
                    xaxis=dict(gridcolor="#2a2d36", showgrid=True),
                    yaxis=dict(gridcolor="#2a2d36", showgrid=True),
                    margin=dict(t=20, b=20),
                    height=360
                )
                st.plotly_chart(fig_line, use_container_width=True)

                # Spending split
                st.markdown("#### Cumulative Spending Split")
                fig_pie = px.pie(
                    df_all,
                    values="value",
                    names="charge",
                    hole=0.5,
                    color_discrete_sequence=["#4f8ef7", "#00c48c", "#ff9f40", "#ff4b4b"],
                    template="plotly_dark"
                )
                fig_pie.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    font=dict(family="DM Sans", color="#e8eaf0"),
                    margin=dict(t=20, b=20),
                    height=320
                )
                st.plotly_chart(fig_pie, use_container_width=True)
            else:
                st.line_chart(df_all.set_index("timestamp")["value"])

            st.markdown("#### Recent Records")
            display_df = df_all.sort_values("timestamp", ascending=False).copy()
            display_df["timestamp"] = display_df["timestamp"].dt.strftime("%Y-%m-%d %H:%M")
            display_df.columns = [c.title() for c in display_df.columns]
            st.dataframe(display_df, use_container_width=True, hide_index=True)

        else:
            st.info("No historical data yet. Upload a bill to get started.")

else:
    # ───────── EMPTY STATE ─────────
    st.markdown("""
        <div style='text-align:center; padding: 60px 20px;'>
            <div style='font-size: 3.5rem; margin-bottom: 16px'>⚡</div>
            <h3 style='color:#c8cbda; margin-bottom: 8px'>Upload a utility bill to begin</h3>
            <p style='color:#7a7f8e; max-width: 420px; margin: 0 auto'>
                Supports PDF and plain text files. Your data is stored locally and never leaves your machine.
            </p>
        </div>
    """, unsafe_allow_html=True)

    if not df_all.empty:
        st.markdown("---")
        st.markdown("#### Last Known Trends")
        if px:
            fig = px.line(
                df_all, x="timestamp", y="value", color="charge",
                markers=True, template="plotly_dark",
                color_discrete_sequence=["#4f8ef7", "#00c48c", "#ff9f40"],
                labels={"charge": "Utility", "value": "Cost (€)"}
            )
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(family="DM Sans", color="#e8eaf0"),
                xaxis=dict(gridcolor="#2a2d36"),
                yaxis=dict(gridcolor="#2a2d36"),
                height=320
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.line_chart(df_all.set_index("timestamp")["value"])