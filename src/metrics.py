import pandas as pd


def get_total_orders(df: pd.DataFrame) -> int:
    return len(df)


def get_total_revenue(df: pd.DataFrame) -> float:
    return float(df["Revenue"].sum()) if not df.empty else 0.0


def get_total_profit(df: pd.DataFrame) -> float:
    return float(df["Profit"].sum()) if not df.empty else 0.0


def get_average_ticket(df: pd.DataFrame) -> float:
    orders = get_total_orders(df)
    return get_total_revenue(df) / orders if orders > 0 else 0.0


def get_monthly_kpi(df: pd.DataFrame, column: str) -> tuple[float, float]:
    """Calculates cumulative sum for current month vs previous month."""
    if df.empty or "Date" not in df.columns:
        return 0.0, 0.0

    latest_date = df["Date"].max()
    curr_month, curr_year = latest_date.month, latest_date.year

    if curr_month == 1:
        prev_month, prev_year = 12, curr_year - 1
    else:
        prev_month, prev_year = curr_month - 1, curr_year

    df_curr = df[(df["Date"].dt.month == curr_month) & (df["Date"].dt.year == curr_year)]
    df_prev = df[(df["Date"].dt.month == prev_month) & (df["Date"].dt.year == prev_year)]

    return float(df_curr[column].sum()), float(df_prev[column].sum())


def get_weekly_orders_kpi(df: pd.DataFrame) -> tuple[int, int]:
    """Returns (current_week_orders, all_time_weekly_record)."""
    if df.empty or "Date" not in df.columns:
        return 0, 1

    weekly_orders = df.set_index("Date").resample("W-SAT")["Quantity"].sum()
    if weekly_orders.empty:
        return 0, 1

    current_week = int(weekly_orders.iloc[-1])
    record_week = int(weekly_orders.max())

    return current_week, max(record_week, 1)


def get_total_flour_kg(df: pd.DataFrame) -> float:
    return float(df["Total_Flour_KG"].sum()) if "Total_Flour_KG" in df.columns else 0.0


def get_weekly_flour_kpi(df: pd.DataFrame) -> tuple[float, float]:
    """Returns (current_week_flour_kg, previous_week_flour_kg)."""
    if df.empty or "Total_Flour_KG" not in df.columns:
        return 0.0, 0.0

    weekly_flour = df.set_index("Date").resample("W-SAT")["Total_Flour_KG"].sum()
    if weekly_flour.empty:
        return 0.0, 0.0

    current_week = float(weekly_flour.iloc[-1])
    prev_week = float(weekly_flour.iloc[-2]) if len(weekly_flour) > 1 else 0.0

    return current_week, prev_week
