"""Reusable KPI Card component renderer for Streamlit UI."""

import streamlit as st


def render_kpi_card(
    title: str,
    value: str,
    subtext: str = "",
    accent_color: str = "#E10600"
):
    """Render a styled F1 racing KPI card using HTML markdown."""
    card_html = f"""
    <div class="f1-kpi-card" style="border-top-color: {accent_color};">
        <div class="f1-kpi-label">{title}</div>
        <div class="f1-kpi-value">{value}</div>
        {"<div class='f1-kpi-subtext'>" + subtext + "</div>" if subtext else ""}
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)


def render_insight_box(text: str, title: str = "STRATEGIC INSIGHT"):
    """Render a highlighted analytical insight box."""
    box_html = f"""
    <div class="f1-insight-box">
        <strong style="color: #E10600; text-transform: uppercase; letter-spacing: 0.5px;">💡 {title}:</strong><br/>
        {text}
    </div>
    """
    st.markdown(box_html, unsafe_allow_html=True)
