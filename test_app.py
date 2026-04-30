"""
High Coverage Pytest suite for ACEest Flask App
"""

import pytest
from app import app, clients_db, PROGRAMS


# ================= FIXTURE =================

@pytest.fixture
def client():
    app.config["TESTING"] = True
    clients_db.clear()
    with app.test_client() as c:
        yield c
    clients_db.clear()


# ================= BASIC ROUTES =================

def test_index(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert b"ACEest" in resp.data


def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.get_json()["status"] == "healthy"


def test_404(client):
    resp = client.get("/random")
    assert resp.status_code == 404


# ================= PROGRAMS =================

def test_get_programs(client):
    resp = client.get("/api/programs")
    assert resp.status_code == 200
    assert "beginner" in resp.get_json()


def test_get_program_valid(client):
    resp = client.get("/api/programs/beginner")
    assert resp.status_code == 200


def test_get_program_invalid(client):
    resp = client.get("/api/programs/xyz")
    assert resp.status_code == 404


# ================= CALORIES =================

def test_calories_valid(client):
    resp = client.post("/api/calculate_calories", json={
        "weight": 80,
        "program_key": "fat_loss_3day"
    })
    assert resp.status_code == 200
    assert resp.get_json()["calories"] == 80 * 22


def test_calories_missing_json(client):
    resp = client.post("/api/calculate_calories")
    assert resp.status_code == 400


def test_calories_missing_fields(client):
    resp = client.post("/api/calculate_calories", json={"weight": 80})
    assert resp.status_code == 400


def test_calories_invalid_program(client):
    resp = client.post("/api/calculate_calories", json={
        "weight": 80,
        "program_key": "invalid"
    })
    assert resp.status_code == 400


def test_calories_invalid_type(client):
    resp = client.post("/api/calculate_calories", json={
        "weight": "abc",
        "program_key": "beginner"
    })
    assert resp.status_code == 400


def test_calories_negative_weight(client):
    resp = client.post("/api/calculate_calories", json={
        "weight": -10,
        "program_key": "beginner"
    })
    assert resp.status_code == 400


# ================= BMI =================

def test_bmi_valid(client):
    resp = client.post("/api/bmi", json={
        "weight": 70,
        "height_cm": 175
    })
    assert resp.status_code == 200
    data = resp.get_json()
    assert "bmi" in data
    assert "category" in data


def test_bmi_missing_json(client):
    resp = client.post("/api/bmi")
    assert resp.status_code == 400


def test_bmi_missing_fields(client):
    resp = client.post("/api/bmi", json={"weight": 70})
    assert resp.status_code == 400


def test_bmi_invalid_type(client):
    resp = client.post("/api/bmi", json={
        "weight": "abc",
        "height_cm": "xyz"
    })
    assert resp.status_code == 400


def test_bmi_negative(client):
    resp = client.post("/api/bmi", json={
        "weight": -70,
        "height_cm": 170
    })
    assert resp.status_code == 400


# ================= CLIENTS =================

def test_list_empty_clients(client):
    resp = client.get("/api/clients")
    assert resp.status_code == 200
    assert resp.get_json() == []


def test_create_client_basic(client):
    resp = client.post("/api/clients", json={
        "name": "Ravi",
        "weight": 75,
        "height_cm": 170
    })
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["name"] == "Ravi"


def test_create_client_full(client):
    resp = client.post("/api/clients", json={
        "name": "Priya",
        "age": 25,
        "weight": 60,
        "height_cm": 165,
        "program_key": "beginner"
    })
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["bmi"] is not None
    assert data["calories"] is not None


def test_create_client_missing_json(client):
    resp = client.post("/api/clients")
    assert resp.status_code == 400


def test_create_client_missing_name(client):
    resp = client.post("/api/clients", json={"age": 20})
    assert resp.status_code == 400


def test_create_duplicate_client(client):
    client.post("/api/clients", json={"name": "A"})
    resp = client.post("/api/clients", json={"name": "A"})
    assert resp.status_code == 409


def test_create_client_invalid_weight(client):
    resp = client.post("/api/clients", json={
        "name": "X",
        "weight": "abc",
        "height_cm": "xyz"
    })
    assert resp.status_code == 201  # handled gracefully
    data = resp.get_json()
    assert data["bmi"] is None
    assert data["calories"] is None


def test_get_client(client):
    client.post("/api/clients", json={"name": "Ravi"})
    resp = client.get("/api/clients/Ravi")
    assert resp.status_code == 200


def test_get_client_not_found(client):
    resp = client.get("/api/clients/ghost")
    assert resp.status_code == 404


def test_delete_client(client):
    client.post("/api/clients", json={"name": "A"})
    resp = client.delete("/api/clients/A")
    assert resp.status_code == 200


def test_delete_client_not_found(client):
    resp = client.delete("/api/clients/X")
    assert resp.status_code == 404


def test_delete_then_get(client):
    client.post("/api/clients", json={"name": "A"})
    client.delete("/api/clients/A")
    resp = client.get("/api/clients/A")
    assert resp.status_code == 404