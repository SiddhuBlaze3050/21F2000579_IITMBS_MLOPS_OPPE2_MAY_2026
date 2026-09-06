import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import RandomizedSearchCV
import joblib

# Install required packages if running interactively: 
# !pip install shap fairlearn scikit-learn pandas numpy

# ==========================================
# 1. Data Loading & Preprocessing (from Notebook)
# ==========================================
# Read from the data directory based on the image provided
df = pd.read_csv('data/data.csv')

df['gender'] = pd.factorize(df['gender'])[0]
cleaned_df = df.dropna()

x = cleaned_df.drop("target", axis=1)
y = cleaned_df["target"]

np.random.seed(42)
x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2)

# ==========================================
# 2. Model Training (from Notebook)
# ==========================================
log_reg_grid = {"C": np.logspace(-4, 4, 20), "solver": ["liblinear"]}
rs_log_reg = RandomizedSearchCV(LogisticRegression(), 
                                param_distributions=log_reg_grid, 
                                cv=5, 
                                n_iter=20, 
                                verbose=False)
rs_log_reg.fit(x_train, y_train)

# Save the model for Phase 2 API development
joblib.dump(rs_log_reg.best_estimator_, "model.pkl")

# ==========================================
# Deliverable 2: Model Explainability (SHAP)
# ==========================================
import shap

best_model = rs_log_reg.best_estimator_
explainer = shap.LinearExplainer(best_model, x_train)
shap_values = explainer.shap_values(x_test)

# Calculate mean absolute SHAP values 
mean_shap = np.abs(shap_values).mean(axis=0)
feature_importance = pd.DataFrame(list(zip(x_train.columns, mean_shap)), columns=['Feature', 'Mean_Abs_SHAP'])
feature_importance = feature_importance.sort_values(by='Mean_Abs_SHAP', ascending=True)

print("--- Deliverable 2: Least Impactful Features ---")
print(feature_importance.head(4))
print("\n")

# ==========================================
# Deliverable 3: Fairness Testing (Fairlearn)
# ==========================================
from fairlearn.metrics import demographic_parity_difference, equalized_odds_difference

# Fairlearn requires numeric target arrays
y_test_numeric = (y_test == "yes").astype(int)
y_pred = best_model.predict(x_test)
y_pred_numeric = (pd.Series(y_pred) == "yes").astype(int)

# Binarize the 'age' column to create sensitive groups (e.g., above or below median age)
age_median = x_test['age'].median()
sensitive_features_age = (x_test['age'] > age_median).astype(int)

dp_diff = demographic_parity_difference(y_test_numeric, 
                                        y_pred_numeric, 
                                        sensitive_features=sensitive_features_age)

eo_diff = equalized_odds_difference(y_test_numeric, 
                                    y_pred_numeric, 
                                    sensitive_features=sensitive_features_age)

print("--- Deliverable 3: Fairness Analysis ('age') ---")
print(f"Demographic Parity Difference: {dp_diff:.4f}")
print(f"Equalized Odds Difference: {eo_diff:.4f}")