```markdown
# Instance-Based vs Model-Based Learning

## Core Idea
Machine Learning systems generalize using two distinct approaches: instance-based learning memorizes training examples and compares new instances via a similarity measure, while model-based learning builds a compact mathematical model from data and uses it for predictions (HOML ch.1). This taxonomy classifies *how* an algorithm makes predictions.

## Why It Matters
Understanding this distinction helps practitioners select appropriate algorithms for a given problem. Instance-based methods (like k-Nearest Neighbors) are simple and require no training, but can be slow at prediction time; model-based methods invest upfront in training for fast inference, and their learned parameters can offer insights into patterns in the data (HOML ch.1).

## Explanation
Instance-based learning generalizes by heart: the system stores training examples, then uses a similarity measure to compare new instances to them. For example, a spam filter could flag emails sharing many words with known spam (HOML ch.1). In contrast, model-based learning builds a model—such as a linear function—from training data. You select a model type (e.g., linear), train it by finding optimal parameters ($\theta_0, \theta_1$) that minimize a cost function, then make predictions by applying the model to new inputs (HOML ch.1). The linear model $\text{life\_satisfaction} = \theta_0 + \theta_1 \times \text{GDP\_per\_capita}$ exemplifies this: training discovers $\theta_0 = 4.85$ and $\theta_1 = 4.91 \times 10^{-5}$, enabling predictions like 5.96 for Cyprus (HOML ch.1). Both approaches are forms of supervised learning when labels are provided (HOML ch.1).

## Key Terms
- **Instance-based learning**: Learns by memorizing training examples; generalizes by comparing new instances to stored examples using a similarity measure (HOML ch.1)
- **Model-based learning**: Builds a model from training data; uses the model with learned parameters to make predictions (HOML ch.1)
- **Similarity measure**: A function quantifying how alike two instances are (e.g., counting shared words between emails) (HOML ch.1)
- **Model parameter**: A value internal to the model (e.g., $\theta_0$, $\theta_1$ in a linear equation) that is learned during training (HOML ch.1)
- **Cost function**: A metric measuring how poorly a model performs; training aims to minimize it (HOML ch.1)

## Common Misunderstanding
Beginners often assume instance-based methods are always inferior to model-based ones; however, instance-based methods require no training phase and can be highly effective when combined with appropriate similarity measures and enough representative data (HOML ch.1).

## Interview Relevance
This concept appears in foundational ML discussions and is useful for understanding algorithm selection trade-offs, though interview importance is rated 0/10. Interviewers may briefly note that k-Nearest Neighbors exemplifies instance-based learning while Linear Regression exemplifies model-based learning (HOML ch.1).

## Related Topics
[Related concepts are embedded throughout this note.]
```