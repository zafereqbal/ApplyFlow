import os
os.environ["DATABASE_URL"] = "sqlite:///./test_applyflow.db"
os.environ["SECRET_KEY"] = "test-secret-key-that-is-long-enough"
os.environ["REDIS_URL"] = "redis://localhost:6399/0"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.database import Base, get_db
from app.main import app

test_engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(bind=test_engine, autoflush=False, autocommit=False)


@pytest.fixture()
def client():
    Base.metadata.create_all(bind=test_engine)
    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=test_engine)


def register_and_login(client, email="test@example.com"):
    response = client.post("/api/auth/register", json={"email": email, "password": "correct-horse-battery"})
    assert response.status_code == 201
    response = client.post("/api/auth/login", data={"username": email, "password": "correct-horse-battery"})
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def test_register_login_and_protected_route(client):
    headers = register_and_login(client)
    assert client.get("/api/auth/me", headers=headers).json()["email"] == "test@example.com"


def test_user_cannot_access_another_users_application(client):
    first = register_and_login(client, "first@example.com")
    second = register_and_login(client, "second@example.com")
    created = client.post("/api/applications", headers=first, json={
        "company": "Acme", "role": "Backend Engineer", "status": "applied"
    })
    assert created.status_code == 201
    app_id = created.json()["id"]
    assert client.get(f"/api/applications/{app_id}", headers=second).status_code == 404


def test_create_list_and_update_application(client):
    headers = register_and_login(client)
    created = client.post("/api/applications", headers=headers, json={
        "company": "Acme", "role": "Python Developer", "status": "saved"
    })
    assert created.status_code == 201
    app_id = created.json()["id"]
    updated = client.patch(f"/api/applications/{app_id}", headers=headers, json={"status": "interview"})
    assert updated.status_code == 200
    listing = client.get("/api/applications?status=interview&page=1&page_size=10", headers=headers)
    assert listing.status_code == 200
    assert listing.json()["total"] == 1


def test_health_endpoint(client):
    assert client.get("/health").json()["status"] == "ok"
