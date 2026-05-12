# AI vs ML vs DL

## Core Idea

Machine Learning is the science and art of programming computers so they can learn from data, rather than following explicitly coded rules (HOML ch.1). It is a subset of the broader field of Artificial Intelligence. The textbooks provided focus on Machine Learning and Statistical Learning methods, which form the foundation for understanding how systems improve performance through experience with data.

## Why It Matters

Understanding the scope and definition of Machine Learning clarifies what problems it can solve and which techniques apply. Machine Learning practitioners must recognize that their work involves building systems that automatically detect patterns in data to make predictions or decisions—this fundamentally changes how you approach problem-solving compared to traditional programming. Misunderstanding these boundaries can lead to selecting inappropriate tools or setting unrealistic expectations for what data and algorithms can achieve (HOML ch.1).

## Explanation

Machine Learning is formally defined as: "A computer program is said to learn from experience E with respect to some task T and some performance measure P, if its performance on T, as measured by P, improves with experience E" (HOML ch.1). This definition captures the essence: learning requires measurable performance improvement through exposure to examples.

The textbooks provided focus on supervised and unsupervised statistical learning methods—the core ML toolkit. Supervised learning involves training on labeled data (inputs paired with desired outputs), while unsupervised learning discovers structure in unlabeled data (ISL ch.1). Machine Learning differs from traditional programming: downloading Wikipedia onto a computer is not Machine Learning, because the computer has not learned to perform any task better (HOML ch.1).

The distinction matters practically. A traditional spam filter requires engineers to manually write rules for detecting spam. A Machine Learning spam filter automatically learns which word patterns distinguish spam from legitimate email, adapts when spammers change tactics, and scales to new detection problems without explicit recoding (HOML ch.1).

## Key Terms

- **Supervised Learning:** Training with labeled data (inputs paired with correct outputs) to predict or classify new instances (HOML ch.1)
- **Unsupervised Learning:** Learning from unlabeled data to discover structure, relationships, or groupings (HOML ch.1)
- **Training Set:** The collection of examples a system learns from (HOML ch.1)
- **Experience (E):** The data and feedback a learning system receives (HOML ch.1)
- **Task (T):** The objective the system is trained to perform (HOML ch.1)
- **Performance Measure (P):** The metric used to evaluate whether the system has learned (HOML ch.1)

## Common Misunderstanding

Beginners often conflate Machine Learning with downloading or storing data. Simply having access to large datasets does not constitute machine learning unless a system's performance at a specific task measurably improves through exposure to that data (HOML ch.1).

## Interview Relevance

This concept rarely appears as a standalone interview question but provides essential framing for discussing your approach to problems. Interviewers may ask "Is this a supervised or unsupervised problem?" to assess whether you've correctly classified the task before proposing algorithms.

**Interview Importance: 1/10**

## Related Topics

None (this is a foundational concept with no prerequisites in this curriculum).