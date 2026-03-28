# Judges Prep

## 1-minute project explanation

We built an AI-assisted data center operations platform. It simulates live sensor streams, scores device risk, forecasts temperature behavior, and converts high-risk events into operator-facing alerts and work orders. The key product idea is not just anomaly detection, but a human-in-the-loop workflow: detect, explain, accept/reject, audit, and act.

## Tech stack and why we used it

### Frontend
- React 18 + TypeScript + Vite
- Tailwind CSS for fast UI iteration
- Zustand for lightweight client state
- TanStack React Query for API state and polling
- Recharts for KPI and time-series visualization

Why:
- React + Vite gave us the fastest path to a multi-screen dashboard during a hackathon.
- TypeScript reduced UI integration mistakes across many components.
- Zustand is simpler than Redux for a small-to-medium dashboard app.
- React Query fits well because most screens are API-backed and need refetching.

### Backend
- FastAPI on Python 3.11
- SQLAlchemy + Alembic
- SQLite
- APScheduler
- WebSockets for live sensor updates

Why:
- FastAPI is a strong fit for ML-backed APIs, async endpoints, and automatic docs.
- Python lets us keep the ML training and inference code in the same language as the API.
- SQLAlchemy/Alembic gave us a clean data model and migrations.
- SQLite is the fastest hackathon choice for local setup and single-node demo use.
- APScheduler lets us run inference every 30 seconds and drift/KPI jobs on intervals.

### Deployment
- Docker
- Nginx reverse proxy

Why:
- Docker makes the demo reproducible on another machine.
- Nginx gives a clean single-entry deployment pattern for frontend + backend.

## ML models in the codebase

### Models actually loaded by the backend

The backend `MLService` loads these artifacts from [`ml/artifacts`](/C:/Users/ramkr/.verdent/verdent-projects/this-is-the-problem/datacenter-ai/ml/artifacts):

1. Isolation Forest
- File: [`backend/app/ml/isolation_forest.py`](/C:/Users/ramkr/.verdent/verdent-projects/this-is-the-problem/datacenter-ai/backend/app/ml/isolation_forest.py)
- Artifact: `isolation_forest_v1.joblib`
- Purpose: unsupervised anomaly detection on 6 sensor features
- Why used: good hackathon choice for anomaly detection when labels are limited or noisy

2. LSTM Autoencoder
- File: [`backend/app/ml/lstm_autoencoder.py`](/C:/Users/ramkr/.verdent/verdent-projects/this-is-the-problem/datacenter-ai/backend/app/ml/lstm_autoencoder.py)
- Artifact: `lstm_autoencoder_v1.pt`
- Purpose: sequence-level anomaly scoring using 12-step windows
- Why used: catches temporal patterns that a pointwise model can miss

3. XGBoost anomaly scorer
- File: [`backend/app/ml/xgb_anomaly.py`](/C:/Users/ramkr/.verdent/verdent-projects/this-is-the-problem/datacenter-ai/backend/app/ml/xgb_anomaly.py)
- Artifact: `xgb_anomaly_v1.json`
- Purpose: supervised anomaly probability
- Why used: strong performance on tabular labeled data, fast inference

4. CatBoost classifier
- File: [`backend/app/ml/catboost_classifier.py`](/C:/Users/ramkr/.verdent/verdent-projects/this-is-the-problem/datacenter-ai/backend/app/ml/catboost_classifier.py)
- Artifact: `catboost_classifier_v1.cbm`
- Purpose: secondary tabular classifier producing risk probabilities
- Why used: robust gradient boosting alternative for structured data

5. Prophet forecaster
- File: [`backend/app/ml/forecaster.py`](/C:/Users/ramkr/.verdent/verdent-projects/this-is-the-problem/datacenter-ai/backend/app/ml/forecaster.py)
- Artifact: `prophet_temp_v1.joblib`
- Purpose: temperature forecasting and what-if simulation support
- Why used: easy time-series baseline with trend/seasonality support and low implementation cost

6. Risk scorer ensemble
- File: [`backend/app/ml/risk_scorer.py`](/C:/Users/ramkr/.verdent/verdent-projects/this-is-the-problem/datacenter-ai/backend/app/ml/risk_scorer.py)
- Purpose: combine the above model outputs into one interpretable 0-100 score

### Current ensemble weights in code

From [`backend/app/ml/risk_scorer.py`](/C:/Users/ramkr/.verdent/verdent-projects/this-is-the-problem/datacenter-ai/backend/app/ml/risk_scorer.py):

