## Understanding Your Data

### Core Idea
Exploratory Data Analysis (EDA) is the practice of investigating a dataset through summary statistics and visualizations to uncover its underlying structure, spot anomalies, and build intuition before formal modeling (HOML ch.2). It combines quick numeric glances with graphical methods to reveal patterns, distributions, and relationships among features.

### Why It Matters
EDA helps practitioners detect data quality issues—such as missing values, capped attributes, or extreme scales—that can sabotage downstream algorithms (HOML ch.2). It also identifies promising predictors and nonlinear relationships, guiding feature engineering and preventing blind, error‑prone model building.

### Explanation
The EDA process begins with a **quick look** at the data: using methods like `head()`, `info()`, and `describe()` to grasp structure, missing values, and statistical summaries (HOML ch.2). For example, the California housing dataset revealed a text attribute `ocean_proximity` with five categories and a numerical attribute `total_bedrooms` with 207 missing entries (HOML ch.2). Next, **histograms** for each numerical attribute expose skewed distributions, value caps, and differing scales (HOML ch.2). Scatterplots with geographical coordinates, colored by target value, reveal high‑price clusters near the coast and population‑dense areas (HOML ch.2). The **correlation matrix** pinpoints linear relationships; in the housing data, `median_income` showed the strongest correlation with `median_house_value` (0.687), while the `corr()` function and `scatter_matrix` help spot nonlinear trends (HOML ch.2). Finally, creating **attribute combinations**—such as *rooms_per_household* or *bedrooms_per_room*—often yields features that are far more predictive than the original raw columns (HOML ch.2). All these steps are iterative: insights from one round of visualization often prompt new questions and further transformations.

### Key Terms
- **Exploratory Data Analysis (EDA)**: The phase of investigating data through summaries and plots to inform modeling decisions (HOML ch.2).
- **Correlation coefficient (Pearson’s r)**: A measure (−1 to 1) of linear association between two variables; a value near 1 indicates strong positive linear relationship (HOML ch.2).
- **Histogram**: A plot showing the frequency of data values in contiguous bins; reveals distribution shape and outliers (HOML ch.2).
- **Scatterplot**: A two‑dimensional plot of points for two numerical variables, often enhanced with color, size, or transparency to highlight density and patterns (HOML ch.2).

### Common Misunderstanding
Beginners often treat EDA as a one‑time look at the data before modeling, whereas it is an iterative cycle—findings from initial plots and correlations should loop back into data cleaning, feature engineering, and even revisiting the problem framing (HOML ch.2).

### Interview Relevance
EDAs are a common topic in entry‑level interviews (importance 5/10). Candidates may be asked to describe how they would explore a new dataset, interpret a correlation matrix, or spot data quirks like capped values—exactly the kind of insight gained from the structured discovery process shown in the California housing project.

### Related Topics
None.