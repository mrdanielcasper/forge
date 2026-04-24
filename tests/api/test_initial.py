from fastapi.testclient import TestClient

from orchestrator import check_human_pause, extract_routing_queue
from src.api.main import app


def test_routing_queue_extraction():
    """Ensure the orchestrator correctly parses the routing array."""
    response = "Here is my analysis. ROUTING: [Design -> Engineering (Build)]"
    queue = extract_routing_queue(response)
    assert queue == ["Design", "Engineering (Build)"]


def test_routing_terminal_state():
    """Ensure the orchestrator recognizes a terminal experiment state."""
    response = "The hypothesis is invalid. ROUTING: [Experiment Only]"
    queue = extract_routing_queue(response)
    assert queue == []


def test_human_pause_detection():
    """Ensure the orchestrator catches critical architectural shifts."""
    response = "This requires a database change. ADR_STATE: [Pending Human]"
    assert check_human_pause(response) is True


def test_human_pause_safe():
    """Ensure the orchestrator doesn't pause on safe outputs."""
    response = "The design looks good. REVERSIBILITY: [2-Way] ADR_STATE: [None]"
    assert check_human_pause(response) is False


client = TestClient(app)


def test_health_endpoint():
    """Ensure the FastAPI scaffold boots and responds to health checks."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "message": "API is online"}
