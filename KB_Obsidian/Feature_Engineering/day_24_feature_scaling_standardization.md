# Feature Scaling - Standardization

## Core Idea
Standardization transforms a numerical feature so that it has a mean of zero and a standard deviation of one. This is done by subtracting the feature’s mean and dividing by its standard deviation (HOML ch.2). The resulting distribution has unit variance and is not confined to a specific range.

## Why It Matters
Machine learning algorithms often perform poorly when input features have very different scales (HOML ch.2). Standardization ensures that each feature contributes fairly to distance‑based and gradient‑based methods. It is also critical for regularized linear models such as ridge regression and the lasso; the ISL textbook explicitly standardizes predictors so that the penalty treats all coefficients equally (ISL ch.6).

## Explanation
For a feature $x$, standardization computes $x' = \frac{x - \bar{x}}{s}$, where $\bar{x}$ is the sample mean and $s$ is the sample standard deviation (HOML ch.2, ISL ch.6). Unlike min‑max scaling (normalization), standardization does not restrict values to a fixed interval like $[0,1]$; extreme values remain possible, but the influence of outliers is much less severe because the scaling uses the mean and standard deviation rather than the minimum and maximum (HOML ch.2). Scikit‑Learn provides the `StandardScaler` transformer for this task (HOML ch.2). Crucially, the scaler must be fitted only on the training data, then used to transform the training set, test set, and any new data—fitting on the full dataset before splitting would cause data leakage (HOML ch.2).

## Key Terms
- **Standardization**: A scaling procedure that gives a feature zero mean and unit variance by subtracting the mean and dividing by the standard deviation (HOML ch.2).
- **StandardScaler**: A Scikit‑Learn transformer that implements standardization (HOML ch.2).

## Common Misunderstanding
Beginners often fit the scaler on the entire dataset before splitting into train and test sets, leaking information. Another misconception is that standardization bounds values to a specific range; it only centers and scales, so outliers can still produce large absolute values (HOML ch.2).

## Interview Relevance
With an importance of 5/10, interview questions may ask when to use standardization versus min‑max scaling, how outliers affect each, and the correct order of fitting/transforming to avoid data leakage. It is often discussed in the context of algorithms sensitive to feature scales, such as k‑NN, SVM, and regularized regression.

## Related Topics
- None (no prerequisites listed)