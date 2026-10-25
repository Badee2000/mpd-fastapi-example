import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from main import app  # noqa: E402


@pytest.fixture
def client():
    return TestClient(app, raise_server_exceptions=False)


def test_index(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_health(client):
    assert client.get("/health").json() == {"status": "healthy"}


def test_docs_are_not_exposed(client):
    assert client.get("/docs").status_code == 404
    assert client.get("/openapi.json").status_code == 404


def test_unhandled_error_is_generic(client):
    @app.get("/boom")
    def boom():
        raise ValueError("secret internal detail")

    response = client.get("/boom")
    assert response.status_code == 500
    assert response.json() == {"error": "internal server error"}
    assert "secret internal detail" not in response.text
