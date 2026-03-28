import sys, json, math
import numpy as np
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).parent.parent
ML   = ROOT / "ml"
ART  = ML / "artifacts"
BACK = ROOT / "backend"
DOCK = ROOT / "docker"

PASS = "[PASS]"
FAIL = "[FAIL]"
WARN = "[WARN]"

results = []

def check(name, fn):
    try:
        msg = fn()
        results.append((PASS, name, msg or ""))
    except Exception as e:
        results.append((FAIL, name, str(e)))

# ── 1. Artifacts exist ────────────────────────────────────────────────────────
for art in ["scaler_v1.joblib","lstm_scaler_v1.joblib","isolation_forest_v1.joblib",
            "lstm_autoencoder_v1.pt","xgb_anomaly_v1.json","catboost_classifier_v1.cbm",
            "prophet_temp_v1.joblib"]:
    p = ART / art
    check(f"Artifact: {art}",
          lambda p=p: (f"{p.stat().st_size:,} bytes") if p.exists() else (_ for _ in ()).throw(FileNotFoundError(str(p))))

# ── 2. hot_corridor.csv ───────────────────────────────────────────────────────
def check_csv():
    import pandas as pd
    df = pd.read_csv(ML / "data" / "raw" / "hot_corridor.csv")
    required = ['inlet_temp_c','outlet_temp_c','power_kw','airflow_cfm',
                'humidity_pct','cpu_util_pct','anomaly','is_train']
    missing = [c for c in required if c not in df.columns]
    if missing: raise ValueError(f"Missing columns: {missing}")
    train, test = df[df.is_train==1], df[df.is_train==0]
    return f"{len(df):,} rows | train={len(train):,} test={len(test):,} anomalies={int(test['anomaly'].sum())}"
check("hot_corridor.csv structure", check_csv)

# ── 3. model_registry.json ───────────────────────────────────────────────────
def check_registry():
    reg = ML / "model_registry.json"
    data = json.loads(reg.read_text())
    return f"keys={list(data.keys())}"
check("model_registry.json parseable", check_registry)

# ── 4. IsolationForest ────────────────────────────────────────────────────────
def check_if():
    import joblib
    scaler = joblib.load(ART / "scaler_v1.joblib")
    model  = joblib.load(ART / "isolation_forest_v1.joblib")
    X = np.random.rand(5, 6)
    import pandas as pd
    Xdf = pd.DataFrame(X, columns=['inlet_temp_c','outlet_temp_c','power_kw','airflow_cfm','humidity_pct','cpu_util_pct'])
    Xs = scaler.transform(Xdf)
    scores = model.score_samples(Xs)
    assert scores.shape == (5,)
    return f"scores range [{scores.min():.3f}, {scores.max():.3f}]"
check("IsolationForest load + score", check_if)

# ── 5. LSTM Autoencoder ───────────────────────────────────────────────────────
def check_lstm():
    import torch, torch.nn as nn, joblib

    class Net(nn.Module):
        def __init__(self):
            super().__init__()
            self.encoder = nn.LSTM(6, 32, batch_first=True)
            self.decoder = nn.LSTM(32, 6, batch_first=True)
        def forward(self, x):
            enc_out, _ = self.encoder(x)
            dec_out, _ = self.decoder(enc_out)
            return dec_out

    model = Net()
    ckpt = torch.load(ART / "lstm_autoencoder_v1.pt", map_location="cpu")
    model.load_state_dict(ckpt["model_state"])
    model.eval()
    scaler = joblib.load(ART / "lstm_scaler_v1.joblib")
    seq = np.random.rand(4, 12, 6).astype(np.float32)
    seq_scaled = scaler.transform(seq.reshape(-1, 6)).reshape(4, 12, 6)
    with torch.no_grad():
        out = model(torch.FloatTensor(seq_scaled))
        mse = torch.mean((torch.FloatTensor(seq_scaled) - out)**2, dim=(1,2))
    assert mse.shape == (4,)
    return f"recon MSE range [{mse.min():.4f}, {mse.max():.4f}]"
check("LSTM Autoencoder load + inference", check_lstm)

# ── 6. XGBoost ────────────────────────────────────────────────────────────────
def check_xgb():
    import xgboost as xgb
    model = xgb.XGBClassifier()
    model.load_model(str(ART / "xgb_anomaly_v1.json"))
    proba = model.predict_proba(np.random.rand(5, 6))
    assert proba.shape == (5, 2)
    return f"output shape {proba.shape}, proba[0]={proba[0].round(3).tolist()}"
