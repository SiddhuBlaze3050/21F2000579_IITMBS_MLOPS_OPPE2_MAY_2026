import time
import requests
import pandas as pd
import numpy as np

API_URL = "http://35.223.226.24/predict"

df = pd.read_csv("data/data.csv")
df['gender'] = pd.factorize(df['gender'])[0]
cleaned_df = df.dropna().drop("target", axis=1)

np.random.seed(42)
records = []
for _ in range(100):
    row = {
        "sno": float(np.random.uniform(cleaned_df['sno'].min(), cleaned_df['sno'].max())),
        "age": float(np.random.uniform(cleaned_df['age'].min(), cleaned_df['age'].max())),
        "gender": int(np.random.choice([0, 1])),
        "cp": float(np.random.choice(cleaned_df['cp'].unique())),
        "trestbps": float(np.random.uniform(cleaned_df['trestbps'].min(), cleaned_df['trestbps'].max())),
        "chol": float(np.random.uniform(cleaned_df['chol'].min(), cleaned_df['chol'].max())),
        "fbs": float(np.random.choice([0, 1])),
        "restecg": float(np.random.choice(cleaned_df['restecg'].unique())),
        "thalach": float(np.random.uniform(cleaned_df['thalach'].min(), cleaned_df['thalach'].max())),
        "exang": float(np.random.choice([0, 1])),
        "oldpeak": float(np.round(np.random.uniform(cleaned_df['oldpeak'].min(), cleaned_df['oldpeak'].max()), 1)),
        "slope": float(np.random.choice(cleaned_df['slope'].unique())),
        "ca": float(np.random.choice(cleaned_df['ca'].unique())),
        "thal": float(np.random.choice(cleaned_df['thal'].unique()))
    }
    records.append(row)

sample_df = pd.DataFrame(records)
sample_df.to_csv("data/generated_100.csv", index=False)
print("Saved refreshed 100-row dataset to data/generated_100.csv")

print(f"Starting per-sample inference against {API_URL}...")
counts = {"yes": 0, "no": 0}
for idx, row in sample_df.iterrows():
    payload = row.to_dict()
    try:
        res = requests.post(API_URL, json=payload, timeout=5)
        if res.status_code == 200:
            pred = res.json().get("prediction")
            counts[pred] = counts.get(pred, 0) + 1
            print(f"[{idx+1:03d}/100] Prediction: {pred}")
        else:
            print(f"[{idx+1:03d}/100] HTTP {res.status_code}")
    except Exception as e:
        print(f"[{idx+1:03d}/100] Error: {e}")
    time.sleep(0.03)

print(f"\nCompleted: {counts}")