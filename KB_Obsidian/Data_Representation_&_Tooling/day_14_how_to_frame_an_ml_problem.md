# How to Frame an ML Problem

## Core Idea
Framing a Machine Learning problem means translating a business goal into a precise technical task: identify whether it is supervised or unsupervised, regression or classification, and which performance metric matters. This initial step determines the entire pipeline, from data collection to model selection, and helps avoid costly misalignment with the company’s actual needs (HOML ch.2).  

## Why It Matters
A clear frame prevents building a regressor when the downstream system only needs a category, as happened in the housing price example (HOML ch.2). It directly influences the choice of algorithm, performance measure, and how much effort to invest in tuning, and it ensures the project delivers actionable value (HOML ch.2).

## Explanation
The first action is to ask the business objective: what will the model’s output be used for? In the California housing case, the predicted district price fed another ML system that decided on investments, so the problem was supervised (labeled data available) and a regression task (predicting a continuous value). Specifically, it was multiple regression (many features) and univariate (single target), and because data was small and static, batch learning sufficed (HOML ch.2).  

Choosing the right performance metric then follows naturally. For regression, Root Mean Square Error (RMSE) is the default, as it penalizes large errors more; if outliers are a concern, Mean Absolute Error (MAE) can be used instead (HOML ch.2). Finally, the practitioner must validate assumptions — e.g., verifying that the downstream system actually needs precise prices, not just price categories — because a mis-framed problem can waste months of work (HOML ch.2).  

The distinction between regression (quantitative response) and classification (qualitative response) is fundamental, and the overall framing should also clarify whether the goal is pure prediction or inference (ISL ch.2).

## Key Terms
- **Supervised learning** – Learning from labeled training examples where each input comes with the correct output (HOML ch.2).  
- **Regression** – Task of predicting a continuous numeric value (HOML ch.2).  
- **Classification** – Task of predicting a qualitative or categorical label (ISL ch.2).  
- **Batch learning** – Training on the entire dataset at once, offline (HOML ch.2).  
- **Root Mean Square Error (RMSE)** – A typical regression performance measure giving higher weight to large errors; corresponds to the Euclidean (ℓ₂) norm (HOML ch.2).  
- **Mean Absolute Error (MAE)** – Regression metric using the sum of absolute errors, less sensitive to outliers; corresponds to the Manhattan (ℓ₁) norm (HOML ch.2).  

## Common Misunderstanding
Many beginners treat every regression problem as a purely numeric-prediction task without asking how the output will be used. If the result is later binned into categories (e.g., “cheap”/“expensive”), the problem should have been framed as classification from the start (HOML ch.2).  

## Interview Relevance
0/10 – This concept is almost never a direct interview question, but competent candidates implicitly demonstrate it when they begin a case study by clarifying business goals, problem type, and success metrics.

## Related Topics
- None (no prerequisites)