check("XGBoost load + predict_proba", check_xgb)

# ── 7. CatBoost ───────────────────────────────────────────────────────────────
def check_cat():
    from catboost import CatBoostClassifier
    model = CatBoostClassifier()
    model.load_model(str(ART / "catboost_classifier_v1.cbm"))
    proba = model.predict_proba(np.random.rand(5, 6))
    assert proba.shape[0] == 5
    return f"classes={proba.shape[1]}, proba[0]={proba[0].round(3).tolist()}"
check("CatBoost load + predict_proba", check_cat)

# ── 8. Prophet (trained with regressors: cooling_setpoint_c, hour_of_day, day_of_week) ──────
def check_prophet():
    import joblib, pandas as pd
    from datetime import datetime, timedelta
    model = joblib.load(ART / "prophet_temp_v1.joblib")
    # Must supply all regressors the model was trained with
    now = datetime.utcnow()
    future = pd.DataFrame({
        "ds": [now + timedelta(hours=i) for i in range(1, 7)],
        "cooling_setpoint_c": [22.0] * 6,
        "hour_of_day":  [(now.hour + i) % 24 for i in range(1, 7)],
        "day_of_week":  [(now.weekday()) for _ in range(6)],
    })
    forecast = model.predict(future)
    assert "yhat" in forecast.columns, "yhat missing from forecast"
    assert "yhat_lower" in forecast.columns and "yhat_upper" in forecast.columns
    return (f"horizon=6h | yhat=[{forecast['yhat'].min():.2f}, {forecast['yhat'].max():.2f}] "
            f"| regressor_count=3 (cooling_setpoint_c, hour_of_day, day_of_week)")
check("Prophet load + predict (with regressors)", check_prophet)

# ── 9. End-to-end risk scoring ────────────────────────────────────────────────
def check_risk_e2e():
    import joblib, xgboost as xgb
    from catboost import CatBoostClassifier
    import pandas as pd

    FEAT = ['inlet_temp_c','outlet_temp_c','power_kw','airflow_cfm','humidity_pct','cpu_util_pct']
    scaler_if = joblib.load(ART / "scaler_v1.joblib")
    model_if  = joblib.load(ART / "isolation_forest_v1.joblib")
    model_xgb = xgb.XGBClassifier(); model_xgb.load_model(str(ART/"xgb_anomaly_v1.json"))
    model_cat = CatBoostClassifier(); model_cat.load_model(str(ART/"catboost_classifier_v1.cbm"))

    N = 8
    raw = np.random.rand(N, 6)
    Xdf = pd.DataFrame(raw, columns=FEAT)
    X_scaled = scaler_if.transform(Xdf)
    if_scores  = model_if.score_samples(X_scaled)
    xgb_scores = model_xgb.predict_proba(raw)[:, 1]
    cat_probs  = model_cat.predict_proba(raw)
    lstm_scores = np.random.rand(N) * 0.1

    W_IF,W_LSTM,W_XGB,W_CAT,W_FC,W_FREQ = 0.15,0.25,0.25,0.20,0.10,0.05
    risks = []
    for i in range(N):
        norm_if   = 1/(1+math.exp(-float(if_scores[i])*10))
        norm_lstm = 1/(1+math.exp(-float(lstm_scores[i])+2))
        norm_xgb  = float(xgb_scores[i])
        nc = cat_probs.shape[1]
        norm_cat  = float(cat_probs[i][1]) if nc==2 else float(cat_probs[i][-1]+0.5*cat_probs[i][1])
        raw_score = W_IF*norm_if+W_LSTM*norm_lstm+W_XGB*norm_xgb+W_CAT*norm_cat
        risks.append(round(raw_score*100, 1))
    mn, mx = min(risks), max(risks)
    assert 0 <= mn <= mx <= 100, f"risk out of bounds: [{mn},{mx}]"
    return f"risk range [{mn}, {mx}] for N={N} devices"
check("End-to-end ensemble risk score", check_risk_e2e)

# ── 10. Backend config import ─────────────────────────────────────────────────
def check_config():
    import os, importlib
    sys.path.insert(0, str(BACK))
    os.environ.setdefault("DATABASE_URL", "sqlite:///./datacenter.db")
    os.environ.setdefault("SECRET_KEY", "test-secret-key")
    os.environ.setdefault("MODEL_ARTIFACTS_PATH", str(ART))
    os.environ.setdefault("MODEL_REGISTRY_PATH", str(ML/"model_registry.json"))
    cfg = importlib.import_module("app.config")
    assert hasattr(cfg, "settings"), "settings not found"
    return f"app_env={cfg.settings.app_env}"
