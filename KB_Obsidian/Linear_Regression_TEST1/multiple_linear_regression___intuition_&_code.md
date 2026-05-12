# Multiple Linear Regression - Intuition & Code

## Core Idea
Multiple Linear Regression extends simple linear regression to handle **multiple predictor variables** simultaneously. Instead of drawing a line through one input dimension, the algorithm fits a hyperplane through $p$-dimensional space. It exists because real-world outcomes (sales, prices, risk) are rarely driven by a single variable — we need a framework that separates each predictor's contribution while accounting for the others.

---

## Intuition
In practice, a single predictor almost never tells the whole story. For example, sales of a product may depend on TV budget, radio budget, *and* newspaper budget simultaneously (ISL ch.3). Multiple Linear Regression asks: after adjusting for all other predictors, how much does each one independently move the response? A key motivating example from the textbook is shark attacks: ice cream sales correlates with shark attacks, but a multiple regression that also includes temperature reveals ice cream sales is no longer a significant predictor — temperature explains both (ISL ch.3). This shows that MLR helps **disentangle confounded relationships** that simple regression cannot separate.

---

## Mathematical Formulation

**Step 1 — Define the model.**  
For $p$ predictors, the model for observation $i$ is:

$$Y_i = \beta_0 + \beta_1 X_{i1} + \beta_2 X_{i2} + \cdots + \beta_p X_{ip} + \epsilon_i \tag{1}$$

Each $\beta_j$ represents the average effect on $Y$ of a one-unit increase in $X_j$, *holding all other predictors fixed* (ISL ch.3).

**Step 2 — Define the loss (RSS).**  
We estimate the coefficients by minimising the Residual Sum of Squares:

$$\text{RSS} = \sum_{i=1}^{n}(y_i - \hat{y}_i)^2 \tag{2}$$

where $\hat{y}_i = \hat{\beta}_0 + \hat{\beta}_1 x_{i1} + \cdots + \hat{\beta}_p x_{ip}$ (ISL ch.3).

**Step 3 — Closed-form solution (Normal Equation).**  
The least-squares estimates can be computed analytically. This gives exact coefficients without iteration (HOML ch.4). The algorithm comparison table in HOML confirms: for the Normal Equation / SVD approach, the number of hyperparameters is **0**, and it requires no feature scaling (HOML ch.4).

**Step 4 — Assess overall significance via the F-statistic.**  
Test whether *at least one* predictor is useful:

$$F = \frac{(\text{TSS} - \text{RSS})/p}{\text{RSS}/(n - p - 1)} \tag{3}$$

where $\text{TSS} = \sum(y_i - \bar{y})^2$ and $\text{RSS} = \sum(y_i - \hat{y}_i)^2$ (ISL ch.3). When $H_0: \beta_1 = \cdots = \beta_p = 0$ is true, $F \approx 1$; a large $F$ provides evidence against $H_0$ (ISL ch.3).

---

## Key Formulas

- **Model equation:** $\hat{Y} = \hat{\beta}_0 + \hat{\beta}_1 X_1 + \cdots + \hat{\beta}_p X_p$ (ISL ch.3)
- **Residual Sum of Squares:** $\text{RSS} = \sum_{i=1}^{n}(y_i - \hat{y}_i)^2$ (ISL ch.3)
- **F-statistic:** $F = \dfrac{(\text{TSS}-\text{RSS})/p}{\text{RSS}/(n-p-1)}$ (ISL ch.3)
- **Total Sum of Squares:** $\text{TSS} = \sum_{i=1}^{n}(y_i - \bar{y})^2$ (ISL ch.3)

---

## Assumptions

- The errors $\epsilon_i$ have a **normal distribution** (required for F-statistic inference) (ISL ch.3)
- Training instances must be **independent and identically distributed (IID)** — shuffling during gradient-based training enforces this (HOML ch.4)
- The relationship between each predictor and the response is **linear** (ISL ch.3)

---

## Step-by-Step Algorithm

1. Collect $n$ observations across $p$ predictor variables and one response variable.
2. Formulate $\hat{Y} = \beta_0 + \beta_1 X_1 + \cdots + \beta_p X_p$.
3. Define RSS as the objective function to minimise (ISL ch.3).
4. Solve for $\hat{\beta}$ via the Normal Equation (closed-form) or gradient descent (HOML ch.4).
5. Compute the F-statistic to test whether any predictor is significant (ISL ch.3).
6. Compute individual $p$-values to assess each predictor's contribution (ISL ch.3).
7. Use $R^2$ and RSE to evaluate overall model fit (ISL ch.3).

---

## Hyperparameters

| Parameter | Effect on Model | How to Tune |
|---|---|---|
| `max_iter` (SGD path) | Max training epochs | Increase if loss hasn't converged (HOML ch.4) |
| `eta0` (learning rate) | Step size during gradient descent | Use learning schedule; default 0.1 (HOML ch.4) |
| `tol` | Convergence threshold | Lower for higher precision (HOML ch.4) |

> [NEEDS REVIEW: insufficient source material for Normal Equation hyperparameter tuning beyond the table in HOML ch.4]

---

## Failure Modes

- **Confounded predictors:** Correlated predictors can make individual $\beta$ estimates unreliable — the shark-attacks example illustrates how omitting temperature distorts conclusions (ISL ch.