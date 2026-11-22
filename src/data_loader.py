import time
import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
SPREADSHEET_ID = st.secrets["spreadsheet_id"]
# Right above we can see that I purposefully hide the link ID 
# of the google sheets, which is good habit for privacy reasons.


@st.cache_data(ttl=300)
def load_sales_data() -> pd.DataFrame:
    """
    Connects to Google Sheets with connection retry logic, loads sales data from 'DAILY SALES',
    and performs robust ETL operations.
    """
    service_account_info = dict(st.secrets["gcp_service_account"])
    credentials = Credentials.from_service_account_info(
        service_account_info, scopes=SCOPES
    )

    client = None
    spreadsheet = None
    for attempt in range(3):
        try:
            client = gspread.authorize(credentials)
            spreadsheet = client.open_by_key(SPREADSHEET_ID)
            break
        except Exception:
            if attempt == 2:
                st.error("⚠️ Connection error with Google Sheets. Please refresh the page.")
                return pd.DataFrame()
            time.sleep(1)

    # 1. Leitura da aba 'DAILY SALES'
    worksheet = None
    for tab_name in ["DAILY SALES", "Daily Sales", "Sales", "Vendas"]:
        try:
            worksheet = spreadsheet.worksheet(tab_name)
            break
        except Exception:
            continue

    if worksheet is None:
        worksheet = spreadsheet.get_worksheet(0)

    raw_data = worksheet.get_all_values()

    if not raw_data or len(raw_data) <= 1:
        return pd.DataFrame()

    # Normaliza cabeçalhos: remove espaços extras e converte para caixa alta
    headers = [str(h).strip().upper() for h in raw_data[0]]
    df = pd.DataFrame(raw_data[1:], columns=headers)
    df = df.loc[:, [c for c in df.columns if c != ""]]

    # Mapeamento exato dos cabeçalhos da sua planilha
    col_mapping = {
        "DATE": "Date",
        "CLIENT": "Client",
        "PRODUCT": "Product",
        "QUANTITY": "Quantity",
        "PRICE": "Price",
        "COST": "Cost",
        "METHOD OF PAYMENT": "Payment_Method",
        "METHOD_OF_PAYMENT": "Payment_Method",
    }
    df = df.rename(columns=col_mapping)

    # Garante a existência de todas as colunas essenciais
    for col in ["Date", "Client", "Product", "Quantity", "Price", "Cost", "Payment_Method"]:
        if col not in df.columns:
            df[col] = 0.0 if col in ["Price", "Cost", "Quantity"] else ""

    # Filtra linhas sem produto registrado
    df = df[df["Product"].astype(str).str.strip() != ""]

    # Limpeza e conversão monetária
    for col in ["Price", "Cost"]:
        df[col] = (
            df[col]
            .astype(str)
            .str.replace("R$", "", regex=False)
            .str.replace("$", "", regex=False)
            .str.replace(" ", "", regex=False)
            .str.replace(",", ".", regex=False)
        )
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)

    df["Quantity"] = pd.to_numeric(df["Quantity"], errors="coerce").fillna(1).astype(int)
    df["Date"] = pd.to_datetime(df["Date"], dayfirst=True, errors="coerce")
    df = df.dropna(subset=["Date"])

    # Métricas calculadas
    df["Revenue"] = df["Price"]
    df["Total_Cost"] = df["Cost"]
    df["Profit"] = df["Revenue"] - df["Total_Cost"]

    # 2. Leitura da aba de Produtos / Receitas (se existir)
    try:
        prod_sheet = None
        for p_tab in ["PRODUCTS", "Produtos", "RECIPES"]:
            try:
                prod_sheet = spreadsheet.worksheet(p_tab)
                break
            except Exception:
                continue

        if prod_sheet:
            raw_prod = prod_sheet.get_all_values()
            if raw_prod and len(raw_prod) > 1:
                p_headers = [str(h).strip().upper() for h in raw_prod[0]]
                df_prod = pd.DataFrame(raw_prod[1:], columns=p_headers)
                df_prod = df_prod.loc[:, [c for c in df_prod.columns if c != ""]]

                p_col = [c for c in df_prod.columns if "PROD" in c]
                f_col = [c for c in df_prod.columns if "WHITE FLOUR (GRAMS)" in c or "FARINHA" in c]

                if p_col and f_col:
                    df_prod = df_prod.rename(
                        columns={p_col[0]: "Product", f_col[0]: "Flour_Grams"}
                    )
                    df_prod["Flour_Grams"] = (
                        df_prod["Flour_Grams"]
                        .astype(str)
                        .str.replace("g", "", regex=False)
                        .str.replace(",", ".", regex=False)
                    )
                    df_prod["Flour_Grams"] = pd.to_numeric(
                        df_prod["Flour_Grams"], errors="coerce"
                    ).fillna(0.0)

                    df = df.merge(df_prod[["Product", "Flour_Grams"]], on="Product", how="left")
                    df["Flour_Grams"] = df["Flour_Grams"].fillna(0.0)
                else:
                    df["Flour_Grams"] = 0.0
            else:
                df["Flour_Grams"] = 0.0
        else:
            df["Flour_Grams"] = 0.0
    except Exception:
        df["Flour_Grams"] = 0.0

    # Métrica de consumo de farinha
    df["Total_Flour_Grams"] = df["Flour_Grams"] * df["Quantity"]
    df["Total_Flour_KG"] = df["Total_Flour_Grams"] / 1000.0

    return df