- Isolation Forest: `0.15`
- LSTM Autoencoder: `0.25`
- XGBoost: `0.25`
- CatBoost: `0.20`
- Forecast deviation: `0.10`
- Recent alert frequency bonus: `0.05`

### Risk thresholds in code

- Healthy: `< 35`
- At risk: `35-65`
- Critical: `>= 65`

## What data we trained on

### Local data path
- [`ml/data/raw`](/C:/Users/ramkr/.verdent/verdent-projects/this-is-the-problem/datacenter-ai/ml/data/raw)

### Files currently present
- `hot_corridor.csv`: `56,958` rows
- `cooling_control.csv`: `3,498` rows

### Data sources used by the repo

There are two training/data stories in this repo, and judges may notice that:

1. Kaggle path
- Declared in [`ml/kaggle_run/kernel-metadata.json`](/C:/Users/ramkr/.verdent/verdent-projects/this-is-the-problem/datacenter-ai/ml/kaggle_run/kernel-metadata.json)
- Datasets:
  - `mbjunior/data-centre-hot-corridor-temperature-prediction`
  - `programmer3/data-center-cold-source-control-dataset`

2. OmniAnomaly/SMD path
- Download helper: [`ml/download_data.py`](/C:/Users/ramkr/.verdent/verdent-projects/this-is-the-problem/datacenter-ai/ml/download_data.py)
- Preprocessing: [`ml/prepare_data.py`](/C:/Users/ramkr/.verdent/verdent-projects/this-is-the-problem/datacenter-ai/ml/prepare_data.py)
- It converts `machine-1-1` from the OmniAnomaly ServerMachineDataset into the feature schema used by the app.

### Best honest way to explain this

Say:

"We built the pipeline to support both public data sources and local preprocessing. For anomaly training we normalized server-machine telemetry into our six-feature schema, and for forecasting we used the cooling-control dataset. The saved artifacts in `ml/artifacts` are what the backend loads during inference."

Do not say:

"We trained only on one pristine production-grade data source."

That is not what the repo shows.

## Where we trained the models

### Local training
- Script: [`ml/train_and_save.py`](/C:/Users/ramkr/.verdent/verdent-projects/this-is-the-problem/datacenter-ai/ml/train_and_save.py)
- This script:
  - creates fallback artifacts first
  - trains Isolation Forest
  - trains Prophet
  - trains LSTM autoencoder
  - trains XGBoost
  - trains CatBoost
  - writes artifacts into `ml/artifacts`
  - regenerates notebooks into `ml/notebooks`

### Kaggle training path
- Notebook metadata exists in [`ml/kaggle_run/kernel-metadata.json`](/C:/Users/ramkr/.verdent/verdent-projects/this-is-the-problem/datacenter-ai/ml/kaggle_run/kernel-metadata.json)
- Notebook file exists in [`ml/kaggle_run/datacenter-ai-training.ipynb`](/C:/Users/ramkr/.verdent/verdent-projects/this-is-the-problem/datacenter-ai/ml/kaggle_run/datacenter-ai-training.ipynb)

Best answer:

"We support local training with `ml/train_and_save.py`, and we also kept a Kaggle notebook workflow for reproducible cloud training experiments."

## End-to-end system flow

1. The simulator loads sensor-style data and emits readings.
2. The backend stores readings in SQLite.
3. APScheduler triggers ML inference every 30 seconds.
4. `MLService` builds per-device feature vectors and 12-step sequences.
5. Isolation Forest, LSTM, XGBoost, CatBoost, and Prophet produce signals.
6. `RiskScorer` combines them into a final device risk score.
7. High-risk events become alerts.
8. Operators accept or reject recommendations.
9. Accepted alerts create work orders.
10. All actions are recorded in the audit log.

## Why we did not use only one deep model

Strong answer:

"Because this is an operations product, not only an ML benchmark. We wanted a mix of fast tabular models, one temporal model, and an interpretable ensemble. That gives us better robustness, easier debugging, and lower inference cost than betting everything on one deep model."

## Likely judge questions and good answers

### 1. What problem are you solving?
"We reduce response time to thermal and power anomalies in data center operations by turning raw telemetry into prioritized, explainable actions."

### 2. Why does this need AI?
"Threshold rules only catch simple limit breaches. We wanted anomaly detection, temporal pattern detection, and forecasting, so the system can react before a hard threshold is crossed."

### 3. Which models are actually used?
"The backend currently loads Isolation Forest, LSTM Autoencoder, XGBoost, CatBoost, and Prophet, then combines them through a weighted risk scorer."

