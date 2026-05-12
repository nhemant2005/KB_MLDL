## Core Idea
Feature engineering is the process of transforming raw data into new representations that make it easier for machine learning algorithms to uncover patterns. It includes creating derived attributes, encoding categorical variables, scaling numeric features, and expanding the input space with polynomial or basis-function terms—all illustrated in the California housing end-to-end project (HOML ch.2) and in polynomial regression (HOML ch.4; ISL ch.7).

## Why It Matters
Without feature engineering, many algorithms fail to capture real relationships. For instance, linear models can only fit curves if we explicitly add powers and interactions (HOML ch.4; ISL ch.7). Even for tree-based models, carefully composed features like “bedrooms per room” expose critical negative correlations that raw counts miss (HOML ch.2). Effective feature engineering often determines the difference between a mediocre model and one that performs well.

## Explanation
Feature engineering ranges from simple scaling to complex basis expansions. In the housing project, the total number of rooms alone was uninformative; combining it with households to form `rooms_per_household` and `bedrooms_per_room` dramatically increased correlation with price (HOML ch.2). Categorical values such as `ocean_proximity` were one-hot encoded to avoid implying an ordinal order that doesn’t exist (HOML ch.2). Numerical attributes were scaled (standardization or min-max) so gradient descent would not struggle with elongated cost surfaces (HOML ch.2, ch.4). More broadly, polynomial regression adds powers of features, letting a linear model approximate nonlinear functions (HOML ch.4). The general framework of *basis functions* replaces each original predictor with a set of fixed transformations \(b_j(X)\); the model becomes a linear combination of these constructed features (ISL ch.7). Thus, feature engineering is about choosing or inventing the right \(b_j(X)\) to expose the underlying signal.

## Key Terms
- **Feature scaling**: Shifting and rescaling numeric attributes to a common range (e.g., standardization to zero mean/unit variance, or min‑max to [0,1]) so algorithms like gradient descent converge faster (HOML ch.2).
- **One-hot encoding**: Creating binary indicator columns for each category of a qualitative variable, removing false numerical ordering (HOML ch.2).
- **Polynomial features**: Extending the feature set with squared, cubic, and interaction terms to allow linear models to capture nonlinear patterns (HOML ch.4; ISL ch.7).
- **Basis functions**: A fixed family of functions \(b_1(X), …, b_K(X)\) that transform a predictor; fitting a linear model on these functions yields flexible, non‑linear fits (ISL ch.7).
- **Attribute combinations**: New features formed by arithmetic operations on existing columns (e.g., rooms per household, bedrooms per room) that reveal relationships invisible to the original variables (HOML ch.2).

## Common Misunderstanding
Beginners often equate feature engineering with cleaning missing values and scaling, overlooking that inventing informative combinations (like `bedrooms_per_room`) can uncover hidden patterns that dramatically improve a model’s performance (HOML ch.2).

## Interview Relevance
This topic appears moderately often (5/10) in applied ML interviews. Candidates may be asked how they would encode a categorical variable such as `ocean_proximity` or how they would help a linear model fit a nonlinear relationship. Answers citing one-hot encoding and polynomial/log‑transforms are expected (HOML ch.2; HOML ch.4; ISL ch.7).

## Related Topics
[[None]]