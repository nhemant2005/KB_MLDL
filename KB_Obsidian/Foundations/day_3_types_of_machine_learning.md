# Types of Machine Learning

## Core Idea
Machine Learning systems are classified by the type of supervision during training (labeled data, unlabeled data, or reward signals), how they process data (all at once or incrementally), and how they generalize to new cases (comparing examples or building predictive models). These classification criteria help practitioners choose appropriate algorithms for specific problems. (HOML ch.1)

## Why It Matters
Understanding ML system types determines algorithm selection: supervised methods for prediction with labeled data, unsupervised for pattern discovery in unlabeled data, and reinforcement learning for sequential decision-making. This taxonomy directly maps to real-world tasks—regression for price prediction, clustering for customer segmentation, and classification for spam detection. (HOML ch.1)

## Explanation
Machine Learning systems can be categorized along three dimensions. First, by supervision: **supervised learning** uses labeled training data where each instance includes desired solutions (labels), enabling tasks like classification (spam filtering) and regression (price prediction) (HOML ch.1). **Unsupervised learning** works with unlabeled data to discover hidden structure, including clustering (grouping similar visitors), visualization, dimensionality reduction, anomaly detection, and association rule learning (HOML ch.1). **Semisupervised learning** combines labeled and unlabeled data when labeling is costly, while **reinforcement learning** trains agents to maximize rewards through interaction with an environment (HOML ch.1).

Second, by data processing: **batch learning** trains on all available data offline before deployment, while **online learning** trains incrementally on sequential data instances, enabling rapid adaptation and out-of-core learning for massive datasets (HOML ch.1).

Third, by generalization: **instance-based learning** memorizes training examples and uses similarity measures to generalize, while **model-based learning** builds a predictive model from training data by optimizing parameters to minimize a cost function (HOML ch.1).

## Key Terms
- **Classification**: Supervised task predicting discrete class labels from labeled examples (HOML ch.1; ISL ch.2)
- **Regression**: Supervised task predicting continuous numeric values from labeled data (HOML ch.1; ISL ch.2)
- **Clustering**: Unsupervised task grouping similar instances without labels (HOML ch.1; ISL ch.2)
- **Anomaly detection**: Unsupervised task identifying unusual instances that differ from normal training examples (HOML ch.1)
- **Dimensionality reduction**: Unsupervised task simplifying data by merging correlated features while preserving information (HOML ch.1)
- **Online learning**: Training incrementally on sequential data instances (HOML ch.1)
- **Batch learning**: Training on the complete dataset at once, typically offline (HOML ch.1)
- **Instance-based learning**: Generalizing by comparing new instances to stored training examples using similarity measures (HOML ch.1)
- **Model-based learning**: Building a predictive model by training parameters on data, then using the model for predictions (HOML ch.1)

## Common Misunderstanding
Beginners often assume supervised learning requires exclusively labeled data—semisupervised learning leverages cheap unlabeled data alongside sparse labels. Additionally, "online learning" refers to incremental data processing, not necessarily live deployment on a website or network. (HOML ch.1)

## Interview Relevance
This foundational taxonomy is rarely tested directly in interviews (0/10 difficulty), but understanding these categories implicitly underpins all algorithm selection discussions. You demonstrate competence by correctly framing problems (e.g., fraud detection as anomaly detection, not classification).

## Related Topics
No prerequisites listed.