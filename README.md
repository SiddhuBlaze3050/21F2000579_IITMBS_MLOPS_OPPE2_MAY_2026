# MLOps OPPE-2: End-to-End Machine Learning Pipeline & Deployment

**Author:** Siddhartha Devulapalli

**Program:** B.S. in Data Science and Applications, IIT Madras

This repository contains the complete implementation for the OPPE-2 MLOps assessment. The project encompasses the full machine learning lifecycle: from training a fair and interpretable Logistic Regression model to containerizing it with FastAPI, deploying it to Google Kubernetes Engine (GKE) via GitHub Actions CI/CD, and concluding with rigorous stress testing and data drift analysis.

## 🛠️ Technology Stack

* **Modeling & Analysis:** Scikit-learn, Pandas, Numpy, Fairlearn, SHAP
* **API Framework:** FastAPI, Uvicorn
* **Containerization & Deployment:** Docker, Kubernetes (GKE), GCP Artifact Registry
* **CI/CD & Security:** GitHub Actions, GCP Workload Identity Federation (WIF)
* **Testing & Observability:** `wrk` (Lua), GCP Cloud Logging, Evidently AI

---

## 🚀 Deliverables Breakdown

### Deliverable 1–3: Model Training, Fairness & Explainability

* **Objective:** Train a Logistic Regression model to predict heart disease, ensure fairness across demographic groups, and explain feature impacts.
* **Inputs:** Raw clinical dataset (`data/data.csv`).
* **Outputs:**
* Trained Logistic Regression artifact (`model.pkl`).
* SHAP summary plots highlighting the global impact of features (e.g., `cp`, `oldpeak`, `thalach`).
* Fairlearn disparity metrics ensuring equitable prediction boundaries across protected attributes like `gender`.



### Deliverable 4: CI/CD & Kubernetes Deployment (GKE)

* **Objective:** Automate the containerization and deployment of the inference API to a GKE cluster with autoscaling enabled.
* **Inputs:**
* `Dockerfile` for the FastAPI application.
* Kubernetes manifests (`k8s/deployment.yaml`, `k8s/service.yaml`, `k8s/hpa.yaml`).
* GitHub Actions workflow (`.github/workflows/deploy.yml`).


* **Outputs:**
* Automated push of the Docker image to GCP Artifact Registry via Workload Identity Federation authentication.
* Successfully scheduled `heart-disease-api` pods with optimized CPU resource requests (`50m`).
* Public LoadBalancer IP exposing the `/health` and `/predict` endpoints.
* Horizontal Pod Autoscaler (HPA) tracking CPU utilization to scale up to 3 pods.



### Deliverable 5: Production Inference & GCP Observability

* **Objective:** Simulate production traffic and capture structured telemetry for observability.
* **Inputs:** `send_predictions.py` generating 100 synthetic clinical records strictly bounded to the original dataset ranges (e.g., `sno` constrained to `[0, 302]`).
* **Outputs:**
* Bounded synthetic dataset saved to `data/generated_100.csv`.
* 100 successful HTTP 200 POST requests sent sequentially to the GKE LoadBalancer.
* Structured JSON telemetry (Timestamp, 14 input features, predicted output) successfully indexed and queryable in GCP Cloud Logging.



### Deliverable 6: Performance Monitoring & Stress Testing

* **Objective:** Benchmark the GKE deployment's resilience under high-concurrency workloads.
* **Inputs:**
* 100-row synthetic dataset (`data/generated_100.csv`).
* `post_data.lua` script formatting the CSV records into rotating JSON HTTP payloads.
* `wrk` CLI tool configured for 10 threads and 2,500 concurrent connections.


* **Outputs:**
* **Throughput:** Sustained 42.82 Requests Per Second (RPS).
* **Latency:** Mean latency of 3.17s (p99 of 4.93s) due to ASGI event loop queuing.
* **Autoscaling Validation:** The CPU saturation successfully triggered the HPA, scaling the deployment from 1 to 3 pods dynamically to absorb the backlog without crashing the cluster (`RESTARTS: 0`).



### Deliverable 7: Input Data Drift Detection

* **Objective:** Detect statistical distribution shifts between the baseline training data and the incoming synthetic production requests.
* **Inputs:**
* Baseline training dataset (`data/data.csv`).
* Production inference sample (`data/generated_100.csv`).
* `src/drift_detection.py` executing two-sample Kolmogorov-Smirnov (KS) tests.


* **Outputs:**
* Terminal statistical report confirming 12 out of 14 features (85.7%) exhibited statistically significant drift ($p < 0.05$) due to uniform sampling generation vs. real-world Gaussian distribution.
* `drift_summary.json` structured metrics file.
* `drift_report.html` interactive dashboard generated via Evidently AI outlining the exact distribution divergences.



---

## ⚙️ Repository Structure

```text
├── .github/workflows/
│   └── deploy.yml           # CI/CD Pipeline (Build, AR Push, GKE Rollout)
├── data/
│   ├── data.csv             # Baseline training dataset
│   └── generated_100.csv    # Synthetic Deliverable 5 dataset
├── k8s/
│   ├── deployment.yaml      # GKE Deployment (50m CPU requests, RollingUpdate)
│   ├── hpa.yaml             # Horizontal Pod Autoscaler configuration
│   └── service.yaml         # LoadBalancer Service configuration
├── src/
│   ├── app.py               # FastAPI inference application with JSON logging
│   ├── train.py             # Model training, SHAP, and Fairlearn script
│   └── drift_detection.py   # Evidently AI KS-test drift analysis
├── AI_USAGE_DOCUMENT_OPPE2.md # GenAI tooling documentation
├── post_data.lua            # Lua payload script for wrk load testing
├── send_predictions.py      # Deliverable 5 synthetic inference script
├── drift_report.html        # Evidently AI drift dashboard
├── requirements.txt         # Python dependencies
└── Dockerfile               # Container build instructions

```