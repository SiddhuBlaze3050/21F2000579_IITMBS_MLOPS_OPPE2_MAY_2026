import json
import pandas as pd
import numpy as np
from scipy.stats import ks_2samp
from sklearn.model_selection import train_test_split

# 1. Load baseline data and prepare training reference split
df_raw = pd.read_csv("data/data.csv")
df_raw['gender'] = pd.factorize(df_raw['gender'])[0]
cleaned_df = df_raw.dropna()

x = cleaned_df.drop("target", axis=1)
y = cleaned_df["target"]

np.random.seed(42)
x_train, _ = train_test_split(x, test_size=0.2, random_state=42)

# 2. Load the 100-row incoming production sample from Deliverable 5
current_df = pd.read_csv("data/generated_100.csv")

feature_cols = [
    "sno", "age", "gender", "cp", "trestbps", "chol", "fbs",
    "restecg", "thalach", "exang", "oldpeak", "slope", "ca", "thal"
]
reference_df = x_train[feature_cols].copy()
current_df = current_df[feature_cols].copy()

print("=" * 70)
print("DELIVERABLE 7: INPUT DATA DRIFT DETECTION REPORT")
print("=" * 70)
print(f"Reference Dataset (Training Set) Size : {len(reference_df)} rows")
print(f"Current Dataset (Generated Sample) Size: {len(current_df)} rows\n")

# 3. Statistical Drift Computation (Two-sample Kolmogorov-Smirnov Test)
drift_results = []
drift_count = 0
alpha = 0.05

for col in feature_cols:
    stat, p_val = ks_2samp(reference_df[col], current_df[col])
    is_drift = bool(p_val < alpha)
    if is_drift:
        drift_count += 1
    drift_results.append({
        "Feature": col,
        "KS_Statistic": round(stat, 4),
        "P_Value": f"{p_val:.4e}",
        "Drift_Detected": "YES" if is_drift else "NO"
    })

results_df = pd.DataFrame(drift_results)
print(results_df.to_string(index=False))

drift_share = drift_count / len(feature_cols)
dataset_drift = drift_share >= 0.5

print("-" * 70)
print(f"Total Features Analyzed : {len(feature_cols)}")
print(f"Features Showing Drift  : {drift_count} ({drift_share * 100:.1f}%)")
print(f"Overall Dataset Drift   : {'DRIFT DETECTED' if dataset_drift else 'NO DATASET DRIFT'}")
print("-" * 70)

# Save statistical summary report
summary_dict = {
    "total_features": len(feature_cols),
    "drifted_features": drift_count,
    "drift_share": round(drift_share, 4),
    "dataset_drift": dataset_drift,
    "feature_details": drift_results
}
with open("drift_summary.json", "w") as f:
    json.dump(summary_dict, f, indent=2)

# 4. Generate Evidently Visual Report
print("\nGenerating Evidently HTML and JSON drift reports...")
try:
    from evidently.report import Report
    from evidently.metric_preset import DataDriftPreset

    report = Report(metrics=[DataDriftPreset()])
    report.run(reference_data=reference_df, current_data=current_df)
    report.save_html("drift_report.html")
    with open("drift_report.json", "w") as f:
        f.write(report.json())
    print("Reports successfully generated: 'drift_report.html' and 'drift_report.json'")

except Exception as e:
    import traceback
    print("\n--- EXACT EVIDENTLY ERROR ---")
    traceback.print_exc()
    print("-----------------------------")