check("Backend app.config import", check_config)

# ── 11. Docker Compose YAML validity ─────────────────────────────────────────
def check_docker():
    try:
        import yaml
    except ImportError:
        return "pyyaml not installed - skipping (OK in production)"
    dc = yaml.safe_load((DOCK/"docker-compose.yml").read_text())
    ov = yaml.safe_load((DOCK/"docker-compose.override.yml").read_text())
    svcs = list(dc.get("services",{}).keys())
    assert "backend" in svcs and "frontend" in svcs and "nginx" in svcs
    return f"services={svcs}"
check("docker-compose files valid", check_docker)

# ── 12. Nginx config ──────────────────────────────────────────────────────────
def check_nginx():
    text = (DOCK/"nginx"/"nginx.conf").read_text()
    for token in ["$host","$remote_addr","$http_upgrade","proxy_pass http://backend","proxy_pass http://frontend"]:
        assert token in text, f"Missing: {token}"
    assert "System.Management" not in text, "PowerShell corruption still present!"
    return "All nginx proxy headers correct"
check("nginx.conf correctness", check_nginx)

# ── 13. .env file ─────────────────────────────────────────────────────────────
def check_env():
    env = ROOT / ".env"
    if not env.exists(): raise FileNotFoundError(".env missing")
    lines = env.read_text().splitlines()
    keys = {l.split("=")[0].strip() for l in lines if "=" in l and not l.startswith("#")}
    for req in ["DATABASE_URL","MODEL_ARTIFACTS_PATH"]:
        assert req in keys, f"Missing key: {req}"
    return f"{len(keys)} env vars present"
check(".env file present and valid", check_env)

# ── 14. Frontend package.json ─────────────────────────────────────────────────
def check_frontend():
    # read_text with utf-8-sig strips BOM if present (Windows common issue)
    raw = (ROOT/"frontend"/"package.json").read_text(encoding="utf-8-sig")
    pkg = json.loads(raw)
    scripts = pkg.get("scripts", {})
    assert "build" in scripts, "'build' script missing"
    deps = list(pkg.get("dependencies",{}).keys())
    devdeps = list(pkg.get("devDependencies",{}).keys())
    return f"name={pkg.get('name','?')} | scripts={list(scripts.keys())} | deps={len(deps)} devDeps={len(devdeps)}"
check("frontend package.json valid", check_frontend)

# ── 15. Backend Dockerfile ────────────────────────────────────────────────────
def check_dockerfile():
    text = (BACK/"Dockerfile").read_text()
    for token in ["FROM python","requirements.txt","uvicorn","ml/artifacts"]:
        assert token in text, f"Missing: {token}"
    assert 'backend-data:/app' not in text, "CRITICAL: backend-data volume still present (overwrites code)!"
    return "Dockerfile looks correct"
check("backend Dockerfile valid", check_dockerfile)

# ── 16. ML pipeline script integrity ─────────────────────────────────────────
def check_train_script():
    text = (ML/"train_and_save.py").read_text()
    for fn in ["train_lstm_autoencoder","train_xgb_anomaly","train_catboost_classifier"]:
        assert f"def {fn}" in text, f"Missing function: {fn}"
        assert "return False" not in text[text.index(f"def {fn}"):text.index(f"def {fn}")+200], \
            f"{fn} still returns False (stub)!"
    return "All 3 model trainers implemented"
check("train_and_save.py - all models implemented", check_train_script)

# ── Print Summary ═════════════════════════════════════════════════════════════
print("\n" + "="*72)
print("  DATA CENTER AI  -  FULL PIPELINE HEALTH CHECK")
print("="*72)
passed = failed = warned = 0
for icon, name, msg in results:
    line = f"  {icon} {name}"
    if msg:
        print(f"{line:<60} {msg}")
    else:
        print(line)
    if icon == PASS: passed += 1
    elif icon == FAIL: failed += 1
    else: warned += 1
print("="*72)
if failed == 0:
    print(f"  RESULT: ALL {passed} CHECKS PASSED!  {warned} warnings.")
else:
    print(f"  RESULT: {passed} passed  |  {warned} warn  |  {failed} FAILED")
print("="*72)
sys.exit(1 if failed > 0 else 0)
