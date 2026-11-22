import streamlit as st
from data_loader import load_sales_data
from filters import render_filters
from charts import plot_weekly_evolution
from metrics import (
    get_total_orders,
    get_total_revenue,
    get_total_profit,
    get_average_ticket,
    get_monthly_kpi,
    get_weekly_orders_kpi,
    get_total_flour_kg,
    get_weekly_flour_kpi,
)

# Page configuration
st.set_page_config(
    page_title="Bakery Executive Dashboard",
    page_icon="🥖",
    layout="wide",
)

# 1. Load Data
df_raw = load_sales_data()

# 2. Render Sidebar Filters
df_filtered = render_filters(df_raw)

# 3. Page Navigation
st.sidebar.divider()
page = st.sidebar.radio(
    "📌 Navigation:",
    options=["📊 Sales & Overview", "🍞 Inventory Management"]
)

# ==============================================================================
# PAGE 1: SALES & OVERVIEW
# ==============================================================================
if page == "📊 Sales & Overview":
    st.title("🥖 Bakery Business Analytics — Overview")
    st.caption("Real-time executive metrics, revenue tracking, and performance indicators.")

    # --- PERFORMANCE TARGETS ---
    st.subheader("🔥 Performance Indicators")
    col_m1, col_m2, col_m3 = st.columns(3)

    with col_m1:
        st.markdown("**Weekly Order Target**")
        curr_week, record_week = get_weekly_orders_kpi(df_filtered)
        progress = min(curr_week / record_week, 1.0)
        st.progress(progress)

        if curr_week >= record_week and record_week > 1:
            st.caption(f"🎉 **{curr_week}** of {record_week} orders (New All-Time High!)")
        else:
            st.caption(f"**{curr_week}** of {record_week} orders (Historical Target)")

    with col_m2:
        curr_profit, prev_profit = get_monthly_kpi(df_filtered, "Profit")
        st.metric(
            label="Month-to-Date Profit",
            value=f"${curr_profit:,.2f}",
            delta=f"${curr_profit - prev_profit:,.2f}"
        )

    with col_m3:
        curr_rev, prev_rev = get_monthly_kpi(df_filtered, "Revenue")
        st.metric(
            label="Month-to-Date Revenue",
            value=f"${curr_rev:,.2f}",
            delta=f"${curr_rev - prev_rev:,.2f}"
        )

    st.divider()

    # --- MAIN FINANCIAL METRICS ---
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Orders", get_total_orders(df_filtered))

    with col2:
        st.metric("Total Revenue", f"${get_total_revenue(df_filtered):,.2f}")

    with col3:
        st.metric("Total Profit", f"${get_total_profit(df_filtered):,.2f}")

    with col4:
        st.metric("Average Ticket", f"${get_average_ticket(df_filtered):,.2f}")

    # --- VISUAL ANALYTICS ---
    st.divider()
    st.subheader("📊 Visual Analytics & Trends")

    tab1, tab2, tab3 = st.tabs(["Revenue", "Profit", "Order Volume"])

    with tab1:
        plot_weekly_evolution(
            df_filtered, y_col="Revenue", title="Weekly Revenue ($)", color="#F4A460"
        )

    with tab2:
        plot_weekly_evolution(
            df_filtered, y_col="Profit", title="Weekly Profit ($)", color="#2E8B57"
        )

    with tab3:
        plot_weekly_evolution(
            df_filtered, y_col="Quantity", title="Weekly Units Sold", color="#4682B4"
        )

# ==============================================================================
# PAGE 2: INVENTORY MANAGEMENT
# ==============================================================================
elif page == "🍞 Inventory Management":
    st.title("🍞 Raw Material Management — White Flour")
    st.info("Weekly tracking of key raw materials to support procurement and demand forecasting.")

    col_inv1, col_inv2, col_inv3 = st.columns(3)

    curr_flour_week, prev_flour_week = get_weekly_flour_kpi(df_filtered)
    diff_flour = curr_flour_week - prev_flour_week

    with col_inv1:
        st.metric(
            label="Current Week Consumption",
            value=f"{curr_flour_week:,.2f} kg",
            delta=f"{diff_flour:,.2f} kg vs previous week"
        )

    with col_inv2:
        total_kg = get_total_flour_kg(df_filtered)
        st.metric(
            label="Total Period Consumption",
            value=f"{total_kg:,.2f} kg"
        )

    with col_inv3:
        bags_5kg = total_kg / 5.0
        st.metric(
            label="Equivalent 5 kg Bags",
            value=f"{bags_5kg:,.1f} bags"
        )

    st.divider()

    st.subheader("📈 Weekly Consumption Trend — White Flour (kg)")

    plot_weekly_evolution(
        df_filtered,
        y_col="Total_Flour_KG",
        title="Weekly White Flour Consumption (kg)",
        color="#D2B48C"
    )

    st.caption("💡 **Scalability Note:** This module can easily be extended to monitor other ingredients (e.g., sugar, yeast, butter) by adding corresponding columns to the recipe matrix.")
