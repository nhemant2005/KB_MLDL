# Working with JSON / SQL

## What It Does
SQL and JSON ingestion tools extract data from relational databases or document‑style files, as commonly needed in real‑world ML projects (HOML ch.2).  
The textbook only highlights this need; it does not provide JSON / SQL syntax or implementation.

## When To Use It
- **Data lives in a relational database** – you must run SQL queries to collect training instances (HOML ch.2).
- **Data arrives as JSON documents** – you need to parse and flatten nested structures, e.g., from web APIs or NoSQL stores (HOML ch.2).
- **Multiple tables/documents exist** – you must handle joins, credentials, and schemas before building the dataset (HOML ch.2).

## Core Syntax / API
> [NEEDS REVIEW: insufficient source material]

## Key Parameters
> [NEEDS REVIEW: insufficient source material]

## Common Mistakes
> [NEEDS REVIEW: insufficient source material]

## Textbook Coverage
HOML ch.2 briefly notes that real‑world data often sits in relational databases or document stores, but the chapter’s data‑ingestion example only downloads a CSV file and loads it with **pandas** (HOML ch.2).

## Related Topics
None (no prerequisites).