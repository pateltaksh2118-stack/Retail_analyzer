# Retail Sales Data Analyzer

Python tool that loads retail sales data (CSV), cleans it, computes metrics,
filters by category/date and visualises trends.

## Concepts used
| Topic | Where |
|---|---|
| Control structures & arrays | `validate_file`, `prompt_for_file`, `report_missing_values` (loops, if-else) |
| OOP | `RetailAnalyzer` class: `load_data`, `calculate_metrics`, `filter_data`, `display_summary`, `visualize` |
| NumPy | totals, mean/median, monthly growth % (`np.diff`), sales share % |
| Pandas | missing-value handling, groupby aggregation, computed columns (`Month`, `Sales Share %`) |
| Matplotlib & Seaborn | bar chart, line graph, correlation heatmap |

## Setup
```bash
pip install -r requirements.txt
python generate_dataset.py      # optional: regenerates retail_sales.csv (500 synthetic rows)
python retail_analyzer.py       # or: python retail_analyzer.py retail_sales.csv
```

## Workflow
1. Enter CSV path (press Enter for `retail_sales.csv`) - format/columns are validated (3 attempts).
2. Data is loaded and cleaned (missing prices -> product median, missing category -> "Unknown",
   invalid rows dropped, `Total Sales` recomputed).
3. Menu: summary report, filter (category / date range), reset filter, generate charts, exit.

Charts are saved in `output/`: `bar_sales_by_category.png`, `line_sales_trend.png`,
`heatmap_correlation.png`.

## Dataset columns
`Date (YYYY-MM-DD), Product, Category, Price, Quantity Sold, Total Sales`
(the sample file intentionally contains a few missing values to demo cleaning).

## Edge cases handled
Missing file, wrong extension, empty file, missing columns, NaN values, non-positive price/quantity,
empty filter result, invalid dates/menu input.
