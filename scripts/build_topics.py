import json
import re

RAW_MAPPING = [
    (1, "What is Machine Learning", "Foundations", [("HOML", ["1"], "primary"), ("ISL", ["1"], "support")]),
    (2, "AI vs ML vs DL", "Foundations", [("HOML", ["1"], "primary"), ("ISL", ["1"], "support")]),
    (3, "Types of Machine Learning", "Foundations", [("HOML", ["1"], "primary"), ("ISL", ["2"], "support")]),
    (4, "Batch Learning", "Foundations", [("HOML", ["1"], "primary"), ("ISL", ["2"], "reference")]),
    (5, "Online Machine Learning", "Foundations", [("HOML", ["1"], "primary")]),
    (6, "Instance-Based vs Model-Based Learning", "Foundations", [("HOML", ["1"], "primary"), ("ISL", ["2"], "support")]),
    (7, "Challenges in Machine Learning", "Foundations", [("HOML", ["1"], "primary"), ("ISL", ["2"], "support")]),
    (8, "Applications of Machine Learning", "Foundations", [("HOML", ["1"], "primary"), ("ISL", ["1"], "support")]),
    (9, "ML Development Life Cycle", "Foundations", [("HOML", ["2"], "primary"), ("ISL", ["2"], "support")]),
    (10, "Data Roles", "Foundations", [("HOML", ["1"], "reference"), ("ISL", ["1"], "reference")]),
    (11, "What are Tensors", "Data Representation & Tooling", [("HOML", ["2", "12"], "primary"), ("PRML", ["1"], "reference")]),
    (12, "Installing Anaconda / Jupyter / Colab", "Data Representation & Tooling", [("HOML", ["Appendix A"], "primary")]),
    (13, "End-to-End Toy Project", "Data Representation & Tooling", [("HOML", ["2"], "primary"), ("ISL", ["3"], "support")]),
    (14, "How to Frame an ML Problem", "Data Representation & Tooling", [("HOML", ["2"], "primary"), ("ISL", ["2"], "support")]),
    (15, "Working with CSV Files", "Data Ingestion", [("HOML", ["2"], "primary"), ("ISL", ["2"], "reference")]),
    (16, "Working with JSON / SQL", "Data Ingestion", [("HOML", ["2"], "primary")]),
    (17, "Fetching Data from an API", "Data Ingestion", [("HOML", ["2"], "primary")]),
    (18, "Web Scraping", "Data Ingestion", [("HOML", ["2"], "primary")]),
    (19, "Understanding Your Data", "EDA", [("HOML", ["2"], "primary"), ("ISL", ["2"], "support")]),
    (20, "Univariate Analysis", "EDA", [("HOML", ["2"], "primary"), ("ISL", ["3"], "support")]),
    (21, "Bivariate and Multivariate Analysis", "EDA", [("HOML", ["2"], "primary"), ("ISL", ["3"], "support")]),
    (22, "Pandas Profiling", "EDA", [("HOML", ["2"], "primary")]),
    (23, "What is Feature Engineering", "Feature Engineering", [("HOML", ["2", "4"], "primary"), ("ISL", ["7"], "support")]),
    (24, "Feature Scaling - Standardization", "Feature Engineering", [("HOML", ["2"], "primary"), ("ISL", ["6"], "support"), ("PRML", ["3"], "reference")]),
    (25, "Feature Scaling - Normalization", "Feature Engineering", [("HOML", ["2"], "primary"), ("ISL", ["6"], "support")]),
    (26, "Ordinal & Label Encoding", "Feature Engineering", [("HOML", ["2"], "primary"), ("ISL", ["3"], "support")]),
    (27, "One Hot Encoding", "Feature Engineering", [("HOML", ["2"], "primary"), ("ISL", ["3"], "support")]),
    (28, "Column Transformer", "Feature Engineering", [("HOML", ["2"], "primary")]),
    (29, "ML Pipelines", "Feature Engineering", [("HOML", ["2"], "primary"), ("ISL", ["6"], "reference")]),
    (30, "Function Transformer", "Feature Engineering", [("HOML", ["2"], "primary"), ("ISL", ["7"], "support")]),
    (31, "Power Transformer", "Feature Engineering", [("HOML", ["2"], "primary"), ("ISL", ["7"], "support")]),
    (32, "Binning and Binarization", "Feature Engineering", [("HOML", ["2"], "primary"), ("ISL", ["7"], "support")]),
    (33, "Handling Mixed Variables", "Feature Engineering", [("HOML", ["2"], "primary"), ("ISL", ["3"], "support")]),
    (34, "Handling Date and Time Variables", "Feature Engineering", [("HOML", ["2"], "primary")]),
    (35, "Complete Case Analysis", "Missing Data Handling", [("HOML", ["2"], "primary"), ("ISL", ["3"], "reference")]),
    (36, "Simple Imputer - Numerical", "Missing Data Handling", [("HOML", ["2"], "primary")]),
    (37, "Simple Imputer - Categorical", "Missing Data Handling", [("HOML", ["2"], "primary")]),
    (38, "Missing Indicator / Random Sample Imputation", "Missing Data Handling", [("HOML", ["2"], "primary")]),
    (39, "KNN Imputer", "Missing Data Handling", [("HOML", ["2"], "primary"), ("ISL", ["12"], "reference")]),
    (40, "MICE / Iterative Imputer", "Missing Data Handling", [("HOML", ["2"], "primary"), ("ISL", ["3"], "reference")]),
    (41, "What are Outliers", "Outlier Handling", [("HOML", ["9"], "primary"), ("ISL", ["3"], "support")]),
    (42, "Z-Score Method", "Outlier Handling", [("HOML", ["2"], "primary"), ("ISL", ["3"], "support"), ("PRML", ["2"], "reference")]),
    (43, "IQR Method", "Outlier Handling", [("HOML", ["2"], "primary"), ("ISL", ["3"], "support")]),
    (44, "Percentile Method / Winsorization", "Outlier Handling", [("HOML", ["2"], "primary"), ("ISL", ["3"], "support")]),
    (45, "Feature Construction / Splitting", "Advanced Feature Engineering", [("HOML", ["2"], "primary"), ("ISL", ["7"], "support")]),
    (46, "Curse of Dimensionality", "Dimensionality Reduction", [("HOML", ["8"], "primary"), ("ISL", ["6"], "support"), ("PRML", ["1"], "reference")]),
    (47, "PCA Part 1 - Geometric Intuition", "Dimensionality Reduction", [("HOML", ["8"], "primary"), ("ISL", ["12"], "support"), ("PRML", ["12"], "reference")]),
    (48, "PCA Part 2 - Mathematical Formulation", "Dimensionality Reduction", [("HOML", ["8"], "primary"), ("ISL", ["12"], "support"), ("PRML", ["12"], "reference")]),
    (49, "PCA Part 3 - Code & Visualization", "Dimensionality Reduction", [("HOML", ["8"], "primary"), ("ISL", ["12"], "support")]),
    (50, "Simple Linear Regression - Intuition & Code", "Linear Regression", [("HOML", ["4"], "primary"), ("ISL", ["3"], "support")]),
    (51, "Simple Linear Regression - Math & Scratch", "Linear Regression", [("HOML", ["4"], "primary"), ("ISL", ["3"], "support"), ("PRML", ["3"], "reference")]),
    (52, "Regression Metrics", "Linear Regression", [("HOML", ["2"], "primary"), ("ISL", ["3"], "support")]),
    (53, "Multiple Linear Regression - Intuition & Code", "Linear Regression", [("HOML", ["4"], "primary"), ("ISL", ["3"], "support")]),
    (54, "Multiple Linear Regression - Math from Scratch", "Linear Regression", [("HOML", ["4"], "primary"), ("ISL", ["3"], "support"), ("PRML", ["3"], "reference")]),
    (55, "Multiple Linear Regression - Code from Scratch", "Linear Regression", [("HOML", ["4"], "primary"), ("ISL", ["3"], "support")]),
    (56, "Assumptions of Linear Regression", "Linear Regression", [("HOML", ["4"], "primary"), ("ISL", ["3"], "support")]),
    (57, "Gradient Descent from Scratch", "Gradient Descent", [("HOML", ["4"], "primary"), ("ISL", ["6"], "reference"), ("PRML", ["5"], "reference")]),
    (58, "Batch Gradient Descent", "Gradient Descent", [("HOML", ["4"], "primary"), ("ISL", ["6"], "reference")]),
    (59, "Stochastic Gradient Descent", "Gradient Descent", [("HOML", ["4"], "primary"), ("PRML", ["5"], "reference")]),
    (60, "Mini-Batch Gradient Descent", "Gradient Descent", [("HOML", ["4", "11"], "primary")]),
    (61, "Polynomial Regression", "Polynomial & Regularized Regression", [("HOML", ["4"], "primary"), ("ISL", ["7"], "support")]),
    (62, "Bias-Variance Trade-off", "Polynomial & Regularized Regression", [("HOML", ["4"], "primary"), ("ISL", ["2"], "support"), ("PRML", ["1"], "reference")]),
    (63, "Ridge Regression - Intuition & Code", "Polynomial & Regularized Regression", [("HOML", ["4"], "primary"), ("ISL", ["6"], "support")]),
    (64, "Ridge Regression - Math from Scratch", "Polynomial & Regularized Regression", [("HOML", ["4"], "primary"), ("ISL", ["6"], "support"), ("PRML", ["3"], "reference")]),
    (65, "Ridge Regression - Gradient Descent", "Polynomial & Regularized Regression", [("HOML", ["4"], "primary"), ("ISL", ["6"], "reference")]),
    (66, "Ridge Regression - 5 Key Points", "Polynomial & Regularized Regression", [("HOML", ["4"], "primary"), ("ISL", ["6"], "support")]),
    (67, "Lasso Regression", "Polynomial & Regularized Regression", [("HOML", ["4"], "primary"), ("ISL", ["6"], "support")]),
    (68, "Why Lasso Creates Sparsity", "Polynomial & Regularized Regression", [("HOML", ["4"], "primary"), ("ISL", ["6"], "support"), ("PRML", ["3"], "reference")]),
    (69, "ElasticNet Regression", "Polynomial & Regularized Regression", [("HOML", ["4"], "primary"), ("ISL", ["6"], "support")]),
    (70, "Logistic Regression - Perceptron Trick", "Logistic Regression", [("HOML", ["4"], "primary"), ("ISL", ["4"], "support")]),
    (71, "Logistic Regression - Perceptron Code", "Logistic Regression", [("HOML", ["4"], "primary"), ("ISL", ["4"], "support")]),
    (72, "Sigmoid Function", "Logistic Regression", [("HOML", ["4"], "primary"), ("ISL", ["4"], "support"), ("PRML", ["4"], "reference")]),
    (73, "Loss Function / MLE / Binary Cross-Entropy", "Logistic Regression", [("HOML", ["4"], "primary"), ("ISL", ["4"], "support"), ("PRML", ["4"], "reference")]),
    (74, "Derivative of Sigmoid", "Logistic Regression", [("HOML", ["4"], "primary"), ("PRML", ["4"], "reference")]),
    (75, "Logistic Regression - Gradient Descent from Scratch", "Logistic Regression", [("HOML", ["4"], "primary"), ("ISL", ["4"], "support"), ("PRML", ["4"], "reference")]),
    (76, "Accuracy and Confusion Matrix", "Logistic Regression", [("HOML", ["3"], "primary"), ("ISL", ["4"], "support")]),
    (77, "Precision, Recall, F1 Score", "Logistic Regression", [("HOML", ["3"], "primary"), ("ISL", ["4"], "support")]),
    (78, "ROC Curve and AUC", "Logistic Regression", [("HOML", ["3"], "primary"), ("ISL", ["4"], "support")]),
    (79, "Softmax Regression / Multinomial Logistic Regression", "Logistic Regression", [("HOML", ["4"], "primary"), ("ISL", ["4"], "support"), ("PRML", ["4"], "reference")]),
    (80, "Polynomial Features in Logistic Regression", "Logistic Regression", [("HOML", ["4"], "primary"), ("ISL", ["7"], "support")]),
    (81, "Logistic Regression Hyperparameters", "Logistic Regression", [("HOML", ["4"], "primary")]),
    (82, "Naive Bayes Part 1", "Naive Bayes", [("PRML", ["1", "2"], "primary"), ("ISL", ["4"], "support"), ("HOML", ["3"], "reference")]),
    (83, "Naive Bayes Part 2", "Naive Bayes", [("PRML", ["1", "2"], "primary"), ("ISL", ["4"], "support"), ("HOML", ["3"], "reference")]),
    (84, "Naive Bayes Part 3", "Naive Bayes", [("PRML", ["1", "2"], "primary"), ("ISL", ["4"], "support"), ("HOML", ["3"], "reference")]),
    (85, "Naive Bayes Part 4", "Naive Bayes", [("PRML", ["1", "2"], "primary"), ("ISL", ["4"], "support"), ("HOML", ["3"], "reference")]),
    (86, "Naive Bayes Part 5", "Naive Bayes", [("PRML", ["1", "2"], "primary"), ("ISL", ["4"], "support"), ("HOML", ["3"], "reference")]),
    (87, "Naive Bayes - Intuition", "Naive Bayes", [("PRML", ["4"], "primary"), ("ISL", ["4"], "support"), ("HOML", ["3"], "reference")]),
    (88, "Naive Bayes - Mathematics", "Naive Bayes", [("PRML", ["4"], "primary"), ("HOML", ["3"], "reference")]),
    (89, "Naive Bayes - Code Example", "Naive Bayes", [("HOML", ["3"], "primary"), ("ISL", ["4"], "support")]),
    (90, "Naive Bayes - Numerical Data", "Naive Bayes", [("HOML", ["3"], "primary"), ("PRML", ["2"], "reference")]),
    (91, "K-Nearest Neighbors", "KNN", [("HOML", ["1", "3"], "primary"), ("ISL", ["2", "4"], "support"), ("PRML", ["2"], "reference")]),
    (92, "SVM - Geometric Intuition", "SVM", [("HOML", ["5"], "primary"), ("ISL", ["9"], "support")]),
    (93, "SVM - Hard Margin Mathematics", "SVM", [("PRML", ["7"], "primary"), ("HOML", ["5"], "support"), ("ISL", ["9"], "support")]),
    (94, "SVM - Soft Margin Mathematics", "SVM", [("PRML", ["7"], "primary"), ("HOML", ["5"], "support"), ("ISL", ["9"], "support")]),
    (95, "Kernel Trick - Geometric Intuition", "SVM", [("PRML", ["6"], "primary"), ("HOML", ["5"], "support"), ("ISL", ["9"], "support")]),
    (96, "Kernel Trick - Code Example", "SVM", [("HOML", ["5"], "primary"), ("ISL", ["9"], "support")]),
    (97, "Decision Trees - Entropy, Gini, Information Gain", "Decision Trees", [("HOML", ["6"], "primary"), ("ISL", ["8"], "support"), ("PRML", ["14"], "reference")]),
    (98, "Decision Trees - Hyperparameters / Overfitting", "Decision Trees", [("HOML", ["6"], "primary"), ("ISL", ["8"], "support")]),
    (99, "Regression Trees", "Decision Trees", [("HOML", ["6"], "primary"), ("ISL", ["8"], "support")]),
    (100, "Decision Tree Visualization", "Decision Trees", [("HOML", ["6"], "primary"), ("ISL", ["8"], "reference")]),
    (101, "Introduction to Ensemble Learning", "Ensemble Methods", [("HOML", ["7"], "primary"), ("ISL", ["8"], "support")]),
    (102, "Voting Ensemble - Intro", "Ensemble Methods", [("HOML", ["7"], "primary"), ("ISL", ["8"], "support")]),
    (103, "Voting Ensemble - Classification", "Ensemble Methods", [("HOML", ["7"], "primary"), ("ISL", ["8"], "support")]),
    (104, "Voting Ensemble - Regression", "Ensemble Methods", [("HOML", ["7"], "primary"), ("ISL", ["8"], "support")]),
    (105, "Bagging - Intro", "Ensemble Methods", [("HOML", ["7"], "primary"), ("ISL", ["8"], "support")]),
    (106, "Bagging - Classifiers", "Ensemble Methods", [("HOML", ["7"], "primary"), ("ISL", ["8"], "support")]),
    (107, "Bagging - Regressors", "Ensemble Methods", [("HOML", ["7"], "primary"), ("ISL", ["8"], "support")]),
    (108, "Introduction to Random Forest", "Ensemble Methods", [("HOML", ["7"], "primary"), ("ISL", ["8"], "support")]),
    (109, "Random Forest - Bias-Variance", "Ensemble Methods", [("HOML", ["7"], "primary"), ("ISL", ["8"], "support")]),
    (110, "Bagging vs Random Forest", "Ensemble Methods", [("HOML", ["7"], "primary"), ("ISL", ["8"], "support")]),
    (111, "Random Forest Hyperparameters", "Ensemble Methods", [("HOML", ["7"], "primary"), ("ISL", ["8"], "support")]),
    (112, "Hyperparameter Tuning with GridSearchCV", "Ensemble Methods", [("HOML", ["2"], "primary"), ("ISL", ["5"], "support")]),
    (113, "OOB Score", "Ensemble Methods", [("HOML", ["7"], "primary"), ("ISL", ["8"], "support")]),
    (114, "Feature Importance", "Ensemble Methods", [("HOML", ["7"], "primary"), ("ISL", ["8"], "support")]),
    (115, "AdaBoost - Geometric Intuition", "Boosting", [("HOML", ["7"], "primary"), ("ISL", ["8"], "support")]),
    (116, "AdaBoost - Step by Step", "Boosting", [("HOML", ["7"], "primary"), ("ISL", ["8"], "support")]),
    (117, "AdaBoost - Code from Scratch", "Boosting", [("HOML", ["7"], "primary")]),
    (118, "AdaBoost Hyperparameters", "Boosting", [("HOML", ["7"], "primary"), ("ISL", ["8"], "support")]),
    (119, "Bagging vs Boosting", "Boosting", [("HOML", ["7"], "primary"), ("ISL", ["8"], "support")]),
    (120, "Gradient Boosting Explained", "Boosting", [("HOML", ["7"], "primary"), ("ISL", ["8"], "support")]),
    (121, "Gradient Boosting Regression - Mathematics", "Boosting", [("HOML", ["7"], "primary"), ("ISL", ["8"], "support")]),
    (122, "Gradient Boosting for Classification", "Boosting", [("HOML", ["7"], "primary"), ("ISL", ["8"], "support")]),
    (123, "Introduction to XGBoost", "Boosting", [("HOML", ["7"], "primary"), ("ISL", ["8"], "support")]),
    (124, "XGBoost for Regression", "Boosting", [("HOML", ["7"], "primary"), ("ISL", ["8"], "support")]),
    (125, "XGBoost for Classification", "Boosting", [("HOML", ["7"], "primary"), ("ISL", ["8"], "support")]),
    (126, "The Math Behind XGBoost", "Boosting", [("HOML", ["7"], "primary"), ("PRML", ["14"], "reference")]),
    (127, "Stacking and Blending Ensembles", "Boosting", [("HOML", ["7"], "primary"), ("ISL", ["8"], "support")]),
    (128, "K-Means - Geometric Intuition", "Clustering", [("HOML", ["9"], "primary"), ("ISL", ["12"], "support")]),
    (129, "K-Means - sklearn", "Clustering", [("HOML", ["9"], "primary"), ("ISL", ["12"], "support")]),
    (130, "K-Means - From Scratch", "Clustering", [("HOML", ["9"], "primary"), ("ISL", ["12"], "support")]),
    (131, "Agglomerative Hierarchical Clustering", "Clustering", [("HOML", ["9"], "primary"), ("ISL", ["12"], "support")]),
    (132, "DBSCAN Clustering", "Clustering", [("HOML", ["9"], "primary"), ("ISL", ["12"], "support")]),
    (133, "Imbalanced Data", "Advanced Topics", [("HOML", ["3"], "primary"), ("ISL", ["4"], "support")]),
    (134, "Hyperparameter Tuning with Optuna", "Advanced Topics", [("HOML", ["2"], "primary"), ("ISL", ["5"], "support")])
]



