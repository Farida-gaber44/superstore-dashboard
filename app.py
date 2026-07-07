# ============================================================
# Superstore Sales Dashboard — app.py
# Run with: streamlit run app.py
# ============================================================

import pandas as pd
import plotly.express as px
import streamlit as st

# ── PAGE CONFIG ──────────────────────────────────────────────
# Sets the browser tab title, icon, and layout width
st.set_page_config(
    page_title="Superstore Sales Dashboard",
    page_icon="📊",
    layout="wide"
)

# ── LOAD DATA ────────────────────────────────────────────────
# Cache the data so it doesn't reload on every interaction
@st.cache_data
def load_data():
    df = pd.read_csv("superstore_clean.csv", dtype={"Postal Code": str})
    df["Order Date"] = pd.to_datetime(df["Order Date"])
    df["Order Month"] = df["Order Date"].dt.to_period("M").astype(str)
    return df

df = load_data()

# ── SIDEBAR FILTERS ───────────────────────────────────────────
# Why: lets users slice the data without changing any code
st.sidebar.title("🔍 Filters")

regions = ["All"] + sorted(df["Region"].unique().tolist())
selected_region = st.sidebar.selectbox("Region", regions)

categories = ["All"] + sorted(df["Category"].unique().tolist())
selected_category = st.sidebar.selectbox("Category", categories)

years = ["All"] + sorted(df["Order Year"].unique().tolist())
selected_year = st.sidebar.selectbox("Year", years)

# Apply filters
filtered = df.copy()
if selected_region != "All":
    filtered = filtered[filtered["Region"] == selected_region]
if selected_category != "All":
    filtered = filtered[filtered["Category"] == selected_category]
if selected_year != "All":
    filtered = filtered[filtered["Order Year"] == selected_year]

# ── HEADER ───────────────────────────────────────────────────
st.title("📊 Superstore Sales Dashboard")
st.markdown("Interactive analysis of US retail sales across regions, categories, and time.")
st.markdown("---")

# ── KPI CARDS ────────────────────────────────────────────────
# Why: gives the user the most important numbers at a glance
total_sales   = filtered["Sales"].sum()
total_profit  = filtered["Profit"].sum()
total_orders  = filtered["Order ID"].nunique()
profit_margin = (total_profit / total_sales * 100) if total_sales > 0 else 0
loss_orders   = (filtered["Profit"] < 0).sum()

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("💰 Total Sales",    f"${total_sales:,.0f}")
col2.metric("📈 Total Profit",   f"${total_profit:,.0f}")
col3.metric("🛒 Unique Orders",  f"{total_orders:,}")
col4.metric("📉 Profit Margin",  f"{profit_margin:.1f}%")
col5.metric("⚠️ Loss Orders",    f"{loss_orders:,}")

st.markdown("---")

# ── SECTION 1: MONTHLY SALES TREND ───────────────────────────
# Why: shows seasonality and growth over time
st.subheader("📈 Monthly Sales Trend")

monthly = filtered.groupby("Order Month")["Sales"].sum().reset_index()
monthly = monthly.sort_values("Order Month")

fig_trend = px.line(
    monthly,
    x="Order Month", y="Sales",
    markers=True,
    title="Sales Over Time",
    labels={"Order Month": "Month", "Sales": "Sales ($)"},
    color_discrete_sequence=["#4f8ef7"]
)
fig_trend.update_layout(xaxis_tickangle=-45, height=350)
st.plotly_chart(fig_trend, use_container_width=True)

st.markdown("---")

# ── SECTION 2: REGIONAL & CATEGORY BREAKDOWN ─────────────────
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("🗺️ Sales & Profit by Region")
    # Why: bar chart makes comparison across 4 regions instant
    region_df = filtered.groupby("Region")[["Sales", "Profit"]].sum().reset_index()
    region_df = region_df.sort_values("Sales", ascending=False)
    fig_region = px.bar(
        region_df,
        x="Region", y=["Sales", "Profit"],
        barmode="group",
        color_discrete_sequence=["#4f8ef7", "#00c49a"],
        labels={"value": "$", "variable": "Metric"}
    )
    fig_region.update_layout(height=350)
    st.plotly_chart(fig_region, use_container_width=True)

with col_right:
    st.subheader("📦 Sales by Category")
    # Why: pie chart shows proportion share at a glance
    cat_df = filtered.groupby("Category")["Sales"].sum().reset_index()
    fig_cat = px.pie(
        cat_df,
        names="Category", values="Sales",
        color_discrete_sequence=["#4f8ef7", "#00c49a", "#f7914f"],
        hole=0.4
    )
    fig_cat.update_layout(height=350)
    st.plotly_chart(fig_cat, use_container_width=True)

st.markdown("---")

# ── SECTION 3: TOP & BOTTOM SUB-CATEGORIES ───────────────────
st.subheader("🏆 Sub-Category Profitability")
# Why: exposes which sub-categories are losing money — key business insight

subcat_df = filtered.groupby("Sub-Category")["Profit"].sum().reset_index()
subcat_df = subcat_df.sort_values("Profit", ascending=True)

# Color bars: red for loss, green for profit
colors = ["#e84040" if p < 0 else "#00c49a" for p in subcat_df["Profit"]]

fig_subcat = px.bar(
    subcat_df,
    x="Profit", y="Sub-Category",
    orientation="h",
    title="Profit by Sub-Category (red = loss)",
    labels={"Profit": "Profit ($)", "Sub-Category": ""},
    color="Profit",
    color_continuous_scale=["#e84040", "#ffffff", "#00c49a"],
    color_continuous_midpoint=0
)
fig_subcat.update_layout(height=500, showlegend=False)
st.plotly_chart(fig_subcat, use_container_width=True)

st.markdown("---")

# ── SECTION 4: TOP CUSTOMERS ─────────────────────────────────
st.subheader("👤 Top 10 Customers by Sales")

top_customers = (
    filtered.groupby("Customer Name")["Sales"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
    .reset_index()
)
fig_cust = px.bar(
    top_customers,
    x="Sales", y="Customer Name",
    orientation="h",
    color_discrete_sequence=["#4f8ef7"],
    labels={"Sales": "Sales ($)", "Customer Name": ""}
)
fig_cust.update_layout(height=400, yaxis=dict(autorange="reversed"))
st.plotly_chart(fig_cust, use_container_width=True)

# ── FOOTER ───────────────────────────────────────────────────
st.markdown("---")
st.caption("Built with Streamlit & Plotly | Superstore Dataset")