# Data Center AI — Fix Plan

## Project Overview
AI-Powered Data Center Management Platform with FastAPI backend, React frontend, 5-model ML ensemble, Docker deployment, and WebSocket real-time updates.

## Scope
Fix all runtime errors, build failures, and logic bugs WITHOUT changing the existing architecture.

---

## Phase 1: Critical Backend Fixes (8 files)

### 1.1 `backend/app/core/event_bus.py`
- **Issue:** `Optional` used on line 27 but not imported
- **Fix:** Add `Optional` to the `from typing import` line

### 1.2 `backend/app/schemas/device.py`
- **Issue:** `SensorReadingResponse` referenced as forward ref but never imported
- **Fix:** Add `from .sensor import SensorReadingResponse` import

### 1.3 `backend/app/schemas/cyber.py`
- **Issue:** `CyberScenarioBase` missing `target_device_id` and `intensity` fields that `app/api/v1/cyber.py` expects
- **Fix:** Add `target_device_id: Optional[str] = None` and `intensity: float = 0.5` to `CyberScenarioBase`

### 1.4 `backend/app/services/work_order_service.py`
- **Issue:** Line 93 — incorrect context manager usage (`get_db_context().__enter__()` returns generator, not iterator)
- **Fix:** Use `SessionLocal()` directly with try/finally cleanup

### 1.5 `backend/app/services/alert_consumer.py`
- **Issue:** `_CYBER_ACTION_TEMPLATES` dict has no "default" key — fallback on line 108 raises `KeyError`
- **Fix:** Add a "default" entry to the dictionary

### 1.6 `backend/app/api/v1/alerts.py`
- **Issue:** Line 113 — returns SQLAlchemy model object `wo` directly, FastAPI can't serialize it
- **Fix:** Convert `wo` to `WorkOrderResponse` Pydantic schema before returning

### 1.7 `backend/app/ml/catboost_classifier.py`
- **Issue:** Line 44 — `probs.shape[1]` fails on 1D array (single sample prediction)
- **Fix:** Reshape 1D array to 2D before accessing `shape[1]`

### 1.8 `backend/app/ml/forecaster.py`
- **Issue:** Lines 64, 91 — `pd.api.types.is_datetime_type` does not exist in pandas 2.2.0
- **Fix:** Replace with `pd.api.types.is_datetime64_any_dtype`

---

## Phase 2: Critical Frontend Fixes (12 files)

### 2.1 `frontend/src/hooks/useAlerts.ts`
- **Issue:** React Query v5 removed `onSuccess` from `useQuery`
- **Fix:** Remove `onSuccess`, add `useEffect` to sync data to store

### 2.2 `frontend/src/hooks/useWorkOrders.ts`
- **Issue:** Same `onSuccess` issue + escaped template literal `\$`
- **Fix:** Same `useEffect` pattern + remove backslash from template literal

### 2.3 `frontend/src/components/charts/RiskGauge.tsx`
- **Issue:** Unused `useMemo` import
- **Fix:** Remove unused import

### 2.4 `frontend/src/components/molecules/WorkOrderCard.tsx`
- **Issue:** Unused `useState` import
- **Fix:** Remove unused import

### 2.5 `frontend/src/components/organisms/AuditLogDrawer.tsx`
- **Issue:** Unused `useState` import
- **Fix:** Remove unused import

### 2.6 `frontend/src/components/molecules/DeviceNode.tsx`
- **Issue:** `sensorData` prop typed as `Record<string, number>` but receives `SensorReading`
- **Fix:** Change prop type to `SensorReading | undefined` and add import

### 2.7 `frontend/src/components/organisms/WorkOrderList.tsx`
- **Issue:** Unused `done` parameter on line 28
- **Fix:** Prefix with underscore: `_done`

### 2.8 `frontend/src/pages/SimulationView.tsx`
- **Issue:** Unused `zones` variable on line 120
- **Fix:** Remove from destructuring

### 2.9 `frontend/src/components/molecules/SecurityAlertPanel.tsx`
- **Issue:** Local `Alert` interface has `reason: string` (required) but shared type has `reason?: string` (optional) — type mismatch when Dashboard passes data
- **Fix:** Make `reason` optional in local interface: `reason?: string`

### 2.10 `frontend/src/components/organisms/SimulationPanel.tsx`
- **Issue:** Empty "Annual Cost Saving" display — missing value interpolation
- **Fix:** Add `result.estimated_annual_cost_saving_usd` to the JSX

### 2.11 Cascade fixes (automatically resolved by #2.1 and #2.2)
- `AlertPanel.tsx` — type inference resolves once `useAlerts` is fixed
- `WorkOrderList.tsx` lines 11, 24 — type inference resolves once `useWorkOrders` is fixed

---

## Phase 3: Critical Docker/Infra Fixes (2 files)

### 3.1 `backend/Dockerfile`
- **Issue:** UTF-8 BOM (`U+FEFF`) at start of file — Docker build fails with "invalid reference format"
- **Fix:** Rewrite file without BOM and fix broken `COPY ... 2>/dev/null || true` instruction

### 3.2 `docker/docker-compose.yml`
- **Issue:** Healthcheck uses `curl` which is not installed in `python:3.11-slim` image
- **Fix:** Use python-based healthcheck instead

---

## Phase 4: ML Pipeline Fixes (2 files)

### 4.1 `ml/prepare_data.py`
- **Issue:** `NameError` crash — `df_hot` accessed but never defined when SMD data is missing
- **Fix:** Guard the SMD-dependent code with proper conditional

### 4.2 `ml/model_registry.json`
- **Issue:** Empty `models` array — drift monitoring has nothing to track
- **Fix:** Populate with the 5 model entries (IF, LSTM, XGB, CatBoost, Prophet)

---

## Phase 5: Secondary Backend Fixes (4 files)

### 5.1 `backend/app/ml/forecaster.py` line 103
- **Issue:** Fragile Prophet internal API access (`params.columns`)
- **Fix:** Wrap in try/except

### 5.2 `backend/app/services/simulator.py`
- **Issue:** Deprecated `datetime.utcnow()`
- **Fix:** Replace with `datetime.now(timezone.utc)`

### 5.3 `backend/app/services/kpi_service.py`
- **Issue:** Deprecated `datetime.utcnow()`
- **Fix:** Replace with `datetime.now(timezone.utc)`

### 5.4 `backend/app/ml/risk_scorer.py`
- **Issue:** Unused `Dict` import
- **Fix:** Remove from import

---

## Phase 6: Verification

1. Run `npx tsc --noEmit` in frontend to verify TypeScript compiles
2. Run `npm run build` in frontend to verify production build
3. Run `python -c "from app.main import app"` in backend to verify imports
4. Verify all Python imports resolve correctly

---

## Files NOT Modified (by design)
- UI styling/appearance (user responsibility)
- Architecture/patterns (preserved as-is)
- README.md / HACKATHON.md (documentation, not runtime)
- Alembic migration files (non-critical warnings)
- Docker compose override (redundant but functional)
- Nginx config (functional)
- `.env` files (user should set their own values)
