import streamlit as st
import pandas as pd


def render_filters(df: pd.DataFrame) -> pd.DataFrame:
    """Renders interactive sidebar filters and returns filtered dataset."""
    st.sidebar.title("⚙️ Dashboard Filters")

    if st.sidebar.button("🔄 Refresh Data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

    st.sidebar.divider()

    if df.empty or "Payment_Method" not in df.columns:
        return df

    # Payment Method Multiselect
    payment_options = sorted(df["Payment_Method"].dropna().unique().tolist())
    selected_payments = st.sidebar.multiselect(
        "Filter by Payment Method:",
        options=payment_options,
        default=payment_options,
    )

    # Filter dataframe
    filtered_df = df[df["Payment_Method"].isin(selected_payments)]

    return filtered_df