TOOLING_TOPICS = {
    "installing_anaconda", "working_with_csv_files",
    "working_with_json_sql", "fetching_data_from_an_api",
    "web_scraping", "pandas_profiling", "column_transformer",
    "ml_pipelines", "decision_tree_visualization",
    "hyperparameter_tuning_rf_using_gridsearchcv",
    "xgboost_for_regression", "xgboost_for_classification",
    "naive_bayes_code_example", "end_to_end_toy_project",
    "knn_code", "svm_kernel_code_example"
}

MATH_FOUNDATION_TOPICS = {
    "what_are_tensors", "curse_of_dimensionality",
    "derivative_of_sigmoid", "why_lasso_creates_sparsity",
    "the_maths_behind_xgboost",
    "gradient_boosting_regression_mathematics",
    "ridge_regression_mathematical_formulation",
    "multiple_linear_regression_mathematical_formulation",
    "simple_linear_regression_mathematical_formulation",
    "naive_bayes_mathematics", "svm_hard_margin_mathematics",
    "svm_soft_margin_mathematics",
    "pca_mathematical_formulation"
}

def classify_topic(slug: str, diff: str) -> str:
    if slug in TOOLING_TOPICS:
        return "tooling"
    if slug in MATH_FOUNDATION_TOPICS:
        return "math_heavy"
    if diff in ("high", "medium"):
        return "algorithm"
    return "concept"

