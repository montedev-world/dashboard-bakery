import pandas as pd
import plotly.express as px
import streamlit as st


def plot_weekly_evolution(df: pd.DataFrame, y_col: str, title: str, color: str) -> None:
    """Generates a styled weekly grouped bar chart using Plotly."""
    if df.empty or "Date" not in df.columns:
        st.info("No data available to display chart.")
        return

    df_temp = df.set_index("Date")
    df_weekly = df_temp.resample("W-SAT")[y_col].sum().reset_index()

    fig = px.bar(
        df_weekly,
        x="Date",
        y=y_col,
        title=title,
        template="plotly_dark",
        text_auto=".2s",
    )

    fig.update_traces(marker_color=color)
    fig.update_layout(
        xaxis_title="Week Ending",
        yaxis_title=title,
        xaxis=dict(tickformat="%b %d, %Y"),
        margin=dict(l=20, r=20, t=40, b=20),
    )

    st.plotly_chart(fig, use_container_width=True)
