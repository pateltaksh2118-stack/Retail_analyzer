"""Generate a sample retail_sales.csv (synthetic data) for the Retail Sales Data Analyzer."""
import numpy as np
import pandas as pd

rng = np.random.default_rng(42)

CATALOGUE = [
    ("Laptop", "Electronics", 55000), ("Smartphone", "Electronics", 25000),
    ("Headphones", "Electronics", 2500), ("Smart Watch", "Electronics", 8000),
    ("T-Shirt", "Clothing", 600), ("Jeans", "Clothing", 1800),
    ("Jacket", "Clothing", 3500), ("Sneakers", "Clothing", 2800),
    ("Rice (5kg)", "Grocery", 450), ("Olive Oil", "Grocery", 700),
    ("Coffee Pack", "Grocery", 350), ("Snacks Box", "Grocery", 250),
    ("Sofa Cushion", "Home", 500), ("Desk Lamp", "Home", 1200),
    ("Bed Sheet Set", "Home", 1500), ("Cookware Set", "Home", 4000),
    ("Notebook Pack", "Stationery", 200), ("Pen Set", "Stationery", 150),
    ("Backpack", "Stationery", 1400),
]

dates = pd.date_range("2024-01-01", "2024-12-31", freq="D")
rows = []
for _ in range(500):
    product, category, base = CATALOGUE[rng.integers(len(CATALOGUE))]
    price = round(base * rng.uniform(0.9, 1.1), 2)
    qty = int(max(1, rng.poisson(max(1.0, 12 - np.log10(price) * 2.5))))
    rows.append({
        "Date": rng.choice(dates).astype("datetime64[D]").astype(str),
        "Product": product,
        "Category": category,
        "Price": price,
        "Quantity Sold": qty,
        "Total Sales": round(price * qty, 2),
    })

df = pd.DataFrame(rows).sort_values("Date").reset_index(drop=True)
for col, n in [("Price", 4), ("Quantity Sold", 4), ("Category", 3)]:
    df.loc[rng.choice(len(df), n, replace=False), col] = np.nan

df.to_csv("retail_sales.csv", index=False)
print(f"Created retail_sales.csv with {len(df)} rows")
