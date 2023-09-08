from fastapi.testclient import TestClient

from app import X_TOKEN
from app.main import app

client = TestClient(app)


def test_root():
    response = client.get("/", headers={"x-token": X_TOKEN})
    assert response.status_code == 200
    assert response.json()["title"] == app.title
    assert response.json()["description"] == app.description
    assert response.json()["version"] == app.version
    assert response.json()["docs_url"] == app.docs_url


def test_health():
    response = client.get("/health", headers={"x-token": X_TOKEN})
    assert response.status_code == 200
