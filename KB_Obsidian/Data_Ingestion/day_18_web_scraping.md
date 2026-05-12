# Web Scraping

## What It Does
Downloads data files from a web URL for automated, repeatable dataset ingestion (HOML ch.2).

## When To Use It
- When the dataset is hosted as a static file (e.g., a `.tgz` or `.csv`) at a known URL (HOML ch.2).
- To refresh the dataset automatically – a script can fetch the latest version on a schedule (HOML ch.2).
- To replicate the data‑acquisition step across multiple machines without manual intervention (HOML ch.2).
- As part of a data pipeline where new raw data arrives periodically.

## Core Syntax / API
```python
import urllib
import tarfile
import os

# Download a compressed file from a URL
urllib.request.urlretrieve(
    "https://raw.githubusercontent.com/…/housing.tgz",  # URL to fetch
    "datasets/housing/housing.tgz"                       # local destination path
)

# Create target directory if needed
os.makedirs("datasets/housing", exist_ok=True)

# Extract the downloaded archive
with tarfile.open("datasets/housing/housing.tgz") as tgz:
    tgz.extractall(path="datasets/housing")
```

*(based on `fetch_housing_data` from HOML ch.2)*

## Key Parameters
| Parameter              | What it controls                                   | Typical value                     |
|------------------------|----------------------------------------------------|------------------------------------|
| `url` (in `urlretrieve`)| The web address of the file to download           | Full URL string                    |
| `filename` (in `urlretrieve`) | Path where the downloaded file is saved      | Local path string                  |
| `path` (in `extractall`) | Directory where the archive contents are extracted | Directory path string              |
| `exist_ok` (in `makedirs`) | If `True`, no error is raised when directory already exists | `True` (recommended in HOML ch.2) |

## Common Mistakes
- Skipping `os.makedirs` with `exist_ok=True` – the script will crash if the target directory doesn’t exist (HOML ch.2).
- Assuming `urlretrieve` handles errors gracefully – broken URLs or network issues can halt the script without proper exception handling.
- Overwriting local files on every run without a check, potentially losing manually modified data.

## Textbook Coverage
Covers basic file download and extraction with `urllib` and `tarfile`; does **not** cover parsing HTML, handling APIs, or scraping dynamic pages (HOML ch.2).

## Related Topics
- Data Ingestion (using urllib)
- File handling with tarfile
- Loading CSV with pandas