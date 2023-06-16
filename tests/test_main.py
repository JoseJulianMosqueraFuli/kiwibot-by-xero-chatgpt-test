import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models import ProblemReport, Ticket
from datetime import datetime
from app import firebase


@pytest.fixture
def client():
    return TestClient(app)


def test_happy_path_get_root(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.template.name == "index.html"


def test_problem_report_endpoint_valid_input(client):
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

    response = client.post("/problem-report", json=report.dict())

    assert response.status_code == 200
    ticket_dict = response.json()
    assert "ticket_id" in ticket_dict
    assert "México" in ticket_dict["problem_location"]
    assert "problema" in ticket_dict["summary"]
    assert ticket_dict["bot_id"] == "bot_123"
    assert ticket_dict["status"] == "open"

    ticket_doc = firebase.tickets_collection.document(ticket_dict["ticket_id"]).get()
    assert ticket_doc.exists
    assert Ticket(**ticket_doc.to_dict()) == Ticket(**ticket_dict)


def test_problem_report_endpoint_invalid_input(client):
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

    response = client.post("/problem-report", json=invalid_report)

    assert response.status_code == 400
    assert "Invalid location range" in response.json()["detail"]


def test_get_ticket_exists(client):
    ticket_id = "ticket_123"
    ticket_data = {"id": ticket_id, "title": "Ticket de ejemplo"}
    firebase.tickets_collection.document(ticket_id).set(ticket_data)

    response = client.get(f"/ticket/{ticket_id}")

    assert response.status_code == 200
    assert response.json() == ticket_data


def test_get_ticket_not_found(client):
    response = client.get("/ticket/nonexistent_ticket")
    assert response.status_code == 404
    assert response.json()["detail"] == "Ticket not found"


def test_change_ticket_status_valid_input(client):
    ticket_id = "ticket_123"
    ticket_data = {
        "ticket_id": ticket_id,
        "problem_location": "Location",
        "problem_type": "software",
        "summary": "Summary",
        "bot_id": "bot_123",
        "status": "open",
    }
    firebase.tickets_collection.document(ticket_id).set(ticket_data)

    new_status = "closed"
    reason = "Trabajo completado"
    request_body = {"new_status": new_status, "reason": reason}

    response = client.put(f"/ticket/{ticket_id}/status", json=request_body)

    assert response.status_code == 200
    assert response.json()["status"] == new_status

    ticket_doc = firebase.tickets_collection.document(ticket_id).get()
    assert ticket_doc.exists
    assert ticket_doc.to_dict()["status"] == new_status
    assert len(ticket_doc.to_dict()["status_changes"]) == 1
    assert ticket_doc.to_dict()["status_changes"][0]["status"] == new_status
    assert ticket_doc.to_dict()["status_changes"][0]["reason"] == reason
