# Univariate Analysis

## Core Idea
Univariate analysis examines a single variable at a time to reveal its distribution, central tendency, spread, and data quality issues such as missing values (HOML ch.2). It is the foundational step of exploratory data analysis (EDA) that flags necessary preprocessing actions like scaling or transformations.

## Why It Matters
Machine learning algorithms are sensitive to feature scales, outliers, and skew. Univariate inspection uncovers varying scales, tail‑heavy distributions, and capped values—problems that, if left untreated, degrade model performance (HOML ch.2). Findings directly guide imputation, standardization, and log/power transformations that make data more suitable for learning.

## Explanation
In the California housing project (HOML ch.2), the `info()` method first reveals data types and the count of non‑null values, exposing that `total_bedrooms` is missing 207 entries. The `describe()` method provides numerical summaries for each attribute: count, mean, standard deviation, min, percentiles, and max. The `std` row measures dispersion, and the $25\%$, $50\%$, $75\%$ rows give the first, second, and third quartiles—values below which a given fraction of observations fall (HOML ch.2). Histograms plotted with `hist()` visualize the shape of every numeric attribute. They show that `median_house_value` is capped at \$500,000, many attributes have very different scales (e.g., `total_rooms` vs. `median_income`), and several are heavily right‑skewed (tail‑heavy) (HOML ch.2). These observations directly motivate later preprocessing: imputation for missing values, feature scaling to equalize magnitudes, and log transformations to reduce skew and achieve more bell‑shaped distributions (HOML ch.2).

## Key Terms
- **Histogram**: A plot that shows the count of instances falling into each value interval for a numerical attribute (HOML ch.2).  
- **Percentile**: The value below which a given percentage of observations lie; e.g., the 25th percentile (first quartile) (HOML ch.2).  
- **Standard deviation ($\sigma$)**: A measure of how spread out the values are around the mean (HOML ch.2).  
- **Missing value**: A feature entry absent for an instance; in the housing data `total_bedrooms` had 207 missing values (HOML ch.2).  
- **Distribution shape**: Describes whether data is symmetric, tail‑heavy (skewed right), or shows artifacts like capped ceilings (HOML ch.2).

## Common Misunderstanding
Beginners often rely solely on `describe()` and overlook visual tools like histograms. Important data quirks—capped values, extreme skew, or unexpected gaps—frequently hide in the distribution shape and appear only when plotted (HOML ch.2).

## Interview Relevance
With an importance of 5/10, univariate analysis appears in interviews as a basic EDA question. A candidate who can walk through `info()`, `describe()`, and `hist()` on a new dataset demonstrates sound data‑handling fundamentals expected of any ML practitioner.

## Related Topics
None