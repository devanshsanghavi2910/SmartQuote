# app.py

import streamlit as st
from parser import parse_message
from pricing import compute_price
import pandas as pd

# --- Load Data ---
@st.cache_data
def load_data():
    df = pd.read_excel("price_sheet.xlsx", sheet_name="Doctor Wiper")
    alias_df = pd.read_csv("alias.csv")
    return df, alias_df

price_df, alias_df = load_data()

# --- UI ---
st.set_page_config(page_title="Smart Quote", layout="centered")
st.title("🧾 Premier Smart Quoting Engine")
st.markdown("Handles *Doctor/Wiper Blades* – Tier A Pricing")

input_text = st.text_area("Paste customer enquiry", height=150)
submit = st.button("Generate Quote")

if submit and input_text.strip():
    with st.spinner("Thinking..."):
        try:
            results = parse_message(input_text, alias_df, price_df)
            if not results:
                st.warning("❗ Couldn't match any items.")
            else:
                total_quote = 0
                for item in results:
                    sku = item["sku"]
                    qty = item["qty"]
                    row = price_df[price_df["NAME IN TALLY"] == sku]
                    if row.empty:
                        st.write(f"• {sku}: ❌ Not in price sheet")
                        continue

                    slabs = {
                        "20pcs": row.iloc[0]["Category A Pricing"],
                        "100pc": row.iloc[0]["Unnamed: 16"],
                        "1box": row.iloc[0]["Unnamed: 17"],
                        "4box": row.iloc[0]["Unnamed: 18"]
                    }
                    box_qty = row.iloc[0]["Qty/ Box"]
                    stock = row.iloc[0]["Stock"]
                    if stock == 0:
                        st.write(f"• {sku}: ❌ Not in stock")
                        continue

                    unit_price, total = compute_price(qty, slabs, box_qty)
                    if unit_price is None:
                        st.write(f"• {sku} – {qty} pcs: ❌ Minimum 20 pcs required")
                        continue

                    st.write(f"• {sku} – {qty} pcs @ ₹{unit_price:.2f} = ₹{total:,.2f}")
                    total_quote += total

                st.markdown(f"### 💰 Total: ₹{total_quote:,.2f}")
        except Exception as e:
            st.error(f"Error: {e}")
