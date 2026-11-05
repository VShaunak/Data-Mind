import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_endpoint():
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert data["app"] == "Data Mind"

def test_session_crud():
    # 1. Create session
    create_res = client.post("/api/sessions", json={"title": "Test Session"})
    assert create_res.status_code == 200
    sess = create_res.json()
    sess_id = sess["id"]
    assert sess["title"] == "Test Session"

    # 2. List sessions
    list_res = client.get("/api/sessions")
    assert list_res.status_code == 200
    items = list_res.json()
    assert any(s["id"] == sess_id for s in items)

    # 3. Get session detail
    detail_res = client.get(f"/api/sessions/{sess_id}")
    assert detail_res.status_code == 200
    detail = detail_res.json()
    assert detail["session"]["id"] == sess_id

    # 4. Delete session
    del_res = client.delete(f"/api/sessions/{sess_id}")
    assert del_res.status_code == 200
    assert del_res.json()["success"] is True

def test_diagnostics_endpoint():
    res = client.get("/api/diagnostics")
    assert res.status_code == 200
    diag = res.json()
    assert "os_info" in diag
    assert "storage" in diag
    assert "docker" in diag
    assert "providers" in diag

def test_start_analysis_endpoint(tmp_path):
    # Create test CSV
    csv_file = tmp_path / "sample.csv"
    csv_file.write_text("Category,Value\nA,10\nB,20\nC,30", encoding="utf-8")

    # Create session
    sess_res = client.post("/api/sessions", json={"title": "Analysis Test"})
    assert sess_res.status_code == 200
    sess_id = sess_res.json()["id"]

    # Start analysis
    start_res = client.post("/api/analysis/start", json={
        "session_id": sess_id,
        "prompt": "Create a bar chart of Value by Category",
        "dataset_path": str(csv_file)
    })
    assert start_res.status_code == 200
    start_data = start_res.json()
    assert start_data["success"] is True
    assert "task_id" in start_data
    assert start_data["session_id"] == sess_id

