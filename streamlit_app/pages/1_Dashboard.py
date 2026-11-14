
import streamlit as st
import pandas as pd
from pathlib import Path

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Delivery Analytics Dashboard",
    page_icon="📊",
    layout="wide"
)

# ---------------- CUSTOM STYLE ----------------
st.markdown("""
<style>
.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
    max-width: 1400px;
}
h1 {
    font-weight: 800;
}
[data-testid="stMetric"] {
    background-color: rgba(128,128,128,0.08);
    padding: 18px;
    border-radius: 12px;
}
</style>
""", unsafe_allow_html=True)

# ---------------- DATA LOADING ----------------
BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "archive"

@st.cache_data
def load_data():
    orders = pd.read_csv(DATA_DIR / "olist_orders_dataset.csv")
    customers = pd.read_csv(DATA_DIR / "olist_customers_dataset.csv")

    df = orders.merge(
        customers[["customer_id", "customer_state"]],
        on="customer_id",
        how="left"
    )

    df["order_purchase_timestamp"] = pd.to_datetime(
        df["order_purchase_timestamp"], errors="coerce"
    )

    df["order_delivered_customer_date"] = pd.to_datetime(
        df["order_delivered_customer_date"], errors="coerce"
    )

    df["order_estimated_delivery_date"] = pd.to_datetime(
        df["order_estimated_delivery_date"], errors="coerce"
    )

    # Keep delivered orders with valid dates
    df = df[
        (df["order_status"] == "delivered") &
        (df["order_delivered_customer_date"].notna()) &
        (df["order_estimated_delivery_date"].notna()) &
        (df["order_purchase_timestamp"].notna())
    ].copy()

    # Target
    df["late_delivery"] = (
        df["order_delivered_customer_date"] >
        df["order_estimated_delivery_date"]
    ).astype(int)

    df["purchase_year"] = df["order_purchase_timestamp"].dt.year
    df["purchase_month"] = df["order_purchase_timestamp"].dt.month

    df["month"] = (
        df["order_purchase_timestamp"].dt.to_period("M").astype(str)
    )

    df["delivery_status"] = df["late_delivery"].map({
        0: "On Time",
        1: "Late"
    })

    return df


try:
    df = load_data()
except Exception as e:
    st.error(f"Could not load dataset: {e}")
    st.stop()

# ---------------- HEADER ----------------
st.title("📊 Delivery Analytics Dashboard")
st.caption("Olist E-commerce | Late Delivery Analysis")

st.divider()

# ---------------- SIDEBAR FILTERS ----------------
st.sidebar.header("🔎 Dashboard Filters")

years = sorted(df["purchase_year"].dropna().unique())

selected_years = st.sidebar.multiselect(
    "Purchase Year",
    options=years,
    default=years
)

states = sorted(df["customer_state"].dropna().unique())

selected_states = st.sidebar.multiselect(
    "Customer State",
    options=states,
    default=states
)

filtered_df = df[
    df["purchase_year"].isin(selected_years) &
    df["customer_state"].isin(selected_states)
].copy()

if filtered_df.empty:
    st.warning("No data available for the selected filters.")
    st.stop()

# ---------------- KPIs ----------------
total_orders = len(filtered_df)
late_orders = int(filtered_df["late_delivery"].sum())
on_time_orders = total_orders - late_orders

late_rate = late_orders / total_orders * 100
on_time_rate = on_time_orders / total_orders * 100

st.subheader("📌 Key Performance Indicators")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Delivered Orders", f"{total_orders:,}")
col2.metric("Late Orders", f"{late_orders:,}")
col3.metric("On-Time Orders", f"{on_time_orders:,}")
col4.metric("Late Delivery Rate", f"{late_rate:.2f}%")

st.divider()

# ---------------- DELIVERY DISTRIBUTION ----------------
st.subheader("📦 Delivery Performance")

col1, col2 = st.columns(2)

with col1:
    st.markdown("**On-Time vs Late Orders**")

    delivery_counts = (
        filtered_df["delivery_status"]
        .value_counts()
        .reindex(["On Time", "Late"], fill_value=0)
    )

    st.bar_chart(delivery_counts)

with col2:
    st.markdown("**Delivery Status Distribution**")

    distribution = pd.DataFrame({
        "Orders": [on_time_orders, late_orders]
    }, index=["On Time", "Late"])

    st.bar_chart(distribution)

st.divider()

# ---------------- MONTHLY ANALYSIS ----------------
st.subheader("📅 Monthly Late Delivery Trend")

monthly = (
    filtered_df.groupby("month")
    .agg(
        total_orders=("late_delivery", "count"),
        late_orders=("late_delivery", "sum")
    )
    .reset_index()
)

monthly["late_rate"] = (
    monthly["late_orders"] / monthly["total_orders"] * 100
)

col1, col2 = st.columns(2)

with col1:
    st.markdown("**Monthly Late Delivery Rate (%)**")
    st.line_chart(
        monthly,
        x="month",
        y="late_rate"
    )

with col2:
    st.markdown("**Monthly Order Volume**")
    st.bar_chart(
        monthly,
        x="month",
        y="total_orders"
    )

st.divider()

# ---------------- STATE ANALYSIS ----------------
st.subheader("🗺️ Late Deliveries by Customer State")

state_analysis = (
    filtered_df.groupby("customer_state")
    .agg(
        total_orders=("late_delivery", "count"),
        late_orders=("late_delivery", "sum")
    )
    .reset_index()
)

state_analysis["late_rate"] = (
    state_analysis["late_orders"] /
    state_analysis["total_orders"] * 100
)

state_analysis = state_analysis.sort_values(
    "late_rate", ascending=False
)

col1, col2 = st.columns([1.5, 1])

with col1:
    st.markdown("**States with Highest Late Delivery Rates**")
    st.bar_chart(
        state_analysis.head(10),
        x="customer_state",
        y="late_rate"
    )

with col2:
    st.markdown("**State Performance Table**")
    st.dataframe(
        state_analysis.rename(columns={
            "customer_state": "State",
            "total_orders": "Total Orders",
            "late_orders": "Late Orders",
            "late_rate": "Late Rate (%)"
        }).round(2),
        use_container_width=True,
        hide_index=True
    )

st.divider()

# ---------------- RAW DATA ----------------
st.subheader("📋 Order Data Explorer")

show_data = st.checkbox("Show filtered order data")

if show_data:
    st.dataframe(
        filtered_df[
            [
                "order_id",
                "customer_state",
                "order_purchase_timestamp",
                "order_delivered_customer_date",
                "order_estimated_delivery_date",
                "delivery_status"
            ]
        ],
        use_container_width=True,
        hide_index=True
    )

# ---------------- FOOTER ----------------
st.caption(
    "Olist E-commerce Dataset | Delivery Analytics & Late Delivery Analysis"
)
