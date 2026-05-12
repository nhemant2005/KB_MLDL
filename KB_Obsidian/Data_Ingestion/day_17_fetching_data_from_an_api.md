# Fetching Data from an API

## What It Does
A utility function that downloads a compressed dataset file from a given URL, creates a local directory, and extracts the data for use in a project. The textbook demonstrates this using Python's `urllib` and `tarfile` to automate data retrieval instead of manual browser downloads. (HOML ch.2)

## When To Use It
- When the data changes regularly and you want the latest version fetched automatically via a scheduled job (HOML ch.2)
- When setting up the project on multiple machines—avoids manual download steps on each one (HOML ch.2)
- When building a reproducible pipeline that includes data retrieval as a coded step rather than an external manual action (HOML ch.2)
- When the data source is a single compressed file at a stable URL and doesn't require authentication tokens or complex API negotiation (HOML ch.2)

## Core Syntax / API

```python
import os
import tarfile
import urllib

# Root URL where the dataset lives
DOWNLOAD_ROOT = "https://raw.githubusercontent.com/ageron/handson-ml2/master/"
HOUSING_PATH = os.path.join("datasets", "housing")  # local save directory
HOUSING_URL = DOWNLOAD_ROOT + "datasets/housing/housing.tgz"  # full URL

def fetch_housing_data(housing_url=HOUSING_URL, housing_path=HOUSING_PATH):
    # Creates the target directory if it doesn't exist; exist_ok avoids errors
    os.makedirs(housing_path, exist_ok=True)
    # Builds the local file path for the compressed archive
    tgz_path = os.path.join(housing_path, "housing.tgz")
    # Downloads the file from housing_url and saves it to tgz_path
    urllib.request.urlretrieve(housing_url, tgz_path)
    # Opens the compressed tar archive
    housing_tgz = tarfile.open(tgz_path)
    # Extracts all contents into housing_path directory
    housing_tgz.extractall(path=housing_path)
    # Closes the archive file handle
    housing_tgz.close()
```

(HOML ch.2)

## Key Parameters

| Parameter | What it controls | Typical value |
|---|---|---|
| `housing_url` | The remote URL from which the dataset is fetched | A raw GitHub URL or any stable direct download link |
| `housing_path` | The local directory where the extracted files land | `os.path.join("datasets", "housing")` |
| `exist_ok=True` | Whether `os.makedirs` should silently succeed if the directory already exists | `True` |

(HOML ch.2)

## Common Mistakes
- Running the download function repeatedly without `exist_ok=True` causes `FileExistsError` if the directory is already present (HOML ch.2)
- Forgetting to close the `tarfile` object after extraction—leaks file handles (HOML ch.2)
- Assuming this simple `urllib`-based approach works for APIs requiring authentication headers, API keys, or pagination—it only handles basic HTTP file retrieval (HOML ch.2)

## Textbook Coverage
The textbook covers a straightforward file download-and-extract pattern using `urllib` and `tarfile` for a single `.tgz` dataset, but does not cover authenticated REST APIs, token management, rate limiting, JSON parsing, or any `requests`-library patterns—all of which dominate real-world API work. (HOML ch.2)

## Related Topics
No prerequisites listed for this note.