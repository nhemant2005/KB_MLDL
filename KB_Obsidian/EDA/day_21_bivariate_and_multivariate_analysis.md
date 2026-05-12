# Bivariate and Multivariate Analysis

## Core Idea
Bivariate analysis examines the relationship between two variables at a time, while multivariate analysis explores interactions among three or more variables. In exploratory data analysis (EDA), these techniques reveal patterns, correlations, and potential data issues before modeling (HOML ch.2).

## Why It Matters
An ML practitioner must understand how features relate to the target and to each other to guide feature selection and engineering. Bivariate correlation can flag redundant predictors, while multivariate views — like scatter matrices and color-coded plots — may expose nonlinear interactions or clusters a simple pairwise check would miss (HOML ch.2).

## Explanation
In the California housing project, bivariate correlation was computed using the standard correlation coefficient (Pearson’s *r*) on every attribute pair via `corr()`, showing a strong linear link between median income and median house value (HOML ch.2). To move beyond pairwise analysis, the team used pandas’ `scatter_matrix()` function: it plots each numerical attribute against every other, creating a grid that helps spot nonlinear patterns, outliers, and the distribution shape of each variable through histograms on the diagonal (HOML ch.2). A multivariate visualization was built by plotting longitude vs. latitude with point color representing house price and point size representing population, encoding four dimensions simultaneously (HOML ch.2). After engineering new attributes (e.g., rooms per household), the correlation matrix was recomputed, uncovering stronger multivariate relationships that simple bivariate checks initially missed (HOML ch.2).

## Key Terms
- **Pearson’s r**: A measure of linear correlation between two variables, ranging from –1 to 1 (HOML ch.2).
- **Scatter matrix**: A grid of pairwise scatter plots for all numerical attributes, often with histograms on the diagonal (HOML ch.2).
- **Correlation matrix**: A table of pairwise correlation coefficients used to quickly screen for linearly related features (HOML ch.2).
- **Multivariate visualization**: Adding visual channels (color, size) to a basic scatter plot to represent more than two dimensions at once (HOML ch.2).

## Common Misunderstanding
A near-zero correlation coefficient is often misinterpreted as evidence of no relationship; it only captures linear association, so strong nonlinear connections can be completely invisible in a correlation matrix (HOML ch.2).

## Interview Relevance
With an interview importance of 5/10, expect to be asked to interpret a correlation matrix or a scatter matrix and to suggest what the patterns imply for feature engineering or model choice.

## Related Topics
None.