#!/usr/bin/env python3
"""
Data Center AI - API Health & Integration Test
===============================================
Runs against a running backend instance.
Usage:
  python test_api.py                     # defaults to http://localhost:8000
  python test_api.py http://backend:8000 # for Docker
  BACKEND_URL=http://localhost:8001 python test_api.py
"""

import sys
import os
import json
import time
import uuid
import urllib.request
import urllib.error

BASE_URL = os.environ.get(
    "BACKEND_URL", sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
)
API = f"{BASE_URL}/api/v1"

passed = 0
failed = 0
errors = []
UNIQUE = uuid.uuid4().hex[:8]


def _request(
    method: str, path: str, body: dict = None, headers: dict = None, timeout: int = 10
) -> tuple[int, dict | str]:
    url = BASE_URL if path == "/" else f"{API}{path}"
    data = json.dumps(body).encode() if body else None
    hdrs = {"Content-Type": "application/json"}
    if headers:
        hdrs.update(headers)
    req = urllib.request.Request(url, data=data, headers=hdrs, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode()
            try:
                return resp.status, json.loads(raw)
            except json.JSONDecodeError:
                return resp.status, raw
    except urllib.error.HTTPError as e:
        raw = e.read().decode()
        try:
            return e.code, json.loads(raw)
        except json.JSONDecodeError:
            return e.code, raw
    except Exception as e:
        return 0, str(e)


def test(name, method, path, expected_status=200, body=None, headers=None, check=None):
    global passed, failed
    status, resp = _request(method, path, body, headers)
    ok = status == expected_status
    if ok and check:
        ok = check(resp)
    if ok:
        passed += 1
        print(f"  PASS  {name}")
    else:
        failed += 1
        err = f"{name} — expected {expected_status}, got {status}"
        errors.append(err)
        print(f"  FAIL  {err}")


def run_tests():
    global passed, failed
    print(f"\n{'=' * 60}")
    print(f"  Data Center AI — API Test Suite")
    print(f"  Target: {BASE_URL}  |  Run ID: {UNIQUE}")
    print(f"{'=' * 60}\n")

    # ── Health ──────────────────────────────────────────────
    print("[Health Checks]")
    test(
        "Root endpoint",
        "GET",
        "/",
        200,
        check=lambda r: (
            isinstance(r, dict) and r.get("name") == "Data Center AI Control Room"
        ),
    )
    test(
        "Health check",
        "GET",
        "/health",
        200,
        check=lambda r: r.get("status") in ("ok", "degraded") and "database" in r,
    )

    # ── Authentication ──────────────────────────────────────
    print("\n[Authentication]")
    test(
        "Login as admin",
        "POST",
        "/auth/login",
        200,
        body={"username": "admin", "password": "admin123"},
        check=lambda r: "access_token" in r and "refresh_token" in r,
    )
    test(
        "Login bad credentials",
        "POST",
        "/auth/login",
        401,
        body={"username": "admin", "password": "wrong"},
    )

    unique_user = f"testuser_{UNIQUE}"
    test(
        "Register new user",
        "POST",
        "/auth/register",
        201,
        body={
            "username": unique_user,
            "email": f"{unique_user}@test.com",
            "password": "test123",
            "role": "operator",
        },
        check=lambda r: r.get("username") == unique_user,
    )
    test(
        "Register duplicate",
        "POST",
        "/auth/register",
        409,
        body={
            "username": "admin",
            "email": f"dup_{UNIQUE}@test.com",
            "password": "test123",
        },
    )

    _, login_resp = _request(
        "POST", "/auth/login", body={"username": "admin", "password": "admin123"}
    )
    token = login_resp.get("access_token", "") if isinstance(login_resp, dict) else ""
    auth_header = {"Authorization": f"Bearer {token}"}

    test(
        "Get current user",
        "GET",
        "/auth/me",
        200,
        headers=auth_header,
        check=lambda r: r.get("username") == "admin" and r.get("role") == "admin",
    )

    # ── Data Centers ────────────────────────────────────────
    print("\n[Data Centers]")
    test(
        "List data centers",
        "GET",
        "/datacenters",
        200,
        check=lambda r: isinstance(r, list) and len(r) >= 1,
    )
    test(
        "Data centers summary",
        "GET",
        "/datacenters/summary",
        200,
        check=lambda r: "total_datacenters" in r and "datacenters" in r,
    )

    dc_id = "dc-primary"
    test(
        "Get data center by ID",
        "GET",
        f"/datacenters/{dc_id}",
        200,
        check=lambda r: r.get("id") == dc_id,
    )

    unique_dc = f"Test DC {UNIQUE}"
    test(
        "Create data center",
        "POST",
        "/datacenters",
        201,
        body={
            "name": unique_dc,
            "location": "Test Lab",
            "region": "us-test-1",
            "tier": "tier-2",
        },
        check=lambda r: r.get("name") == unique_dc and "id" in r,
    )

    test(
        "Get data center KPIs",
        "GET",
        f"/datacenters/{dc_id}/kpis",
        200,
        check=lambda r: "device_count" in r and r.get("datacenter_id") == dc_id,
    )
    test(
        "Get data center devices",
        "GET",
        f"/datacenters/{dc_id}/devices",
        200,
        check=lambda r: isinstance(r, list) and len(r) >= 1,
    )
    test("Get non-existent data center", "GET", "/datacenters/nonexistent", 404)

    # ── Devices ─────────────────────────────────────────────
    print("\n[Devices]")
    test(
        "List all devices",
        "GET",
        "/devices",
        200,
        check=lambda r: isinstance(r, list) and len(r) >= 8,
    )
    test(
        "List devices by data center",
        "GET",
        f"/devices?datacenter_id={dc_id}",
        200,
        check=lambda r: all(d.get("datacenter_id") == dc_id for d in r),
    )
    test(
        "List devices by type",
        "GET",
        "/devices?device_type=rack",
        200,
        check=lambda r: all(d.get("type") == "rack" for d in r),
    )
    test(
        "Get device detail",
        "GET",
        "/devices/RACK-A1",
        200,
        check=lambda r: r.get("id") == "RACK-A1" and "recent_readings" in r,
    )
    test("Get non-existent device", "GET", "/devices/FAKE-999", 404)

    # ── KPIs ────────────────────────────────────────────────
    print("\n[KPIs]")
    test(
        "Get KPI snapshot",
        "GET",
        "/kpis",
        200,
        check=lambda r: "pue" in r and "total_power_kwh" in r,
    )
    test(
        "Get KPI with window",
        "GET",
        "/kpis?window=1h",
        200,
        check=lambda r: r.get("window") == "1h",
    )

    # ── Alerts ──────────────────────────────────────────────
    print("\n[Alerts]")
    test(
        "List alerts",
        "GET",
        "/alerts",
        200,
        check=lambda r: "items" in r and "total" in r,
    )

    # ── Work Orders ─────────────────────────────────────────
    print("\n[Work Orders]")
    test(
        "List work orders",
        "GET",
        "/work-orders",
        200,
        check=lambda r: isinstance(r, dict) and "items" in r,
    )

    # ── ML Registry ─────────────────────────────────────────
    print("\n[ML Registry]")
    test(
        "Get model registry",
        "GET",
        "/ml/model-registry",
        200,
        check=lambda r: isinstance(r, dict) and "models" in r and len(r["models"]) >= 1,
    )
    test(
        "List ML models",
        "GET",
        "/ml/models",
        200,
        check=lambda r: isinstance(r, dict) and "models" in r and len(r["models"]) >= 1,
    )
    test(
        "Get specific model",
        "GET",
        "/ml/models/isolation_forest_v1",
        200,
        check=lambda r: r.get("model_id") == "isolation_forest_v1",
    )
    test("Get non-existent model", "GET", "/ml/models/fake_model", 404)

    # ── Audit Log ───────────────────────────────────────────
    print("\n[Audit Log]")
    test(
        "List audit logs",
        "GET",
        "/audit-log",
        200,
        check=lambda r: isinstance(r, dict) and "items" in r,
    )

    # ── Cyber Simulation ────────────────────────────────────
    print("\n[Cyber Simulation]")
    test(
        "Get cyber scenarios",
        "GET",
        "/cyber/scenarios",
        200,
        check=lambda r: "scenarios" in r and "available_threat_types" in r,
    )
    test(
        "Get simulation state",
        "GET",
        "/cyber/simulation-state",
        200,
        check=lambda r: "running" in r,
    )
    test(
        "What-If simulation",
        "POST",
        "/simulation/what-if",
        200,
        body={
            "device_id": "RACK-A1",
            "parameter": "setpoint",
            "current_value": 24.0,
            "proposed_value": 22.0,
            "horizon_min": 60,
        },
        check=lambda r: "estimated_annual_cost_saving_usd" in r,
    )
    test(
        "Inject anomaly (demo)",
        "POST",
        "/demo/inject-anomaly?device_id=RACK-A2",
        200,
        check=lambda r: r.get("injected") is True,
    )

    # ── Summary ─────────────────────────────────────────────
    total = passed + failed
    print(f"\n{'=' * 60}")
    print(f"  Results: {passed}/{total} passed, {failed} failed")
    print(f"{'=' * 60}")
    if errors:
        print("\n  Failures:")
        for e in errors:
            print(f"    - {e}")
    print()
    return failed == 0


if __name__ == "__main__":
    print(f"Waiting for {BASE_URL} to be ready...")
    for i in range(30):
        try:
            status, _ = _request("GET", "/", timeout=5)
            if status:
                print(f"Server ready after ~{i}s\n")
                break
        except Exception:
            pass
        time.sleep(1)
    else:
        print(f"ERROR: Server at {BASE_URL} did not become ready in 30s")
        sys.exit(1)

    success = run_tests()
    sys.exit(0 if success else 1)
