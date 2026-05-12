# ML Development Life Cycle

## Core Idea
The ML development life cycle is a structured, end-to-end process for building and deploying machine learning systems, from initial problem framing through to ongoing monitoring and maintenance. It emphasizes that model training is only one step in a much larger pipeline of data preparation, evaluation, and productionization (HOML ch.2).

## Why It Matters
Understanding the full life cycle prevents practitioners from focusing narrowly on algorithms while neglecting critical steps like test set creation, data cleaning, and production monitoring. Proper execution of each phase directly impacts downstream model performance—for instance, how you frame the problem determines which performance measure you select and which algorithms are appropriate (HOML ch.2).

## Explanation
The life cycle begins with looking at the big picture: defining business objectives, framing the problem as supervised/unsupervised and regression/classification, and selecting a performance measure like RMSE or MAE (HOML ch.2). Next comes data acquisition, exploratory visualization to gain insights, and preparation through cleaning, feature scaling, and transformation pipelines (HOML ch.2). A critical early step is setting aside a test set before any exploration to avoid data snooping bias—your brain is an amazing pattern detection system prone to overfitting if it sees the test data (HOML ch.2). Models are then selected, trained, evaluated via cross-validation, and fine-tuned through grid or randomized search (HOML ch.2). Finally, the system is launched into production where monitoring code checks live performance, since models tend to "rot" as the world changes (HOML ch.2).

## Key Terms
- **Data pipeline**: A sequence of data processing components that run asynchronously, with each component pulling data, processing it, and outputting results to a data store (HOML ch.2)
- **Data snooping bias**: The over-optimistic generalization error estimate that results from looking at the test set before model selection (HOML ch.2)
- **Stratified sampling**: Dividing the population into homogeneous subgroups called strata and sampling the right number from each to ensure representativeness (HOML ch.2)

## Common Misunderstanding
Beginners often assume the life cycle is linear—get data, train model, done. In reality, it is highly iterative: insights from model error analysis frequently send you back to earlier stages for additional data preparation or feature engineering (HOML ch.2).

## Interview Relevance
Interview importance is None/10. This topic is foundational orientation material rather than a technical deep-dive. It rarely appears as a specific interview question but provides essential context for understanding where individual techniques fit into practice.

## Related Topics

