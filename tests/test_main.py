import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app.main import app
from app.models import ProblemReport, Ticket
from datetime import datetime
from app import firebase


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def mock_auth():
    with patch("app.main.auth.verify_id_token") as mock:
        mock.return_value = {"uid": "test_user_123"}
        yield mock


@pytest.fixture
def mock_gpt():
    with patch("app.gpt.GPT.get_instance") as mock:
        gpt_instance = MagicMock()
        gpt_instance.generate_response.return_value = "hardware problem with the wheels"
        mock.return_value = gpt_instance
        yield mock


def test_happy_path_get_root(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.template.name == "index.html"


def test_problem_report_endpoint_valid_input(client, mock_auth, mock_gpt):
    timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S")

    report = ProblemReport(
        content="El bot no responde, esta teniendo algun problema",
        heartbeat={
            "bot_id": "bot_123",
            "timestamp": timestamp,
            "location": {"lat": 19.4326, "lon": -99.1332},
            "status": "available",
            "battery_level": 80.0,
            "software_version": "1.0.0",
            "hardware_version": "2.0.0",
        },
    )

    response = client.post(
        "/v1/problem-reports",
        json=report.model_dump(),
        headers={"Authorization": "Bearer fake_token"},
    )

    assert response.status_code == 200
    ticket_dict = response.json()
    assert "ticket_id" in ticket_dict
    assert ticket_dict["bot_id"] == "bot_123"
    assert ticket_dict["status"] == "open"

    ticket_doc = firebase.get_tickets_collection().document(ticket_dict["ticket_id"]).get()
    assert ticket_doc.exists
    assert Ticket(**ticket_doc.to_dict()) == Ticket(**ticket_dict)


def test_problem_report_endpoint_invalid_input(client, mock_auth):
    invalid_report = {
        "content": "El bot no responde, esta teniendo algun problema",
        "heartbeat": {
            "bot_id": "bot_123",
            "timestamp": "2023-05-10T12:00:00",
            "location": {"lat": 91, "lon": -99.1332},
            "status": "available",
            "battery_level": 80.0,
            "software_version": "1.0.0",
            "hardware_version": "2.0.0",
        },
    }

    response = client.post(
        "/v1/problem-reports",
        json=invalid_report,
        headers={"Authorization": "Bearer fake_token"},
    )

    assert response.status_code == 400
    assert "Invalid location range" in response.json()["detail"]


def test_problem_report_endpoint_unauthorized(client):
    timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S")

    report = ProblemReport(
        content="El bot no responde",
        heartbeat={
            "bot_id": "bot_123",
            "timestamp": timestamp,
            "location": {"lat": 19.4326, "lon": -99.1332},
            "status": "available",
            "battery_level": 80.0,
            "software_version": "1.0.0",
            "hardware_version": "2.0.0",
        },
    )

    response = client.post("/v1/problem-reports", json=report.model_dump())

    assert response.status_code == 401


def test_get_ticket_exists(client):
    ticket_id = "ticket_123"
    ticket_data = {
        "ticket_id": ticket_id,
        "problem_location": "Test Location",
        "problem_type": "software",
        "summary": "Test summary",
        "bot_id": "bot_123",
        "status": "open",
        "status_changes": [],
        "assigned_agent": None,
    }
    firebase.get_tickets_collection().document(ticket_id).set(ticket_data)

    response = client.get(f"/v1/ticket/{ticket_id}")

    assert response.status_code == 200
    assert response.json()["ticket_id"] == ticket_id


def test_get_ticket_not_found(client):
    response = client.get("/v1/ticket/nonexistent_ticket")
    assert response.status_code == 404
    assert response.json()["detail"] == "Ticket not found"


def test_change_ticket_status_valid_input(client, mock_auth):
    ticket_id = "ticket_status_123"
    ticket_data = {
        "ticket_id": ticket_id,
        "problem_location": "Location",
        "problem_type": "software",
        "summary": "Summary",
        "bot_id": "bot_123",
        "status": "open",
        "status_changes": [],
        "assigned_agent": None,
    }
    firebase.get_tickets_collection().document(ticket_id).set(ticket_data)

    new_status = "closed"
    reason = "Trabajo completado"
    request_body = {"new_status": new_status, "reason": reason}

    response = client.put(
        f"/v1/ticket/{ticket_id}/status",
        json=request_body,
        headers={"Authorization": "Bearer fake_token"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == new_status

    ticket_doc = firebase.get_tickets_collection().document(ticket_id).get()
    assert ticket_doc.exists
    assert ticket_doc.to_dict()["status"] == new_status
    assert len(ticket_doc.to_dict()["status_changes"]) == 1
    assert ticket_doc.to_dict()["status_changes"][0]["status"] == new_status
    assert ticket_doc.to_dict()["status_changes"][0]["reason"] == reason


def test_change_ticket_status_unauthorized(client):
    ticket_id = "ticket_status_456"
    request_body = {"new_status": "closed", "reason": "Test reason"}

    response = client.put(f"/v1/ticket/{ticket_id}/status", json=request_body)

    assert response.status_code == 401


def test_change_ticket_status_invalid_status(client, mock_auth):
    ticket_id = "ticket_status_789"
    ticket_data = {
        "ticket_id": ticket_id,
        "problem_location": "Location",
        "problem_type": "software",
        "summary": "Summary",
        "bot_id": "bot_123",
        "status": "open",
        "status_changes": [],
        "assigned_agent": None,
    }
    firebase.get_tickets_collection().document(ticket_id).set(ticket_data)

    request_body = {"new_status": "invalid_status", "reason": "Test reason"}

    response = client.put(
        f"/v1/ticket/{ticket_id}/status",
        json=request_body,
        headers={"Authorization": "Bearer fake_token"},
    )

    assert response.status_code == 400