MERGE_MAP = {
    "1": {
        "merge_group": None,
        "merge_role": None
    },
    "2": {
        "merge_group": None,
        "merge_role": None
    },
    "3": {
        "merge_group": None,
        "merge_role": None
    },
    "4": {
        "merge_group": None,
        "merge_role": None
    },
    "5": {
        "merge_group": None,
        "merge_role": None
    },
    "6": {
        "merge_group": None,
        "merge_role": None
    },
    "7": {
        "merge_group": None,
        "merge_role": None
    },
    "8": {
        "merge_group": None,
        "merge_role": None
    },
    "9": {
        "merge_group": None,
        "merge_role": None
    },
    "10": {
        "merge_group": None,
        "merge_role": None
    },
    "11": {
        "merge_group": None,
        "merge_role": None
    },
    "12": {
        "merge_group": None,
        "merge_role": None
    },
    "13": {
        "merge_group": None,
        "merge_role": None
    },
    "14": {
        "merge_group": None,
        "merge_role": None
    },
    "15": {
        "merge_group": None,
        "merge_role": None
    },
    "16": {
        "merge_group": None,
        "merge_role": None
    },
    "17": {
        "merge_group": None,
        "merge_role": None
    },
    "18": {
        "merge_group": None,
        "merge_role": None
    },
    "19": {
        "merge_group": None,
        "merge_role": None
    },
    "20": {
        "merge_group": None,
        "merge_role": None
    },
    "21": {
        "merge_group": None,
        "merge_role": None
    },
    "22": {
        "merge_group": None,
        "merge_role": None
    },
    "23": {
        "merge_group": None,
        "merge_role": None
    },
    "24": {
        "merge_group": None,
        "merge_role": None
    },
    "25": {
        "merge_group": None,
        "merge_role": None
    },
    "26": {
        "merge_group": None,
        "merge_role": None
    },
    "27": {
        "merge_group": None,
        "merge_role": None
    },
    "28": {
        "merge_group": None,
        "merge_role": None
    },
    "29": {
        "merge_group": None,
        "merge_role": None
    },
    "30": {
        "merge_group": None,
        "merge_role": None
    },
    "31": {
        "merge_group": None,
        "merge_role": None
    },
    "32": {
        "merge_group": None,
        "merge_role": None
    },
    "33": {
        "merge_group": None,
        "merge_role": None
    },
    "34": {
        "merge_group": None,
        "merge_role": None
    },
    "35": {
        "merge_group": None,
        "merge_role": None
    },
    "36": {
        "merge_group": None,
        "merge_role": None
    },
    "37": {
        "merge_group": None,
        "merge_role": None
    },
    "38": {
        "merge_group": None,
        "merge_role": None
    },
    "39": {
        "merge_group": None,
        "merge_role": None
    },
    "40": {
        "merge_group": None,
        "merge_role": None
    },
    "41": {
        "merge_group": None,
        "merge_role": None
    },
    "42": {
        "merge_group": None,
        "merge_role": None
    },
    "43": {
        "merge_group": None,
        "merge_role": None
    },
    "44": {
        "merge_group": None,
        "merge_role": None
    },
    "45": {
        "merge_group": None,
        "merge_role": None
    },
    "46": {
        "merge_group": None,
        "merge_role": None
    },
    "47": {
        "merge_group": "pca",
        "merge_role": "intuition"
    },
    "48": {
        "merge_group": "pca",
        "merge_role": "mathematics"
    },
    "49": {
        "merge_group": "pca",
        "merge_role": "implementation"
    },
    "50": {
        "merge_group": "linear_regression",
        "merge_role": "intuition"
    },
    "51": {
        "merge_group": "linear_regression",
        "merge_role": "mathematics"
    },
    "52": {
        "merge_group": None,
        "merge_role": None
    },
    "53": {
        "merge_group": "linear_regression",
        "merge_role": "extension"
    },
    "54": {
        "merge_group": "linear_regression",
        "merge_role": "mathematics_extension"
    },
    "55": {
        "merge_group": "linear_regression",
        "merge_role": "implementation"
    },
    "56": {
        "merge_group": "linear_regression",
        "merge_role": "assumptions"
    },
    "57": {
        "merge_group": "gradient_descent",
        "merge_role": "intuition"
    },
    "58": {
        "merge_group": "gradient_descent",
        "merge_role": "batch"
    },
    "59": {
        "merge_group": "gradient_descent",
        "merge_role": "stochastic"
    },
    "60": {
        "merge_group": "gradient_descent",
        "merge_role": "mini_batch"
    },
    "61": {
        "merge_group": None,
        "merge_role": None
    },
    "62": {
        "merge_group": None,
        "merge_role": None
    },
    "63": {
        "merge_group": "ridge_regression",
        "merge_role": "intuition"
    },
    "64": {
        "merge_group": "ridge_regression",
        "merge_role": "mathematics"
    },
    "65": {
        "merge_group": "ridge_regression",
        "merge_role": "gradient_descent"
    },
    "66": {
        "merge_group": "ridge_regression",
        "merge_role": "key_points"
    },
    "67": {
        "merge_group": None,
        "merge_role": None
    },
    "68": {
        "merge_group": None,
        "merge_role": None
    },
    "69": {
        "merge_group": None,
        "merge_role": None
    },
    "70": {
        "merge_group": "logistic_regression",
        "merge_role": "intuition"
    },
    "71": {
        "merge_group": "logistic_regression",
        "merge_role": "implementation"
    },
    "72": {
        "merge_group": "logistic_regression",
        "merge_role": "sigmoid"
    },
    "73": {
        "merge_group": "logistic_regression",
        "merge_role": "loss_function"
    },
    "74": {
        "merge_group": "logistic_regression",
        "merge_role": "sigmoid_derivative"
    },
    "75": {
        "merge_group": "logistic_regression",
        "merge_role": "gradient_descent"
    },
    "76": {
        "merge_group": None,
        "merge_role": None
    },
    "77": {
        "merge_group": None,
        "merge_role": None
    },
    "78": {
        "merge_group": None,
        "merge_role": None
    },
    "79": {
        "merge_group": None,
        "merge_role": None
    },
    "80": {
        "merge_group": None,
        "merge_role": None
    },
    "81": {
        "merge_group": None,
        "merge_role": None
    },
    "82": {
        "merge_group": "naive_bayes",
        "merge_role": "conditional_probability"
    },
    "83": {
        "merge_group": "naive_bayes",
        "merge_role": "independent_events"
    },
    "84": {
        "merge_group": "naive_bayes",
        "merge_role": "mutually_exclusive"
    },
    "85": {
        "merge_group": "naive_bayes",
        "merge_role": "bayes_theorem"
    },
    "86": {
        "merge_group": "naive_bayes",
        "merge_role": "examples"
    },
    "87": {
        "merge_group": "naive_bayes",
        "merge_role": "intuition"
    },
    "88": {
        "merge_group": "naive_bayes",
        "merge_role": "mathematics"
    },
    "89": {
        "merge_group": "naive_bayes",
        "merge_role": "implementation"
    },
    "90": {
        "merge_group": "naive_bayes",
        "merge_role": "numerical_data"
    },
    "91": {
        "merge_group": None,
        "merge_role": None
    },
    "92": {
        "merge_group": "svm",
        "merge_role": "intuition"
    },
    "93": {
        "merge_group": "svm",
        "merge_role": "hard_margin"
    },
    "94": {
        "merge_group": "svm",
        "merge_role": "soft_margin"
    },
    "95": {
        "merge_group": "svm",
        "merge_role": "kernel_intuition"
    },
    "96": {
        "merge_group": "svm",
        "merge_role": "kernel_implementation"
    },
    "97": {
        "merge_group": "decision_trees",
        "merge_role": "theory"
    },
    "98": {
        "merge_group": "decision_trees",
        "merge_role": "hyperparameters"
    },
    "99": {
        "merge_group": "decision_trees",
        "merge_role": "regression"
    },
    "100": {
        "merge_group": "decision_trees",
        "merge_role": "visualization"
    },
    "101": {
        "merge_group": None,
        "merge_role": None
    },
    "102": {
        "merge_group": "voting_ensemble",
        "merge_role": "intro"
    },
    "103": {
        "merge_group": "voting_ensemble",
        "merge_role": "classification"
    },
    "104": {
        "merge_group": "voting_ensemble",
        "merge_role": "regression"
    },
    "105": {
        "merge_group": "bagging",
        "merge_role": "intro"
    },
    "106": {
        "merge_group": "bagging",
        "merge_role": "classifiers"
    },
    "107": {
        "merge_group": "bagging",
        "merge_role": "regressors"
    },
    "108": {
        "merge_group": None,
        "merge_role": None
    },
    "109": {
        "merge_group": None,
        "merge_role": None
    },
    "110": {
        "merge_group": None,
        "merge_role": None
    },
    "111": {
        "merge_group": None,
        "merge_role": None
    },
    "112": {
        "merge_group": None,
        "merge_role": None
    },
    "113": {
        "merge_group": None,
        "merge_role": None
    },
    "114": {
        "merge_group": None,
        "merge_role": None
    },
    "115": {
        "merge_group": "adaboost",
        "merge_role": "intuition"
    },
    "116": {
        "merge_group": "adaboost",
        "merge_role": "step_by_step"
    },
    "117": {
        "merge_group": "adaboost",
        "merge_role": "implementation"
    },
    "118": {
        "merge_group": "adaboost",
        "merge_role": "hyperparameters"
    },
    "119": {
        "merge_group": None,
        "merge_role": None
    },
    "120": {
        "merge_group": "gradient_boosting",
        "merge_role": "intuition"
    },
    "121": {
        "merge_group": "gradient_boosting",
        "merge_role": "mathematics_regression"
    },
    "122": {
        "merge_group": "gradient_boosting",
        "merge_role": "classification"
    },
    "123": {
        "merge_group": "xgboost",
        "merge_role": "intuition"
    },
    "124": {
        "merge_group": "xgboost",
        "merge_role": "regression"
    },
    "125": {
        "merge_group": "xgboost",
        "merge_role": "classification"
    },
    "126": {
        "merge_group": "xgboost",
        "merge_role": "mathematics"
    },
    "127": {
        "merge_group": None,
        "merge_role": None
    },
    "128": {
        "merge_group": "kmeans",
        "merge_role": "intuition"
    },
    "129": {
        "merge_group": "kmeans",
        "merge_role": "sklearn"
    },
    "130": {
        "merge_group": "kmeans",
        "merge_role": "from_scratch"
    },
    "131": {
        "merge_group": None,
        "merge_role": None
    },
    "132": {
        "merge_group": None,
        "merge_role": None
    },
    "133": {
        "merge_group": None,
        "merge_role": None
    },
    "134": {
        "merge_group": None,
        "merge_role": None
    }
}

