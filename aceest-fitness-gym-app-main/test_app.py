"""
Comprehensive Pytest suite for the ACEest Fitness & Gym Flask application.
Validates routes, business logic, and edge cases.
"""

import pytest
from app import (
    app,
    calculate_calories,
    calculate_bmi,
    bmi_category,
    PROGRAMS,
    clients_db,
)


# Fixtures

@pytest.fixture
def client():
    """Create a Flask test client with a fresh in-memory data store."""
    app.config["TESTING"] = True
    clients_db.clear()
    with app.test_client() as c:
        yield c
    clients_db.clear()


# Unit Tests – Pure Business Logic

class TestCalculateCalories:
    """Tests for the calculate_calories helper."""

    def test_fat_loss_3day(self):
        assert calculate_calories(80, "fat_loss_3day") == 80 * 22

    def test_muscle_gain(self):
        assert calculate_calories(70, "muscle_gain_ppl") == 70 * 35

    def test_beginner(self):
        assert calculate_calories(60, "beginner") == 60 * 26

    def test_fat_loss_5day(self):
        assert calculate_calories(90, "fat_loss_5day") == 90 * 24

    def test_returns_int(self):
        result = calculate_calories(65.5, "beginner")
        assert isinstance(result, int)

    def test_unknown_program_raises(self):
        with pytest.raises(ValueError, match="Unknown programme"):
            calculate_calories(80, "nonexistent")

    def test_zero_weight_raises(self):
        with pytest.raises(ValueError, match="Weight must be positive"):
            calculate_calories(0, "beginner")

    def test_negative_weight_raises(self):
        with pytest.raises(ValueError, match="Weight must be positive"):
            calculate_calories(-10, "beginner")


class TestCalculateBMI:
    """Tests for the calculate_bmi helper."""

    def test_normal_bmi(self):
        bmi = calculate_bmi(70, 175)
        assert 22.0 <= bmi <= 23.0

    def test_returns_float(self):
        assert isinstance(calculate_bmi(80, 180), float)

    def test_zero_height_raises(self):
        with pytest.raises(ValueError, match="Height must be positive"):
            calculate_bmi(70, 0)

    def test_negative_height_raises(self):
        with pytest.raises(ValueError, match="Height must be positive"):
            calculate_bmi(70, -170)

    def test_zero_weight_raises(self):
        with pytest.raises(ValueError, match="Weight must be positive"):
            calculate_bmi(0, 170)


class TestBMICategory:
    """Tests for bmi_category classification."""

    def test_underweight(self):
        assert bmi_category(17.0) == "Underweight"

    def test_normal(self):
        assert bmi_category(22.0) == "Normal weight"

    def test_overweight(self):
        assert bmi_category(27.5) == "Overweight"

    def test_obese(self):
        assert bmi_category(35.0) == "Obese"

    def test_boundary_18_5(self):
        assert bmi_category(18.5) == "Normal weight"

    def test_boundary_25(self):
        assert bmi_category(25.0) == "Overweight"

    def test_boundary_30(self):
        assert bmi_category(30.0) == "Obese"


class TestIndexRoute:
    """Tests for the home page."""

    def test_index_status(self, client):
        resp = client.get("/")
        assert resp.status_code == 200

    def test_index_contains_title(self, client):
        resp = client.get("/")
        assert b"ACEest" in resp.data


class TestHealthRoute:
    """Tests for /health."""

    def test_health_ok(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["status"] == "healthy"

    def test_health_app_name(self, client):
        resp = client.get("/health")
        data = resp.get_json()
        assert "ACEest" in data["app"]


class TestProgramsAPI:
    """Tests for /api/programs endpoints."""

    def test_get_all_programs(self, client):
        resp = client.get("/api/programs")
        assert resp.status_code == 200
        data = resp.get_json()
        assert "beginner" in data
        assert len(data) == len(PROGRAMS)

    def test_get_single_program(self, client):
        resp = client.get("/api/programs/beginner")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["name"] == "Beginner (BG)"

    def test_get_unknown_program_404(self, client):
        resp = client.get("/api/programs/nonexistent")
        assert resp.status_code == 404


class TestCalorieAPI:
    """Tests for /api/calculate_calories endpoint."""

    def test_valid_request(self, client):
        resp = client.post(
            "/api/calculate_calories",
            json={"weight": 80, "program_key": "fat_loss_3day"},
        )
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["calories"] == 80 * 22

    def test_missing_fields(self, client):
        resp = client.post("/api/calculate_calories", json={"weight": 80})
        assert resp.status_code == 400

    def test_no_json_body(self, client):
        resp = client.post("/api/calculate_calories")
        assert resp.status_code == 400

    def test_invalid_program(self, client):
        resp = client.post(
            "/api/calculate_calories",
            json={"weight": 80, "program_key": "xyz"},
        )
        assert resp.status_code == 400


class TestBMIAPI:
    """Tests for /api/bmi endpoint."""

    def test_valid_bmi(self, client):
        resp = client.post("/api/bmi", json={"weight": 70, "height_cm": 175})
        assert resp.status_code == 200
        data = resp.get_json()
        assert "bmi" in data
        assert "category" in data

    def test_missing_height(self, client):
        resp = client.post("/api/bmi", json={"weight": 70})
        assert resp.status_code == 400

    def test_no_json_body(self, client):
        resp = client.post("/api/bmi")
        assert resp.status_code == 400


class TestClientsAPI:
    """Tests for /api/clients CRUD endpoints."""

    def test_empty_clients_list(self, client):
        resp = client.get("/api/clients")
        assert resp.status_code == 200
        assert resp.get_json() == []

    def test_create_client(self, client):
        resp = client.post(
            "/api/clients",
            json={
                "name": "Ravi",
                "age": 28,
                "weight": 75,
                "height_cm": 178,
                "program_key": "muscle_gain_ppl",
            },
        )
        assert resp.status_code == 201
        data = resp.get_json()
        assert data["name"] == "Ravi"
        assert data["calories"] == 75 * 35

    def test_create_duplicate_client(self, client):
        client.post("/api/clients", json={"name": "Ravi", "weight": 75, "height_cm": 170})
        resp = client.post("/api/clients", json={"name": "Ravi", "weight": 80, "height_cm": 170})
        assert resp.status_code == 409

    def test_create_client_missing_name(self, client):
        resp = client.post("/api/clients", json={"age": 25})
        assert resp.status_code == 400

    def test_get_client(self, client):
        client.post(
            "/api/clients",
            json={"name": "Priya", "age": 30, "weight": 60, "height_cm": 165},
        )
        resp = client.get("/api/clients/Priya")
        assert resp.status_code == 200
        assert resp.get_json()["name"] == "Priya"

    def test_get_missing_client_404(self, client):
        resp = client.get("/api/clients/Ghost")
        assert resp.status_code == 404

    def test_delete_client(self, client):
        client.post("/api/clients", json={"name": "Arjun", "weight": 70, "height_cm": 170})
        resp = client.delete("/api/clients/Arjun")
        assert resp.status_code == 200
        # Confirm removed
        resp = client.get("/api/clients/Arjun")
        assert resp.status_code == 404

    def test_delete_missing_client(self, client):
        resp = client.delete("/api/clients/Nobody")
        assert resp.status_code == 404

    def test_clients_list_after_creation(self, client):
        client.post("/api/clients", json={"name": "A", "weight": 60, "height_cm": 160})
        client.post("/api/clients", json={"name": "B", "weight": 70, "height_cm": 170})
        resp = client.get("/api/clients")
        assert len(resp.get_json()) == 2
