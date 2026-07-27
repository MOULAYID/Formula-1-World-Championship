"""Reusable Plotly chart builders for Formula 1 dashboard visualizations."""

from typing import List, Optional
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys

from src.utils.helpers import apply_f1_plotly_theme, F1_COLORS


def build_driver_radar_chart(driver_stats_df: pd.DataFrame, selected_drivers: List[str]) -> go.Figure:
    """Build a multi-axis Radar chart comparing selected driver career statistics."""
    df_sel = driver_stats_df[driver_stats_df["driver_name"].isin(selected_drivers)].copy()
    
    categories = ["Win Rate", "Podium Rate", "Pole Rate", "Teammate H2H", "DPS Score"]
    
    fig = go.Figure()
    
    colors = [F1_COLORS["red"], F1_COLORS["cyan"], F1_COLORS["gold"], F1_COLORS["orange"], "#0090FF"]

    for idx, (_, row) in enumerate(df_sel.iterrows()):
        values = [
            row["win_rate"] * 100.0,
            row["podium_rate"] * 100.0,
            row["pole_rate"] * 100.0,
            row["teammate_h2h_win_rate"] * 100.0,
            row["driver_performance_score"],
        ]
        # Close the loop
        values.append(values[0])
        cats = categories + [categories[0]]
        
        color = colors[idx % len(colors)]
        
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=cats,
            fill='toself',
            name=row["driver_name"],
            line=dict(color=color, width=2),
            opacity=0.6,
        ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100], gridcolor="#232A36", color=F1_COLORS["text_secondary"]),
            angularaxis=dict(gridcolor="#232A36", color=F1_COLORS["text_primary"]),
            bgcolor="rgba(15, 20, 30, 0.6)",
        ),
        showlegend=True,
    )
    return apply_f1_plotly_theme(fig, "Driver Performance Radar Comparison", height=450)


def build_goat_scatter_matrix(driver_stats_df: pd.DataFrame) -> go.Figure:
    """Build Driver Performance Score vs Career Win Rate scatter matrix."""
    fig = px.scatter(
        driver_stats_df,
        x="win_rate",
        y="driver_performance_score",
        size="wins",
        color="championships",
        hover_name="driver_name",
        hover_data=["total_starts", "podiums", "teammate_h2h_win_rate"],
        color_continuous_scale="Reds",
        labels={
            "win_rate": "Win Rate",
            "driver_performance_score": "Driver Performance Score (DPS)",
            "championships": "Titles",
        },
    )
    
    # Highlight legendary drivers text
    legends = ["Lewis Hamilton", "Michael Schumacher", "Ayrton Senna", "Max Verstappen", "Juan Fangio", "Fernando Alonso", "Sebastian Vettel", "Alain Prost"]
    df_leg = driver_stats_df[driver_stats_df["driver_name"].isin(legends)]
    for _, row in df_leg.iterrows():
        fig.add_annotation(
            x=row["win_rate"],
            y=row["driver_performance_score"],
            text=row["driver_name"],
            showarrow=True,
            arrowhead=2,
            arrowcolor=F1_COLORS["red"],
            font=dict(size=11, color="#FFFFFF"),
        )

    return apply_f1_plotly_theme(fig, "The GOAT Debate Matrix: DPS vs Win Rate", height=500)


def build_era_win_share_chart(master_df: pd.DataFrame) -> go.Figure:
    """Build era win share breakdown stacked bar chart for top constructors."""
    wins_df = master_df[master_df["is_win"] == 1].groupby(["era", "constructor_name"]).size().reset_index(name="wins")
    
    # Keep top 8 constructors overall
    top_constructors = master_df[master_df["is_win"] == 1]["constructor_name"].value_counts().head(8).index.tolist()
    wins_df["constructor_group"] = wins_df["constructor_name"].apply(lambda x: x if x in top_constructors else "Others")
    
    wins_grouped = wins_df.groupby(["era", "constructor_group"])["wins"].sum().reset_index()

    fig = px.bar(
        wins_grouped,
        x="era",
        y="wins",
        color="constructor_group",
        title="Constructor Race Wins Distribution by Era",
        color_discrete_sequence=px.colors.qualitative.Bold,
        barmode="stack",
    )
    return apply_f1_plotly_theme(fig, "Constructor Wins Share Across F1 Eras", height=450)


def build_circuits_map(circuits_df: pd.DataFrame) -> go.Figure:
    """Build global interactive Mapbox scatter plot for circuits."""
    fig = px.scatter_mapbox(
        circuits_df,
        lat="lat",
        lon="lng",
        hover_name="circuit_name",
        hover_data=["location", "circuit_country", "total_races", "circuit_difficulty_score"],
        size="total_races",
        color="circuit_difficulty_score",
        color_continuous_scale="OrRd",
        size_max=25,
        zoom=1,
        mapbox_style="carto-darkmatter",
    )
    fig.update_layout(
        margin=dict(l=0, r=0, t=30, b=0),
        height=500,
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#FFFFFF"),
    )
    return fig


def build_grid_vs_finish_scatter(master_df: pd.DataFrame) -> go.Figure:
    """Scatter plot with trendline comparing starting grid to final race finish."""
    sample_df = master_df[(master_df["grid"] > 0) & (master_df["positionOrder"] > 0)].sample(n=min(3000, len(master_df)), random_state=42)
    
    fig = px.scatter(
        sample_df,
        x="grid",
        y="positionOrder",
        color="is_podium",
        hover_name="driver_name",
        hover_data=["race_name", "year", "constructor_name"],
        color_discrete_map={1: F1_COLORS["gold"], 0: F1_COLORS["text_secondary"]},
        labels={"grid": "Grid Position (Qualifying)", "positionOrder": "Final Finish Position"},
        opacity=0.5,
    )
    
    # Add diagonal baseline (Grid == Finish)
    fig.add_trace(go.Scatter(
        x=[1, 24],
        y=[1, 24],
        mode="lines",
        name="No Position Change",
        line=dict(color=F1_COLORS["red"], dash="dash", width=2)
    ))

    return apply_f1_plotly_theme(fig, "Grid Position vs Final Race Outcome", height=480)
