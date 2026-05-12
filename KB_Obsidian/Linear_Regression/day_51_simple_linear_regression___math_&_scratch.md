---
topic: "Simple Linear Regression - Math & Scratch"
section: "Linear Regression"
playlist_day: 51
difficulty: "high"
interview_importance: 10
status: "not_started"
tags: ["LinearRegression", "high", "algorithm"]
prerequisites: []
---

# Simple Linear Regression - Math & Scratch

## Core Idea
Simple Linear Regression fits a straight line through data by finding the parameter vector $\hat{\theta}$ that minimizes the cost function (Mean Squared Error). It solves the problem of predicting a continuous target variable from one or more input features. It exists as the foundational supervised learning model — interpretable, computationally tractable, and solvable in closed form. (HOML ch.4)

## Intuition
The model assumes a linear relationship exists between inputs and the target, so the task reduces to finding the best line. Think of it as choosing a slope and intercept that keep your predictions as close as possible to the true values, on average. The "best" parameters are those that minimize the sum of squared vertical distances between the predicted line and each data point. The noise in real data means we can never recover exact ground-truth parameters — only approximations. (HOML ch.4)

## Mathematical Formulation

**Step 1 — Define the model prediction:**

$$\hat{y} = X_b \, \theta$$

where $X_b$ is the design matrix with a column of ones prepended (to handle the bias term $\theta_0$), and $\theta$ is the parameter vector. (HOML ch.4)

**Step 2 — Define the cost function (MSE):**

$$\text{MSE}(\theta) = \frac{1}{m} \sum_{i=1}^{m} \left( \hat{y}^{(i)} - y^{(i)} \right)^2$$

We want to find $\hat{\theta}$ that minimizes this quantity. (HOML ch.4)

**Step 3 — Closed-form solution (Normal Equation):**

Taking the derivative of $\text{MSE}(\theta)$ with respect to $\theta$, setting it to zero, and solving yields the **Normal Equation**:

$$\hat{\theta} = (X^{\top} X)^{-1} X^{\top} y$$

This directly gives the parameter values that minimize the cost — no iteration required. (HOML ch.4)

**Step 4 — Make predictions:**

$$\hat{y}_{\text{new}} = X_{\text{new},b} \, \hat{\theta}$$

Prediction complexity is $O(m \times n)$ — linear in both instances and features. (HOML ch.4)

## Key Formulas

- **Model hypothesis:** $\hat{y} = X_b \, \theta$ (HOML ch.4)
- **MSE cost function:** $\text{MSE}(\theta) = \frac{1}{m} \sum_{i=1}^{m}(\hat{y}^{(i)} - y^{(i)})^2$ (HOML ch.4)
- **Normal Equation:** $\hat{\theta} = (X^{\top} X)^{-1} X^{\top} y$ (HOML ch.4)
- **Pseudoinverse solution:** $\hat{\theta} = X^{+} y$, where $X^{+} = V \Sigma^{+} U^{\top}$ (HOML ch.4)

## Assumptions

- A linear relationship exists between the features and the target. (HOML ch.4)
- The matrix $X^{\top}X$ must be invertible; if features are redundant or $m < n$, the Normal Equation fails — use the pseudoinverse instead. (HOML ch.4)
- Noise prevents exact parameter recovery from data. (HOML ch.4)

## Step-by-Step Algorithm

1. Collect training data: input matrix $X$ and target vector $y$.
2. Prepend a column of ones to $X$ to form the augmented matrix $X_b$ (handles bias term $\theta_0$).
3. Compute $X^{\top} X$ and check invertibility.
4. Apply the Normal Equation: $\hat{\theta} = (X^{\top} X)^{-1} X^{\top} y$.
5. Alternatively, use the pseudoinverse $X^{+}$ via SVD for numerical stability when $X^{\top}X$ is singular.
6. Store $\hat{\theta}$ (intercept = $\hat{\theta}_0$, slope(s) = remaining components).
7. Predict on new data: $\hat{y} = X_{\text{new},b} \, \hat{\theta}$.

(HOML ch.4)

## Hyperparameters

| Parameter | Effect on Model | How to Tune |
|---|---|---|
| None (closed-form) | Normal Equation has no hyperparameters — solution is exact | N/A |

> [NEEDS REVIEW: insufficient source material — textbook does not discuss hyperparameters for the closed-form solver]

## Failure Modes

- **Non-invertible $X^{\top}X$:** Occurs when $m < n$ or features are linearly redundant; Normal Equation breaks down. (HOML ch.4)
- **Too many features:** Normal Equation complexity is $O(n^{2.4})$ to $O(n^3)$; becomes very slow for ~100,000+ features. (HOML ch.4)
- **Noise:** Corrupts parameter estimates — the recovered $\hat{\theta}$ approximates but never exactly matches true parameters. (HOML ch.4)
- **Memory constraints:** Both Normal Equation and SVD are $O(m)$ in instances, so very large datasets may not fit in memory. (HOML ch.4)

## Interview Questions

1. Derive the Normal Equation $\hat{\theta} = (X^{\top}X)^{-1}X^{\top}y$ from first principles.
2. When does the Normal Equation fail, and what is the preferred numerical alternative?
3. What is the computational complexity of the Normal Equation with respect to features vs. instances?
4. Why do we prepend a column of ones to $X$ before applying the Normal Equation?
5. Why can't we always perfectly recover the true parameters even with the correct model form?

## Code Examp

# Generate synthetic linear data:
---
## Links

**Same Section**
- [[Simple Linear Regression - Intuition & Code]]
- [[Regression Metrics]]
- [[Multiple Linear Regression - Intuition & Code]]
- [[Multiple Linear Regression - Math from Scratch]]
- [[Multiple Linear Regression - Code from Scratch]]

**See Also**
- [[What is Machine Learning]]
- [[AI vs ML vs DL]]
- [[Types of Machine Learning]]
- [[Batch Learning]]

