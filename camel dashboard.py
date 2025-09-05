import streamlit as st
import pandas as pd
import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

# File where camel meat sales records are stored
FILE = "camel_records.csv"

# Define standard columns
COLUMNS = [
    "Date", "Item", "Quantity", "Buying Price",
    "Selling Price", "Revenue", "COGS", "Profit",
    "Payment Method", "Debt", "Transport", "Workers", "Slaughter", "Other Expenses"
]

# Load or create dataframe
if os.path.exists(FILE):
    df = pd.read_csv(FILE)
    for col in COLUMNS:
        if col not in df.columns:
            df[col] = 0
else:
    df = pd.DataFrame(columns=COLUMNS)

# Recalculate if not empty
if not df.empty:
    df["Revenue"] = df["Quantity"] * df["Selling Price"]
    df["COGS"] = df["Quantity"] * df["Buying Price"]
    df["Total Expenses"] = df[["Transport", "Workers", "Slaughter", "Other Expenses"]].sum(axis=1)
    df["Profit"] = df["Revenue"] - df["COGS"] - df["Total Expenses"] - df["Debt"]

st.title("🐪 Camel Meat Business Dashboard")

# --- Data Entry Form ---
with st.form("sales_form"):
    date = st.date_input("Date", datetime.today())
    item = st.selectbox("Select Item", ["Camel Meat", "Camel Liver", "Camel Sarara"])
    quantity = st.number_input("Quantity (kg)", min_value=1, step=1)
    buying_price = st.number_input("Buying Price per kg", min_value=0.0, step=50.0)
    selling_price = st.number_input("Selling Price per kg", min_value=0.0, step=50.0)

    payment_method = st.selectbox("Payment Method", ["Cash", "Mpesa", "Debt"])
    debt = 0
    if payment_method == "Debt":
        debt = st.number_input("Enter Debt Amount", min_value=0.0, step=50.0)

    st.markdown("### 🧾 Expenses Breakdown")
    transport = st.number_input("Transport Cost", min_value=0.0, step=50.0)
    workers = st.number_input("Workers Cost", min_value=0.0, step=50.0)
    slaughter = st.number_input("Slaughter Fee", min_value=0.0, step=50.0)
    other = st.number_input("Other Expenses", min_value=0.0, step=50.0)

    submitted = st.form_submit_button("Add Record")

    if submitted:
        revenue = quantity * selling_price
        cogs = quantity * buying_price
        total_expenses = transport + workers + slaughter + other
        profit = revenue - cogs - total_expenses - debt

        new_record = pd.DataFrame([{
            "Date": date,
            "Item": item,
            "Quantity": quantity,
            "Buying Price": buying_price,
            "Selling Price": selling_price,
            "Revenue": revenue,
            "COGS": cogs,
            "Profit": profit,
            "Payment Method": payment_method,
            "Debt": debt,
            "Transport": transport,
            "Workers": workers,
            "Slaughter": slaughter,
            "Other Expenses": other
        }])

        df = pd.concat([df, new_record], ignore_index=True)
        df.to_csv(FILE, index=False)
        st.success("✅ Record added successfully!")

# --- Display Table ---
st.subheader("📋 Daily Records")
st.dataframe(df)

# --- Summary ---
st.subheader("📊 Daily Summary")
if not df.empty:
    total_revenue = df["Revenue"].sum()
    total_cogs = df["COGS"].sum()
    total_expenses = df[["Transport", "Workers", "Slaughter", "Other Expenses"]].sum().sum()
    total_profit = df["Profit"].sum()
    total_debt = df["Debt"].sum()

    st.metric("Total Revenue", f"{total_revenue:,.0f} KES")
    st.metric("Total COGS", f"{total_cogs:,.0f} KES")
    st.metric("Total Expenses", f"{total_expenses:,.0f} KES")
    st.metric("Total Profit", f"{total_profit:,.0f} KES")
    st.metric("Total Debt", f"{total_debt:,.0f} KES")

# --- Export PDF Report ---
def export_pdf():
    pdf_file = f"Camel_Report_{datetime.today().strftime('%Y%m%d')}.pdf"
    c = canvas.Canvas(pdf_file, pagesize=A4)
    width, height = A4

    c.setFont("Helvetica-Bold", 14)
    c.drawString(180, 800, "Camel Meat Business Daily Report")

    c.setFont("Helvetica", 12)
    y = 770
    for index, row in df.iterrows():
        record = f"{row['Date']} | {row['Item']} | Qty: {row['Quantity']} | Rev: {row['Revenue']} | Profit: {row['Profit']} | Pay: {row['Payment Method']} | Debt: {row['Debt']}"
        c.drawString(30, y, record)
        y -= 20
        if y < 60:  
            c.showPage()
            c.setFont("Helvetica", 12)
            y = 800

    # Summary at the end
    c.setFont("Helvetica-Bold", 12)
    y -= 40
    c.drawString(30, y, f"Total Revenue: {total_revenue:,.0f} KES")
    c.drawString(30, y - 20, f"Total COGS: {total_cogs:,.0f} KES")
    c.drawString(30, y - 40, f"Total Expenses: {total_expenses:,.0f} KES")
    c.drawString(30, y - 60, f"Total Profit: {total_profit:,.0f} KES")
    c.drawString(30, y - 80, f"Total Debt: {total_debt:,.0f} KES")

    c.save()
    return pdf_file

if st.button("📑 Export Daily Report as PDF"):
    pdf_path = export_pdf()
    st.success(f"Report exported as {pdf_path}")
