# Feature Scaling - Normalization

## Core Idea
Feature scaling — specifically min-max scaling (commonly called normalization) — transforms numerical features so their values fall within a fixed range, typically 0 to 1. This is achieved by subtracting the minimum value of a feature and dividing by the range (max minus min).

## Why It Matters
Machine Learning algorithms generally do not perform well when input numerical attributes have very different scales (HOML ch.2). Without scaling, features with large numerical ranges can dominate those with smaller ranges, distorting model learning. Methods like ridge regression and PCR are explicitly sensitive to the scale of predictors, making standardization a prerequisite (ISL ch.6).

## Explanation
The core problem is that raw features often occupy incompatible ranges: for example, in the California housing dataset, total rooms ranges from roughly 6 to 39,320 while median income ranges from 0 to 15 (HOML ch.2). Min-max scaling addresses this by applying the transformation:

$$x_{\text{scaled}} = \frac{x - x_{\min}}{x_{\max} - x_{\min}}$$

so that all values end up in $[0, 1]$ (HOML ch.2). Scikit-Learn provides `MinMaxScaler` for this purpose, which also exposes a `feature_range` hyperparameter if a range other than 0–1 is needed (HOML ch.2). For ridge regression specifically, the textbook recommends standardizing predictors because the ridge penalty is not scale equivariant — multiplying a predictor by a constant changes the coefficient estimate in a non-trivial way (ISL ch.6). When performing PCR, standardizing each predictor prior to generating principal components ensures that high-variance variables do not unduly dominate the components (ISL ch.6).

## Key Terms
- **Min-max scaling (normalization):** Rescaling values by subtracting the minimum and dividing by the range so they lie in $[0, 1]$ (HOML ch.2)
- **Feature range:** A `MinMaxScaler` hyperparameter controlling the target output interval (HOML ch.2)
- **Scale equivariance:** The property of least squares whereby multiplying a predictor by a constant simply rescales its coefficient by the inverse factor — a property ridge regression does *not* share (ISL ch.6)

## Common Misunderstanding
Beginners often apply scalers to the entire dataset (including test data) before splitting, which causes data leakage; scalers must be fit on the training set only and then used to transform both training and test sets (HOML ch.2).

## Interview Relevance
This is a foundational preprocessing question that occasionally surfaces as a warm-up or data pipeline question; interviewers typically ask *when* to use normalization versus standardization rather than focusing deeply on the math alone.

## Related Topics

> [NEEDS REVIEW: insufficient source material]

No prerequisite backlinks are defined for this note.