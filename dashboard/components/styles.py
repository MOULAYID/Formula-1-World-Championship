"""Custom CSS styling tokens and layout rules for Formula 1 Dark Racing theme."""

import streamlit as st


def inject_f1_custom_css():
    """Inject custom CSS rules into Streamlit head for F1 dark racing aesthetic."""
    css = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&family=Titillium+Web:ital,wght@0,400;0,700;1,400&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        background-color: #0B0E14;
        color: #F1F5F9;
    }

    /* Streamlit Main Container Background */
    .stApp {
        background: linear-gradient(180deg, #0B0E14 0%, #111622 100%);
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #11151F !important;
        border-right: 1px solid #232A36;
    }

    /* Header Banner */
    .f1-header-title {
        font-family: 'Titillium Web', sans-serif;
        font-weight: 800;
        font-size: 2.2rem;
        letter-spacing: -0.5px;
        color: #FFFFFF;
        margin-bottom: 0px;
        text-transform: uppercase;
        display: flex;
        align-items: center;
        gap: 12px;
    }
    
    .f1-header-accent {
        color: #E10600;
    }

    .f1-subtitle {
        font-size: 0.95rem;
        color: #94A3B8;
        margin-top: 4px;
        margin-bottom: 24px;
    }

    /* Glassmorphism KPI Card */
    .f1-kpi-card {
        background: rgba(21, 25, 34, 0.85);
        border: 1px solid #232A36;
        border-top: 3px solid #E10600;
        border-radius: 10px;
        padding: 16px 20px;
        margin-bottom: 16px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.35);
        transition: transform 0.2s ease, border-color 0.2s ease;
    }

    .f1-kpi-card:hover {
        transform: translateY(-2px);
        border-color: #E10600;
    }

    .f1-kpi-label {
        font-size: 0.78rem;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        color: #94A3B8;
        font-weight: 600;
        margin-bottom: 6px;
    }

    .f1-kpi-value {
        font-family: 'Titillium Web', sans-serif;
        font-size: 1.85rem;
        font-weight: 700;
        color: #FFFFFF;
        line-height: 1.2;
    }

    .f1-kpi-subtext {
        font-size: 0.75rem;
        color: #00D2BE;
        margin-top: 4px;
        font-weight: 500;
    }

    /* Insights Box */
    .f1-insight-box {
        background: rgba(225, 6, 0, 0.08);
        border-left: 4px solid #E10600;
        border-radius: 6px;
        padding: 14px 18px;
        margin: 16px 0;
        color: #F1F5F9;
        font-size: 0.9rem;
        line-height: 1.5;
    }

    /* Streamlit Metric Overrides */
    div[data-testid="stMetricValue"] {
        font-family: 'Titillium Web', sans-serif;
        font-size: 1.8rem !important;
        color: #FFFFFF !important;
    }

    /* Selectbox and Filter Styling */
    div[data-baseweb="select"] {
        background-color: #151922 !important;
        border-color: #232A36 !important;
    }
    
    /* Table Header Styling */
    .dataframe {
        border-collapse: collapse !important;
        width: 100% !important;
        background-color: #151922 !important;
    }

    .dataframe th {
        background-color: #1E2430 !important;
        color: #E10600 !important;
        font-family: 'Titillium Web', sans-serif !important;
        font-size: 0.9rem !important;
        padding: 10px !important;
    }
    
    .dataframe td {
        color: #F1F5F9 !important;
        padding: 8px !important;
        border-bottom: 1px solid #232A36 !important;
    }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


def render_f1_sidebar():
    """Render unified F1 sidebar branding across all Streamlit pages."""
    with st.sidebar:
        st.image("https://upload.wikimedia.org/wikipedia/commons/3/33/F1.svg", width=120)
        st.markdown("### 🏎️ **F1 Intelligence Nav**")
        st.markdown("Select a page above to explore performance analytics.")
        st.divider()
        st.caption("Data Source: Kaggle F1 World Championship Dataset (1950–Present)")
        st.caption("Built with Python, Scikit-Learn, Plotly & Streamlit")
