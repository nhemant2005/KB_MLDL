# Data Roles

## Core Idea
In machine learning, data is partitioned into subsets that serve different roles: training, validation, and test sets are used to build, tune, and evaluate models, while a train‑dev set helps diagnose data mismatch. (HOML ch.1)

## Why It Matters
Without a proper split of data into these roles, a practitioner cannot reliably estimate how well a model will perform on new, unseen instances, leading to overfitting or overly optimistic performance expectations. (HOML ch.1) This directly impacts the trustworthiness of a deployed model.

## Explanation
The **training set** is used to fit the model’s parameters. After training, the model’s true generalization ability is estimated using a held‑out **test set**. To avoid biasing this estimate, hyperparameters are tuned on a separate **validation set** — a portion of the training data that is not used for final parameter fitting. When the training data distribution differs from the production data (data mismatch), a **train‑dev set** (sampled from the training distribution) can reveal whether poor validation performance stems from overfitting or from the distribution gap. (HOML ch.1)

## Key Terms
- Training set: The data subset used to adjust model parameters. (HOML ch.1)
- Test set: A held‑out subset that provides an unbiased estimate of generalization error. (HOML ch.1)
- Validation set: A portion of the training data used to select the best model and tune hyperparameters. (HOML ch.1)
- Train‑dev set: A subset drawn from the training distribution that helps separate overfitting from data‑mismatch issues. (HOML ch.1)

## Common Misunderstanding
Beginners often use the test set to tune hyperparameters, which causes the test error to no longer reflect true generalization performance. (HOML ch.1)

## Interview Relevance
The concept is foundational but rarely asked about directly (importance 1/10). In interviews it may appear as part of broader questions about preventing overfitting or evaluating models.

## Related Topics
None.