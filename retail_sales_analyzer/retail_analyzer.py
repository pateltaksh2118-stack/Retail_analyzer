"""
Retail Sales Data Analyzer
==========================
Processes, analyses and visualises retail sales data.

Concepts demonstrated
---------------------
* Control structures & arrays : input/file validation, loops, missing-value checks
* OOP                         : RetailAnalyzer class
* NumPy                       : growth rates, percentages, averages
* Pandas                      : cleaning, aggregation, computed columns
* Matplotlib & Seaborn        : bar chart, line graph, heatmap

Usage:  python retail_analyzer.py [path/to/retail_sales.csv]
"""
import os
import sys

import matplotlib


if not os.environ.get("DISPLAY") and sys.platform.startswith("linux"):
    matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

REQUIRED_COLUMNS = ["Date", "Product", "Category", "Price", "Quantity Sold", "Total Sales"]
OUTPUT_DIR = "output"



def validate_file(file_path):
    """Return (is_valid, message) after checking the CSV path and its header."""
    if not file_path.lower().endswith(".csv"):
        return False, "File must have a .csv extension."
    if not os.path.isfile(file_path):
        return False, f"File not found: {file_path}"
    if os.path.getsize(file_path) == 0:
        return False, "File is empty."

    with open(file_path, "r", encoding="utf-8") as fh:
        header = [h.strip() for h in fh.readline().strip().split(",")]
    missing = [col for col in REQUIRED_COLUMNS if col not in header]  
    if missing:
        return False, f"Missing required columns: {', '.join(missing)}"
    return True, "File format is valid."


def prompt_for_file(default="retail_sales.csv"):
    """Keep asking the user for a CSV path until a valid one is given (max 3 tries)."""
    for attempt in range(1, 4):
        path = input(f"Enter CSV file path [{default}]: ").strip() or default
        ok, msg = validate_file(path)
        print(("[OK] " if ok else "[ERROR] ") + msg)
        if ok:
            return path
        print(f"Attempt {attempt}/3 failed.\n")
    return None


def report_missing_values(df):
    """Loop over every column and report missing / invalid entries."""
    print("\n--- Data Quality Check ---")
    found = False
    for col in df.columns:
        n_missing = int(df[col].isna().sum())
        if n_missing > 0:
            found = True
            print(f"  {col:<14}: {n_missing} missing value(s)")
    if not found:
        print("  No missing values found.")

    # Invalid-entry check: non-positive price / quantity
    for col in ("Price", "Quantity Sold"):
        n_bad = int((df[col] <= 0).sum())
        if n_bad:
            print(f"  {col:<14}: {n_bad} non-positive value(s)")


