# AI-Powered Data Center Management Platform

An AI Control Room for data centers — monitors power & cooling, predicts failures, and guides operators with actionable recommendations.

## Features

- **Live Overview**: Real-time topology grid, PUE, power consumption, temperature heatmap
- **AI Anomaly Detection**: IsolationForest + Prophet forecasting with ensemble Risk Score (0-100)
- **Human-in-the-Loop**: Accept/Reject AI recommendations → auto-generated work orders
- **What-If Simulation**: Modify cooling setpoints → see projected energy savings instantly
- **Audit Trail**: Full log of every operator action for compliance

## Quick Start

`ash
# 1. Clone and enter the project
cd datacenter-ai

# 2. Download Kaggle datasets (requires: pip install kaggle)
#    Hot corridor temperature data
kaggle datasets download -d mbjunior/data-centre-hot-corridor-temperature-prediction -p ml/data/raw/
unzip ml/data/raw/data-centre-hot-corridor-temperature-prediction.zip -d ml/data/raw/
mv ml/data/raw/*.csv ml/data/raw/hot_corridor.csv 2>/dev/null || true

#    Cooling control data
kaggle datasets download -d programmer3/data-center-cold-source-control-dataset -p ml/data/raw/
unzip ml/data/raw/data-center-cold-source-control-dataset.zip -d ml/data/raw/
mv ml/data/raw/*.csv ml/data/raw/cooling_control.csv 2>/dev/null || true

# 3. Train ML models (requires: pip install -r backend/requirements.txt)
cd backend
pip install -r requirements.txt
cd ..
python ml/train_and_save.py   # Trains IF + Prophet, saves to ml/artifacts/

# 4. Start with Docker
docker-compose -f docker/docker-compose.yml up --build

# 5. Open browser
#    Frontend:   http://localhost
#    API docs:   http://localhost/api/v1/docs
`

## Local Development (without Docker)

`ash
# Backend
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Frontend (separate terminal)
cd frontend
npm install
npm run dev
`

## Demo Helpers

`ash
# Force a critical alert for live demo
curl -X POST \"http://localhost:8000/api/v1/demo/inject-anomaly?device_id=RACK-A1\"

# Check ML model status
curl http://localhost:8000/api/v1/ml/model-registry

# View audit log
curl http://localhost:8000/api/v1/audit-log
`

## Architecture

- **Frontend**: React 18 + Vite + TypeScript + Tailwind CSS + Zustand + React Query
- **Backend**: FastAPI (Python 3.11) + asyncio EventBus
- **ML**: scikit-learn IsolationForest + Prophet + custom RiskScorer ensemble
- **Database**: SQLite with SQLAlchemy ORM + Alembic migrations
- **Deployment**: Docker + Nginx reverse proxy

## Screens

| Screen | URL | Purpose |
|--------|-----|---------|
| Overview | / | Live topology, KPI strip, What-If simulator |
| AI Anomalies | /anomalies | Alert panel with Accept/Reject |
| Actions | /actions | Work orders + audit log |

## ML Models

| Model | Purpose | Weight |
|-------|---------|--------|
| IsolationForest | Anomaly detection on 6 sensor features | 50% |
| Prophet Forecaster | 60-min temperature/power forecast | 35% |
| RiskScorer Ensemble | Combined Risk Score 0-100 | — |
| DriftMonitor | KS-test statistical drift detection | — |
| WhatIfSimulator | Counterfactual cooling scenarios | — |

## Risk Thresholds

| Score | Status | Color |
|-------|--------|-------|
| 0-35 | Healthy | Green |
| 35-65 | At Risk | Amber |
| 65-100 | Critical | Red |

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | /api/v1/health | Liveness check |
| GET | /api/v1/devices | All devices with risk scores |
| GET | /api/v1/sensors/latest | Latest reading per device |
| GET | /api/v1/alerts | Paginated anomaly alerts |
| POST | /api/v1/alerts/{id}/accept | Accept → work order |
| POST | /api/v1/alerts/{id}/reject | Reject → audit log |
| GET | /api/v1/work-orders | Work orders |
| PATCH | /api/v1/work-orders/{id} | Update step / status |
| GET | /api/v1/kpis | PUE, savings, alerts |
| POST | /api/v1/simulation/what-if | Cooling scenario |
| GET | /api/v1/audit-log | Full audit trail |
| GET | /api/v1/ml/model-registry | Model versions + drift |
| POST | /api/v1/demo/inject-anomaly | Force alert for demo |
| WS | /ws/sensors | Real-time sensor stream |

## License

MIT
