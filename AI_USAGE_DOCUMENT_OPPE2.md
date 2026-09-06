# OPPE AI Usage Documentation

**Student**: Siddhartha Devulapalli \
**Roll Number**: 21F2000579 \
**Exam Date**: September 6, 2026

---

## AI Tools Utilized and Conversation History

> List all GenAI / LLM tools used during the exam
> Provide **public share links** to AI chats or attach conversation files if links are not available

* **Tool Name:** Gemini
* **Purpose:** End-to-end assistance for OPPE-2 MLOps pipeline construction, including Docker containerization, Kubernetes (GKE) deployments, GitHub Actions CI/CD debugging (WIF/Artifact Registry), `wrk` load testing, and Evidently AI drift detection.
* **Shared Chat Link:** *https://share.gemini.google/nfJkVLkPli1N*
* **Notes:** This single Gemini thread was the only AI tool utilized during the entire OPPE-2 examination.



---

## Key Areas of AI Assistance

### Pipeline Architecture & Debugging

* **GitHub Actions (CI/CD):** Resolved complex GCP Workload Identity Federation (WIF) authentication failures by properly mapping OIDC `attribute.repository` claims and explicitly passing the `project_id` to GKE authentication steps. Bypassed `docker-credential-gcloud` issues by directly piping OAuth tokens to `docker login`.
* **Kubernetes (GKE) Deployment:** Diagnosed and resolved `PodUnschedulable` (Insufficient CPU) errors by optimizing the `deployment.yaml` resource requests (lowering CPU to `50m`) and tuning the rolling update strategy to fit node capacity.
* **Data Generation & Observability:** Fixed an issue where synthetic inference data generated uniformly out-of-bound serial numbers (`sno`), causing model prediction skew.
* **Load Testing:** Generated a custom Lua script to format nested JSON payloads for high-concurrency `wrk` benchmarking (2,500 connections).
* **Drift Detection (Evidently AI):** Resolved deep C++ standard library linker errors (`CXXABI_1.3.15`) and Numpy 2.x/Pandas 3.x dependency conflicts that were crashing the Evidently report generation module.

---

## Prompts and Responses Used

> Include **all prompts** that contributed to solving the exam tasks
> Include **all responses** in case of public share links are not available to share

### Tool Name #1: Gemini

* **Prompt 1:** `I got error here. I think we have not pushed the data folder to github hence the error... FileNotFoundError: [Errno 2] No such file or directory: 'data/data.csv'`
* **Response Log:** The AI provided the Git commands to force-add the dataset (`git add -f data/data.csv`) and remove it from `.gitignore` so the CI/CD training step could access it.


* **Prompt 2:** `Error: google-github-actions/auth failed with: failed to generate Google Cloud OAuth 2.0 Access Token... Permission 'iam.serviceAccounts.getAccessToken' denied on resource`
* **Response Log:** The AI identified that the Workload Identity Pool lacked the proper attribute mappings and provided the `gcloud iam workload-identity-pools providers update-oidc` command to map `assertion.repository` to `attribute.repository`, alongside the necessary IAM token creator bindings.


* **Prompt 3:** `Cannot schedule pods: Insufficient cpu. no new claims to deallocate.`
* **Response Log:** The AI identified that the default GKE node was maxed out on allocatable CPU. It provided an updated `k8s/deployment.yaml` dropping CPU requests to `50m` and changing the `rollingUpdate` strategy (`maxSurge: 0`, `maxUnavailable: 1`).


* **Prompt 4:** `Surprisingly I got all of them as no. Is this a problem?` *(During Deliverable 5 prediction testing)*
* **Response Log:** The AI executed background Python code to check model coefficients and found `sno` had a negative weight. It corrected the `send_predictions.py` script to sample `sno` within the valid bounds `[0, 302]` instead of `[1000, 9999]`, successfully balancing the predictions.


* **Prompt 5:** `ImportError: /lib/x86_64-linux-gnu/libstdc++.so.6: version 'CXXABI_1.3.15' not found`
* **Response Log:** The AI identified a dynamic linker conflict where the host OS library was overriding the micromamba library. It provided the fix: `export LD_LIBRARY_PATH=/opt/micromamba/lib:$LD_LIBRARY_PATH`, allowing Evidently AI to import correctly.



---

## Files Generated with AI Assistance

### Fully AI-Generated (>90%)

1. `post_data.lua` - Lua script formatting 100 JSON payloads for `wrk` load testing.
2. `send_predictions.py` - Script for Deliverable 5 to generate bounded synthetic data and log per-sample predictions to GCP.
3. `src/drift_detection.py` - Pipeline to compute KS-tests for statistical drift and generate the Evidently HTML dashboard.

### Heavily AI-Assisted (50-90%)

1. `.github/workflows/deploy.yml` - CI/CD pipeline integrated with WIF, Artifact Registry Docker builds, and GKE rollouts.
2. `k8s/deployment.yaml` - Kubernetes manifest optimized for resource constraints and rolling update limits.

---

## Critical AI-Assisted Decisions

### ✅ Successful AI Recommendations

1. **GKE Resource Tuning:**
* *Problem:* Kubernetes hung indefinitely on `ContainerCreating` because the new pod required more CPU than the node had available during a standard rolling update.
* *AI Solution:* Dropped the container CPU request to `50m` and strictly enforced a 1-out, 1-in replacement strategy (`maxSurge: 0`).
* *Impact:* Allowed successful deployment and scaling on the limited GKE cluster.


2. **Evidently AI Dependency Pinning:**
* *Problem:* Generating the data drift report failed with hidden module errors due to modern Pandas 3.x and Numpy 2.x breaking legacy Evidently APIs.
* *AI Solution:* Instructed a strict environment downgrade (`pandas==2.2.2`, `numpy==1.26.4`, `evidently==0.4.33`) and updated the `LD_LIBRARY_PATH`.
* *Impact:* Restored compatibility and successfully generated the required HTML dashboard without code rewrites.


3. **Direct Docker OAuth Authentication in CI:**
* *Problem:* `gcloud auth configure-docker` failed inside GitHub Actions due to token generation permission errors in the subshell.
* *AI Solution:* Altered the workflow to request an `access_token` from WIF and pipe it directly to `docker login -u oauth2accesstoken`.
* *Impact:* Bypassed the gcloud credential helper bug and successfully pushed the FastAPI container to Artifact Registry.