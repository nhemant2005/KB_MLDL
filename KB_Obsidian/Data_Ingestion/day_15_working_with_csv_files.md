## What It Does
Reads comma-separated values (CSV) files and loads them into a pandas DataFrame object for data manipulation and analysis in Python. (HOML ch.2)

## When To Use It
- Importing structured tabular data stored as CSV files into a Python environment for ML projects (HOML ch.2)
- Loading the raw housing dataset after extracting it from a compressed archive (HOML ch.2)
- Using within a reusable function to fetch and load data, especially when datasets change regularly or need to be installed on multiple machines (HOML ch.2)
- Inspecting data structure immediately after loading using `.head()` or `.info()` methods on the returned DataFrame (HOML ch.2)

## Core Syntax / API
```python
import pandas as pd

# Basic usage: provide file path
housing = pd.read_csv("housing.csv")

# Usage within a reusable loading function
def load_housing_data(housing_path="datasets/housing"):
    csv_path = os.path.join(housing_path, "housing.csv")
    return pd.read_csv(csv_path)  # returns DataFrame
```
(HOML ch.2)

## Key Parameters
| Parameter | what it controls | typical value |
|-----------|------------------|---------------|
| `filepath_or_buffer` | Path to the CSV file to read | `"housing.csv"` or a constructed path string (HOML ch.2) |
| `header` | Which row to use as column names (R equivalent shown with `header = T`) | `0` (first row) or `True` (ISL ch.2) |
| `na_values` | Additional strings to recognize as NA/NaN (R equivalent: `na.strings`) | `"?"` or a list of strings (ISL ch.2) |
| `dtype` or type handling | How to treat string columns (R equivalent: `stringsAsFactors`) | Let pandas infer or set manually for categorical columns (ISL ch.2) |

The textbook primarily demonstrates the default usage of `pd.read_csv()` without exploring extensive parameter customization for Python. (HOML ch.2, ISL ch.2)

## Common Mistakes
- Removing rows with missing values blindly without checking why data is missing first. The `total_bedrooms` attribute had 207 null values that need handling. (HOML ch.2)
- Forgetting that text attributes loaded from CSV may have dtype `object`, requiring inspection with `.value_counts()` to recognize them as categorical. (HOML ch.2)
- Assuming all columns are numerical; the `ocean_proximity` field was text and needed encoding before ML algorithms could use it. (HOML ch.2)

## Textbook Coverage
The HOML textbook uses `pd.read_csv` as a standard data ingestion tool within an end-to-end ML workflow but does not provide exhaustive API documentation; the ISL textbook covers the R equivalent with slightly more parameter detail. Coverage is utilitarian, focusing on getting data loaded rather than deep CSV parsing options.

## Related Topics
*No prerequisites specified.*