def get_slug(topic):
    slug = topic.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'[\s-]+', '_', slug)
    return slug

def main():
    try:
        with open('playlist_raw.json', 'r', encoding='utf-8') as f:
            playlist = json.load(f)
    except FileNotFoundError:
        print("playlist_raw.json not found.")
        return

    day_to_mapping = {m[0]: m for m in RAW_MAPPING}
    day_to_slug = {m[0]: get_slug(m[1]) for m in RAW_MAPPING}

    prereqs_dict = {d: [] for d in range(1, 135)}
    
    # probability_basics -> logistic_regression_loss_function, naive_bayes_intuition
    for target in [73, 87]:
        for d in range(82, 87):
            prereqs_dict[target].append(day_to_slug[d])
            
    # linear_regression -> ridge, lasso, elasticnet
    for target in list(range(63, 70)):
        for d in range(50, 56):
            prereqs_dict[target].append(day_to_slug[d])
            
    # gradient_descent -> ridge_gradient_descent, logistic_regression_gradient_descent
    for target in [65, 75]:
        for d in range(57, 61):
            prereqs_dict[target].append(day_to_slug[d])
            
    # decision_trees -> ensemble_intro, bagging_intro, adaboost_intro, gradient_boosting, random_forest_intro
    for target in [101, 105, 115, 120, 121, 122, 108]:
        for d in range(97, 100):
            prereqs_dict[target].append(day_to_slug[d])
            
    prereqs_dict[98].append(day_to_slug[97])
    prereqs_dict[109].append(day_to_slug[62])
    prereqs_dict[119].append(day_to_slug[62])

    topics_output = []
    total_built = 0
    needs_review_count = 0
    section_counts = {}
    primary_book_counts = {"HOML": 0, "ISL": 0, "PRML": 0}
    difficulty_counts = {"low": 0, "medium": 0, "high": 0}
    interview_high_count = 0

    for item in playlist:
        day = item['index']
        if day not in day_to_mapping:
            continue
            
        m = day_to_mapping[day]
        topic_name = m[1]
        section = m[2]
        sources = m[3]
        slug = day_to_slug[day]
        
        tb_sources = []
        for src in sources:
            tb_sources.append({
                "book": src[0],
                "chapters": src[1],
                "priority": src[2]
            })
            if src[2] == "primary":
                primary_book_counts[src[0]] += 1
                
        diff = "medium"
        if 1 <= day <= 40:
            diff = "low"
        elif day in [51, 54, 57, 58, 59, 60, 62, 63, 64, 65, 66, 67, 68, 69, 72, 73, 74, 82, 83, 84, 85, 86, 87, 88, 92, 93, 94, 95, 96, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126]:
            diff = "high"
            
        imp = None
        if day in [62, 50,51,53,54,55, 72,73,74,75, 57,58,59,60, 108,109,110,111,112,113,114, 120,121,122, 123,124,125,126]:
            imp = 10
        elif day in [63,64,65,66, 67,68, 92,93,94,95,96, 97,98,99, 115,116,117,118, 101,102,103,104,105,106,107, 77, 78, 76]:
            imp = 9
        elif day in [46,47,48,49, 82,83,84,85,86,87,88,89,90, 69, 79]:
            imp = 7
        elif day in [23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45, 19,20,21,22, 52, 81]:
            imp = 5
        elif day in [91, 133, 134]:
            imp = 3
        elif day in [10, 11, 12, 15, 16, 17, 18]:
            imp = 1
            
        if imp in [9, 10]:
            interview_high_count += 1
            
        needs_review = False
        if day == 134:
            needs_review = True
            
        title_raw = item.get('title', '')
        words_topic = set(get_slug(topic_name).split('_'))
        words_raw = set(get_slug(title_raw).split('_'))
        if len(words_topic.intersection(words_raw)) < len(words_topic) * 0.3:
            needs_review = True
            
        note_type = classify_topic(slug, diff)
        m_data = MERGE_MAP.get(str(day), {"merge_group": None, "merge_role": None})
        if not m_data.get("merge_group"): # Check int key fallback
            m_data = MERGE_MAP.get(day, {"merge_group": None, "merge_role": None})
        
        entry = {
            "playlist_day": day,
            "title_raw": title_raw,
            "topic": topic_name,
            "slug": slug,
            "note_type": note_type,
            "url": item.get('url'),
            "duration_seconds": item.get('duration_seconds'),
            "section": section,
            "prerequisites": prereqs_dict[day],
            "textbook_sources": tb_sources,
            "status": "not_started",
            "difficulty": diff,
            "interview_importance": imp,
            "notes_file": f"notes/{slug}.md",
            "needs_review": needs_review,
            "merge_group": m_data["merge_group"],
            "merge_role": m_data["merge_role"]
        }
        
        if day == 134:
            entry["external_reference"] = "Optuna Documentation"
            
        topics_output.append(entry)
        
        total_built += 1
        if needs_review:
            needs_review_count += 1
        section_counts[section] = section_counts.get(section, 0) + 1
        difficulty_counts[diff] += 1
        
    with open('topics.json', 'w', encoding='utf-8') as f:
        json.dump(topics_output, f, indent=2, ensure_ascii=False)
        
    print(f"✓ Total topics built: {total_built}")
    print(f"✓ Topics flagged needs_review: {needs_review_count}")
    print("✓ Section breakdown:")
    for s, c in section_counts.items():
        print(f"  - {s}: {c}")
    print("✓ Textbook coverage (primary):")
    for b, c in primary_book_counts.items():
        print(f"  - {b}: {c}")
    print(f"✓ Difficulty breakdown: low / medium / high counts: {difficulty_counts['low']} / {difficulty_counts['medium']} / {difficulty_counts['high']}")
    print(f"✓ Interview importance: count of topics scored 9-10: {interview_high_count}")

if __name__ == "__main__":
    main()
