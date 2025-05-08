# parser.py

import os
import openai
import json
import pandas as pd

openai.api_key = os.getenv("OPENAI_API_KEY")

# Build prompt using few-shot examples
def build_prompt(message):
    examples = [
        {
            "input": "db 12a: 100",
            "output": [{"sku": "DB 12A", "qty": 100}]
        },
        {
            "input": "need 2 box wb 88a and 50 pcs doctor 12a",
            "output": [
                {"sku": "WB 88A", "qty": 2, "unit": "box"},
                {"sku": "DB 12A", "qty": 50}
            ]
        },
        {
            "input": "wiper 1215 20pcs",
            "output": [{"sku": "WB CP 1215", "qty": 20}]
        }
    ]
    prompt = "You are a quoting assistant. Extract SKU names and quantities from customer messages.\n\n"
    for ex in examples:
        prompt += f"Input: \"{ex['input']}\"\nOutput: {json.dumps(ex['output'])}\n\n"
    prompt += f"Input: \"{message}\"\nOutput:"
    return prompt

# Alias replacement helper
def apply_aliases(text, alias_df):
    for _, row in alias_df.iterrows():
        alias, sku = row["Alias"].lower(), row["SKU"]
        if alias in text.lower():
            text = text.lower().replace(alias, sku)
    return text

# Main parser function
def parse_message(message, alias_df, price_df):
    cleaned_input = apply_aliases(message, alias_df)
    prompt = build_prompt(cleaned_input)

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "system", "content": prompt}],
        temperature=0
    )

    parsed = json.loads(response.choices[0].message.content)
    for item in parsed:
        sku = item["sku"]
        qty = int(item["qty"])
        row = price_df[price_df["NAME IN TALLY"] == sku]
        if not row.empty:
            item["slabs"] = {
                "20pcs": row.iloc[0]["Category A Pricing"],
                "100pc": row.iloc[0]["Unnamed: 16"],
                "1box": row.iloc[0]["Unnamed: 17"],
                "4box": row.iloc[0]["Unnamed: 18"]
            }
            box_qty = row.iloc[0]["Qty/ Box"]
            item["box_qty"] = int(box_qty) if pd.notna(box_qty) else None
    return parsed
