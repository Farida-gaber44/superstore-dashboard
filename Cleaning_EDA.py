# ============================================================
# Superstore Sales — Data Cleaning & EDA
# ============================================================
# Run this file with: python 01_cleaning_eda.py
# Make sure "Sample - Superstore.csv" is in the same folder
# ============================================================

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings("ignore")

# ── 1. LOAD ──────────────────────────────────────────────────────────────────
# Why: Read the CSV while keeping Postal Code as string (it has leading zeros)
df = pd.read_csv("Sample - Superstore.csv",
                 dtype={"Postal Code": str},
                 encoding="latin-1")   # latin-1 handles special characters in product names

print("=" * 55)
print("STEP 1 — RAW DATA OVERVIEW")
print("=" * 55)
print(f"Shape        : {df.shape[0]:,} rows × {df.shape[1]} columns")
print(f"Columns      : {list(df.columns)}")
print(f"\nData Types:\n{df.dtypes}")
print(f"\nMissing Values:\n{df.isnull().sum()}")
print(f"\nDuplicates   : {df.duplicated().sum()}")

# ── 2. CLEAN ─────────────────────────────────────────────────────────────────
print("\n" + "=" * 55)
print("STEP 2 — CLEANING")
print("=" * 55)

# 2a. Drop useless columns
# Why: Row ID is just a sequence number — adds no analytical value
df.drop(columns=["Row ID"], inplace=True)

# 2b. Convert dates
# Why: String dates can't be used for time-series analysis or sorting
df["Order Date"] = pd.to_datetime(df["Order Date"], format="%m/%d/%Y")
df["Ship Date"]  = pd.to_datetime(df["Ship Date"],  format="%m/%d/%Y")

# 2c. Extract time features
# Why: We need Month/Year for trend analysis
df["Order Year"]  = df["Order Date"].dt.year
df["Order Month"] = df["Order Date"].dt.to_period("M").astype(str)

# 2d. Drop duplicates (if any)
before = len(df)
df.drop_duplicates(inplace=True)
print(f"Duplicates removed : {before - len(df)}")

# 2e. Flag negative profit rows (don't remove — they're real business insight)
# Why: Negative profit = over-discounted orders — important to show clients
df["Profit Flag"] = df["Profit"].apply(lambda x: "Loss" if x < 0 else "Profit")
loss_pct = (df["Profit Flag"] == "Loss").mean() * 100
print(f"Loss-making orders : {loss_pct:.1f}% of all orders")
print("✓ Cleaning complete")

# ── 3. EDA — KEY BUSINESS QUESTIONS ──────────────────────────────────────────
print("\n" + "=" * 55)
print("STEP 3 — EDA: KEY INSIGHTS")
print("=" * 55)

# Q1: Overall KPIs
total_sales   = df["Sales"].sum()
total_profit  = df["Profit"].sum()
total_orders  = df["Order ID"].nunique()
profit_margin = (total_profit / total_sales) * 100

print(f"\n📊 KPIs")
print(f"  Total Sales    : ${total_sales:,.0f}")
print(f"  Total Profit   : ${total_profit:,.0f}")
print(f"  Profit Margin  : {profit_margin:.1f}%")
print(f"  Unique Orders  : {total_orders:,}")

# Q2: Sales & Profit by Region
print(f"\n🗺️  By Region")
region = df.groupby("Region")[["Sales","Profit"]].sum().sort_values("Sales", ascending=False)
print(region.to_string())

# Q3: Sales by Category
print(f"\n📦 By Category")
cat = df.groupby("Category")[["Sales","Profit"]].sum().sort_values("Sales", ascending=False)
print(cat.to_string())

# Q4: Most profitable Sub-Categories
print(f"\n🏆 Top 5 Sub-Categories by Profit")
subcat = df.groupby("Sub-Category")["Profit"].sum().sort_values(ascending=False).head(5)
print(subcat.to_string())

# Q5: Worst Sub-Categories (loss makers)
print(f"\n⚠️  Bottom 3 Sub-Categories by Profit")
worst = df.groupby("Sub-Category")["Profit"].sum().sort_values().head(3)
print(worst.to_string())

# Q6: Monthly Sales Trend
monthly = df.groupby("Order Month")["Sales"].sum().reset_index()
monthly = monthly.sort_values("Order Month")

# Q7: Top 10 Customers by Sales
print(f"\n👤 Top 5 Customers by Sales")
top_cust = df.groupby("Customer Name")["Sales"].sum().sort_values(ascending=False).head(5)
print(top_cust.to_string())

# ── 4. SAVE CLEANED FILE ──────────────────────────────────────────────────────
df.to_csv("superstore_clean.csv", index=False)
print("\n✓ Cleaned file saved as superstore_clean.csv")
print("  → Use this file for the Streamlit dashboard")

print("\n" + "=" * 55)
print("EDA complete — ready for Step 3: Dashboard")
print("=" * 55)
