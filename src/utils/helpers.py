"""Utility functions, F1 color themes, and Plotly layout formatters."""

from typing import Dict, Any
import plotly.graph_objects as go


# Formula 1 Official & Team Color Palette
F1_COLORS = {
    "red": "#E10600",
    "dark_bg": "#0B0E14",
    "card_bg": "#151922",
    "card_border": "#232A36",
    "text_primary": "#FFFFFF",
    "text_secondary": "#94A3B8",
    "gold": "#FFD700",
    "cyan": "#00D2BE",
    "orange": "#FF8700",
    "ferrari": "#DC0000",
    "mercedes": "#00D2BE",
    "redbull": "#1E41FF",
    "mclaren": "#FF8700",
    "williams": "#005AFF",
    "aston_martin": "#006F62",
    "alpine": "#0090FF",
}


def apply_f1_plotly_theme(fig: go.Figure, title: str = "", height: int = 450) -> go.Figure:
    """Apply consistent F1 dark racing theme to a Plotly figure."""
    fig.update_layout(
        title=dict(
            text=f"<b>{title}</b>" if title else "",
            font=dict(family="Titillium Web, sans-serif", size=18, color=F1_COLORS["text_primary"]),
            x=0.01,
            y=0.95,
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(15, 20, 30, 0.6)",
        font=dict(family="Inter, sans-serif", color=F1_COLORS["text_secondary"], size=12),
        margin=dict(l=40, r=40, t=60, b=40),
        height=height,
        xaxis=dict(
            gridcolor="#1E2638",
            zerolinecolor="#232A36",
            tickfont=dict(color=F1_COLORS["text_secondary"]),
            title_font=dict(color=F1_COLORS["text_primary"]),
        ),
        yaxis=dict(
            gridcolor="#1E2638",
            zerolinecolor="#232A36",
            tickfont=dict(color=F1_COLORS["text_secondary"]),
            title_font=dict(color=F1_COLORS["text_primary"]),
        ),
        legend=dict(
            bgcolor="rgba(21, 25, 34, 0.8)",
            bordercolor=F1_COLORS["card_border"],
            borderwidth=1,
            font=dict(color=F1_COLORS["text_primary"]),
        ),
        hoverlabel=dict(
            bgcolor=F1_COLORS["card_bg"],
            font_size=13,
            font_family="Inter, sans-serif",
            font_color="#FFFFFF",
        ),
    )
    return fig


def format_kpi_value(value: Any, fmt_type: str = "number") -> str:
    """Format numeric values cleanly for KPI card rendering."""
    if value is None or (isinstance(value, float) and float("nan") == value):
        return "N/A"
    
    if fmt_type == "int":
        return f"{int(value):,}"
    elif fmt_type == "percent":
        return f"{float(value) * 100.0:.1f}%"
    elif fmt_type == "float":
        return f"{float(value):.2f}"
    elif fmt_type == "currency":
        return f"${float(value):,.0f}"
    else:
        return str(value)


def get_driver_flag_url(nationality: str) -> str:
    """Return flag icon emoji or indicator for driver nationality."""
    nat_flags = {
        "British": "🇬🇧",
        "German": "🇩🇪",
        "Brazilian": "🇧🇷",
        "French": "🇫🇷",
        "Italian": "🇮🇹",
        "Spanish": "🇪🇸",
        "Dutch": "🇳🇱",
        "Australian": "🇦🇺",
        "Finnish": "🇫🇮",
        "Austrian": "🇦🇹",
        "Argentine": "🇦🇷",
        "Canadian": "🇨🇦",
        "American": "🇺🇸",
        "Mexican": "🇲🇽",
        "Japanese": "🇯🇵",
    }
    return nat_flags.get(nationality, "🏁")