class RetailAnalyzer:
    """Encapsulates loading, cleaning, analysing and plotting retail sales data."""

    def __init__(self):
        self.data = None      
        self.raw_data = None   
        self.metrics = {}

    def load_data(self, file_path):
        """Read the CSV with Pandas, report issues and clean the dataset."""
        df = pd.read_csv(file_path)
        df.columns = [c.strip() for c in df.columns]
        report_missing_values(df)
        self.raw_data = self._clean(df)
        self.data = self.raw_data.copy()
        print(f"\nLoaded {len(self.data)} clean records.")
        return self.data

    @staticmethod
    def _clean(df):
        """Handle missing values and add computed columns."""
        df = df.copy()
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        df = df.dropna(subset=["Date", "Product"])             

        df["Category"] = df["Category"].fillna("Unknown")
        df["Price"] = df["Price"].fillna(df.groupby("Product")["Price"].transform("median"))
        df["Price"] = df["Price"].fillna(df["Price"].median())
        df["Quantity Sold"] = df["Quantity Sold"].fillna(df["Quantity Sold"].median()).round()

        df = df[(df["Price"] > 0) & (df["Quantity Sold"] > 0)] 
        df["Total Sales"] = (df["Price"] * df["Quantity Sold"]).round(2)

        df["Month"] = df["Date"].dt.to_period("M").astype(str)
        df["Sales Share %"] = np.round(100 * df["Total Sales"] / df["Total Sales"].sum(), 4)
        return df.reset_index(drop=True)

    def calculate_metrics(self):
        """Compute total/average sales, top product, monthly growth (NumPy)."""
        df = self.data
        if df is None or df.empty:
            print("No data available to analyse.")
            return {}

        sales = df["Total Sales"].to_numpy()                       
        monthly = df.groupby("Month")["Total Sales"].sum().to_numpy()
        growth = np.diff(monthly) / monthly[:-1] * 100 if len(monthly) > 1 else np.array([])

        by_product_qty = df.groupby("Product")["Quantity Sold"].sum()
        by_category = df.groupby("Category")["Total Sales"].sum()

        self.metrics = {
            "total_sales": float(np.sum(sales)),
            "average_sales": float(np.mean(sales)),
            "median_sales": float(np.median(sales)),
            "max_sale": float(np.max(sales)),
            "num_transactions": int(len(sales)),
            "most_popular_product": by_product_qty.idxmax(),
            "most_popular_qty": int(by_product_qty.max()),
            "top_category": by_category.idxmax(),
            "top_category_share": float(by_category.max() / by_category.sum() * 100),
            "avg_monthly_growth": float(np.mean(growth)) if growth.size else 0.0,
            "monthly_growth": growth,
        }
        return self.metrics

    def filter_data(self, condition):
        """
        Filter the working data. `condition` is a dict, e.g.
            {"category": "Electronics", "start": "2024-03-01", "end": "2024-06-30"}
        Any key may be omitted. Returns the filtered DataFrame.
        """
        df = self.raw_data
        if "category" in condition:
            df = df[df["Category"].str.lower() == condition["category"].lower()]
        if "start" in condition:
            df = df[df["Date"] >= pd.to_datetime(condition["start"])]
        if "end" in condition:
            df = df[df["Date"] <= pd.to_datetime(condition["end"])]
        self.data = df.reset_index(drop=True)
        print(f"Filter applied -> {len(self.data)} record(s) match.")
        return self.data

    def reset_filter(self):
        self.data = self.raw_data.copy()

    def display_summary(self):
        """Print a formatted summary report."""
        m = self.calculate_metrics()
        if not m:
            return
        line = "=" * 52
        print(f"\n{line}\n{'RETAIL SALES SUMMARY':^52}\n{line}")
        print(f"Period              : {self.data['Date'].min():%Y-%m-%d} to {self.data['Date'].max():%Y-%m-%d}")
        print(f"Transactions        : {m['num_transactions']}")
        print(f"Total Sales         : {m['total_sales']:,.2f}")
        print(f"Average Sale        : {m['average_sales']:,.2f}")
        print(f"Median Sale         : {m['median_sales']:,.2f}")
        print(f"Largest Sale        : {m['max_sale']:,.2f}")
        print(f"Most Popular Product: {m['most_popular_product']} ({m['most_popular_qty']} units)")
        print(f"Top Category        : {m['top_category']} ({m['top_category_share']:.1f}% of sales)")
        print(f"Avg Monthly Growth  : {m['avg_monthly_growth']:+.2f}%")
        print("\nTop 5 Products by Revenue:")
        top = self.data.groupby("Product")["Total Sales"].sum().nlargest(5)
        for rank, (prod, val) in enumerate(top.items(), 1):
            print(f"  {rank}. {prod:<15} {val:>14,.2f}")
        print(line)

    def visualize(self, show=True):
        """Create bar chart, line graph and heatmap; save PNGs in ./output."""
        if self.data is None or self.data.empty:
            print("No data to visualise.")
            return
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        sns.set_theme(style="whitegrid", context="notebook")
        df = self.data

        fig, ax = plt.subplots(figsize=(9, 5))
        cat = df.groupby("Category")["Total Sales"].sum().sort_values(ascending=False).reset_index()
        sns.barplot(data=cat, x="Category", y="Total Sales", hue="Category", palette="viridis",
                    legend=False, ax=ax)
        for c in ax.containers:
            ax.bar_label(c, fmt="%.0f", padding=3, fontsize=8)
        ax.set(title="Total Sales by Product Category", xlabel="Category", ylabel="Total Sales")
        fig.tight_layout()
        fig.savefig(os.path.join(OUTPUT_DIR, "bar_sales_by_category.png"), dpi=150)

        fig, ax = plt.subplots(figsize=(10, 5))
        monthly = df.groupby("Month")["Total Sales"].sum().reset_index()
        sns.lineplot(data=monthly, x="Month", y="Total Sales", marker="o", linewidth=2.2,
                     color="#2a6f97", label="Monthly Sales", ax=ax)
        ax.set(title="Sales Trend Over Time", xlabel="Month", ylabel="Total Sales")
        ax.tick_params(axis="x", rotation=45)
        ax.legend()
        fig.tight_layout()
        fig.savefig(os.path.join(OUTPUT_DIR, "line_sales_trend.png"), dpi=150)

        fig, ax = plt.subplots(figsize=(6.5, 5))
        corr = df[["Price", "Quantity Sold", "Total Sales"]].corr()
        sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm", vmin=-1, vmax=1, square=True, ax=ax)
        ax.set_title("Correlation: Price vs Quantity Sold vs Total Sales")
        fig.tight_layout()
        fig.savefig(os.path.join(OUTPUT_DIR, "heatmap_correlation.png"), dpi=150)

        print(f"Charts saved in '{OUTPUT_DIR}/' folder.")
        if show:
            plt.show()
        plt.close("all")


def filter_menu(analyzer):
    """Ask the user for filter criteria and apply them."""
    cats = sorted(analyzer.raw_data["Category"].unique())
    print("Available categories:", ", ".join(cats))
    cond = {}
    category = input("Category (blank = all): ").strip()
    if category:
        if category.lower() not in [c.lower() for c in cats]:
            print("Unknown category - ignored.")
        else:
            cond["category"] = category
    for key, label in (("start", "Start date"), ("end", "End date")):
        value = input(f"{label} YYYY-MM-DD (blank = none): ").strip()
        if value:
            try:
                pd.to_datetime(value)
                cond[key] = value
            except ValueError:
                print(f"Invalid {label.lower()} - ignored.")
    analyzer.filter_data(cond)


def main():
    print("=== Retail Sales Data Analyzer ===")
    path = sys.argv[1] if len(sys.argv) > 1 else prompt_for_file()
    if path is None:
        print("Too many invalid attempts. Exiting.")
        return
    ok, msg = validate_file(path)
    if not ok:
        print("[ERROR]", msg)
        return

    analyzer = RetailAnalyzer()
    analyzer.load_data(path)

    menu = ("\n1. Show summary\n2. Filter data\n3. Reset filter\n"
            "4. Generate visualizations\n5. Exit")
    while True:
        print(menu)
        choice = input("Choose an option (1-5): ").strip()
        if choice == "1":
            analyzer.display_summary()
        elif choice == "2":
            filter_menu(analyzer)
        elif choice == "3":
            analyzer.reset_filter()
            print("Filter cleared.")
        elif choice == "4":
            analyzer.visualize()
        elif choice == "5":
            print("Goodbye!")
            break
        else:
            print("Invalid choice, please enter 1-5.")


if __name__ == "__main__":
    main()
