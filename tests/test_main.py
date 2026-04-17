from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_home():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello CI/CD"}


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_greet():
    response = client.get("/greet/Michael")
    assert response.status_code == 200
    assert response.json() == {"greeting": "Hello, Michael!"}


def test_unknown_route():
    response = client.get("/does-not-exist")
    assert response.status_code == 404
