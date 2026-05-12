# Simple Linear Regression - Intuition & Code

## Core Idea
Simple Linear Regression models the relationship between one predictor variable and a continuous response by fitting a straight line through the data. It solves the problem of predicting an unknown output $y$ from a known input $x$ when that relationship is approximately linear. It exists because a closed-form, interpretable solution is available that directly minimises prediction error without iteration.

---

## Intuition
The goal is to find a line $\hat{y} = \theta_0 + \theta_1 x$ that sits as close as possible to all data points simultaneously. Think of each data point pulling the line toward itself; the algorithm finds the unique line where the total squared pull is minimised (HOML ch.4). The parameters $\theta_0$ (intercept) and $\theta_1$ (slope) fully describe this line (HOML ch.4). Because the cost surface for this problem is a convex bowl, there is exactly one global minimum, reachable directly via a formula rather than iterative search (HOML ch.4).

---

## Mathematical Formulation

**Step 1 — Write the model in matrix form.**
Stack a column of ones onto the feature matrix so the intercept is absorbed:

$$\hat{y} = X\theta \quad \text{where } X \in \mathbb{R}^{m \times (n+1)}, \; \theta \in \mathbb{R}^{n+1}$$

(HOML ch.4)

**Step 2 — Define the cost as Mean Squared Error (MSE).**
We want to minimise the average squared difference between predictions and targets:

$$\text{MSE}(\theta) = \frac{1}{m}\sum_{i=1}^{m}\!\left(\hat{y}^{(i)} - y^{(i)}\right)^2$$

(HOML ch.4)

**Step 3 — Set the gradient to zero and solve analytically.**
Taking the derivative of MSE with respect to $\theta$, setting it to zero, and solving yields the **Normal Equation**:

$$\hat{\theta} = \left(X^\top X\right)^{-1} X^\top y$$

(HOML ch.4)

**Step 4 — Interpret the result.**
$\hat{\theta}$ is the unique parameter vector that minimises the cost function. Once computed, predictions on new data are simply $\hat{y} = X_{\text{new}}\,\hat{\theta}$ (HOML ch.4).

**Step 5 — Alternative via pseudoinverse.**
When $X^\top X$ is singular, Scikit-Learn uses the Moore-Penrose pseudoinverse $X^+$, computed via SVD, giving $\hat{\theta} = X^+ y$ (HOML ch.4).

---

## Key Formulas

- **Linear model:** $\hat{y} = \theta_0 + \theta_1 x_1$ (HOML ch.4)
- **MSE cost:** $\text{MSE}(\theta) = \frac{1}{m}\sum_{i=1}^{m}\!\left(\hat{y}^{(i)} - y^{(i)}\right)^2$ (HOML ch.4)
- **Normal Equation:** $\hat{\theta} = \left(X^\top X\right)^{-1} X^\top y$ (HOML ch.4)
- **Pseudoinverse solution:** $\hat{\theta} = X^+ y$ (HOML ch.4)

---

## Assumptions

- The relationship between predictor and response is linear (HOML ch.4)
- The noise added to the data is Gaussian (the textbook generates data as $y = 4 + 3x + \text{Gaussian noise}$, implying this assumption) (HOML ch.4)
- $X^\top X$ must be invertible for the Normal Equation; features must not be redundant and $m \geq n$ (HOML ch.4)

---

## Step-by-Step Algorithm

1. Collect training data $(X, y)$.
2. Prepend a column of ones to $X$ to create $X_b$ (absorbs the bias term $\theta_0$). (HOML ch.4)
3. Compute $X_b^\top X_b$.
4. Invert $X_b^\top X_b$ (or use pseudoinverse via SVD if singular). (HOML ch.4)
5. Multiply: $\hat{\theta} = \left(X_b^\top X_b\right)^{-1} X_b^\top y$. (HOML ch.4)
6. Store $\hat{\theta}$; the model is fully trained.
7. For new input $X_{\text{new}}$, prepend ones and compute $\hat{y} = X_{\text{new},b}\,\hat{\theta}$. (HOML ch.4)

---

## Hyperparameters

| Parameter | Effect on model | How to tune |
|---|---|---|
| None (closed-form) | The Normal Equation has no hyperparameters; $\hat{\theta}$ is computed directly | N/A (HOML ch.4) |

> [NEEDS REVIEW: insufficient source material]

---

## Failure Modes

- **Too many features:** The Normal Equation inverts an $(n+1)\times(n+1)$ matrix at $O(n^{2.4})$–$O(n^3)$ complexity; it becomes very slow when $n$ is large (e.g., 100,000 features) (HOML ch.4).
- **Singular matrix:** If $m < n$ or features are redundant, $X^\top X$ is not invertible and the Normal Equation fails; the pseudoinverse handles this edge case (HOML ch.4).
- **Noise obscures true parameters:** Even moderate Gaussian noise prevents exact recovery of the true $\theta$ (HOML ch.4).
- **Memory constraint:** Both Normal Equation and SVD are $O(m)$ in instances, so large datasets that cannot fit in memory cause problems (