### 4. Why Isolation Forest?
"It is a strong unsupervised baseline for tabular anomaly detection and works well when labels are limited."

### 5. Why LSTM Autoencoder?
"To capture sequence anomalies across recent telemetry windows, not just single-point outliers."

### 6. Why XGBoost and CatBoost both?
"They are fast, strong on structured data, and provide a supervised signal when anomaly labels exist. We kept both to compare and ensemble rather than hard-commit to one."

### 7. Why Prophet?
"We needed a fast, understandable forecast model for temperature trends and what-if simulation, and Prophet was the quickest reliable baseline."

### 8. How do you combine model outputs?
"The ensemble is explicit in `risk_scorer.py`; it is a weighted combination of anomaly, sequence, forecast, and alert-frequency signals into a 0-100 risk score."

### 9. What features do you use?
"The main anomaly feature set is inlet temperature, outlet temperature, power, airflow, humidity, and CPU utilization."

### 10. How often does inference run?
"Every 30 seconds through APScheduler."

### 11. Where are predictions stored?
"Risk scores are written back to device rows in the database, and alert records are created for risky conditions."

### 12. Why FastAPI?
"Same language as the ML layer, fast development, async support, and automatic OpenAPI docs."

### 13. Why SQLite?
"For a hackathon it minimizes setup friction and keeps the demo portable. In a production version we would replace it with a time-series or operational database."

### 14. How would you scale this?
"Move from SQLite to Postgres/TimescaleDB or InfluxDB, separate the inference worker, stream sensor data through a queue, and batch inference per device group."

### 15. Is this connected to real hardware?
"Not yet. The current repo demonstrates the full software loop with simulated or replayed telemetry, which is the right stage for hackathon validation."

### 16. How do you prevent unsafe automation?
"We are intentionally human-in-the-loop. The system recommends and logs actions, but operators approve before work orders are created."

### 17. How do you handle model drift?
"There is a drift monitor in the backend using statistical checks over live feature distributions, though it is still lightweight rather than production-grade MLOps."

### 18. How do you evaluate accuracy?
"For supervised models we can use held-out anomaly labels. For unsupervised detection we focus on score behavior, alert usefulness, and operator workflow value. The repo includes training notebooks and saved artifacts, but the evaluation layer is still early."

### 19. What is the most innovative part?
"The product workflow. Many projects stop at anomaly scoring. We connected anomaly scoring, forecasting, explainability, work orders, and audit logging into one operations loop."

### 20. What would you build next?
"Production data integrations, authentication/RBAC, a proper model registry with metrics, and stronger evaluation plus retraining automation."

## Hard questions judges may ask if they inspect closely

### Why is the model registry empty?
Current file [`ml/model_registry.json`](/C:/Users/ramkr/.verdent/verdent-projects/this-is-the-problem/datacenter-ai/ml/model_registry.json) is effectively empty. The API has a fallback response if the registry is missing, but the registry implementation is not finished.

Best answer:
"The artifact pipeline is in place, but the registry metadata layer still needs hardening. For the hackathon we prioritized inference and workflow over full MLOps metadata."

### Are all models trained on the same source?
No. The repo mixes transformed OmniAnomaly/SMD-style telemetry and cooling-control data, plus optional Kaggle training workflow metadata.

Best answer:
"We normalized multiple public sources into a common feature shape to prototype the pipeline quickly. In production we would retrain on one consistent customer telemetry schema."

### Are dummy artifacts used?
Yes, `ml/train_and_save.py` creates fallback artifacts first so the backend can boot even before real training finishes.

Best answer:
"The dummy artifacts are a resilience fallback for local startup. The intended demo path is to replace them with the trained artifacts in `ml/artifacts`."

## Current demo risks you should know before judges arrive

### Verified good
- Backend Python modules now compile cleanly.
- ML pipeline, training files, data files, and artifacts are present.
- Frontend dependencies install successfully.

### Still risky
- The frontend currently does not typecheck or build because many UI files have syntax corruption beyond simple quote escaping.
- There is no authentication or role-based access control.
- SQLite is a demo-only persistence choice.
- The model registry metadata is incomplete.
- Data provenance is mixed and should be explained honestly.

## Best concise answer if a judge asks "What exactly did you build?"

"We built a full-stack AI operations prototype for data centers. The backend ingests telemetry, runs a five-model ensemble plus forecasting, converts that into a transparent risk score, and surfaces alerts, work orders, and audit trails. The point is not just anomaly detection; it is operational decision support with a human approval step."
