"""API tests. Skipped automatically where fastapi/httpx are not installed."""
import pytest

pytest.importorskip("fastapi")
pytest.importorskip("httpx")
from fastapi.testclient import TestClient  # noqa: E402

from cardioscreen.api import app  # noqa: E402
from tests.test_core import HEALTHY, SICK  # noqa: E402


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


def test_health_and_index(client):
    assert client.get("/health").json()["model_loaded"] is True
    assert "Heart" in client.get("/").text


def test_predict_ok(client):
    r = client.post("/predict", json=SICK)
    assert r.status_code == 200 and r.json()["prediction"] == 1


def test_predict_validation_422(client):
    assert client.post("/predict", json={**HEALTHY, "age": -5}).status_code == 422
    assert client.post("/predict", json={}).status_code == 422


def test_batch(client):
    r = client.post("/predict/batch", json={"patients": [HEALTHY, SICK]})
    assert r.json()["count"] == 2
    assert client.post("/predict/batch", json={"patients": []}).status_code == 422
