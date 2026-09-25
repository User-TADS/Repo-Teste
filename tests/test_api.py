import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app


@pytest.fixture
def client():
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    Base.metadata.create_all(bind=engine)

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
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


def test_profile_endpoints_and_validation(client):
    created = client.post(
        "/api/profiles",
        json={"name": "Ada Lovelace", "bio": "Backend developer", "github_url": "https://github.com/ada"},
    )
    assert created.status_code == 201
    profile = created.json()
    assert profile["name"] == "Ada Lovelace"
    assert profile["projects"] == []

    fetched = client.get(f"/api/profiles/{profile['id']}")
    assert fetched.status_code == 200
    assert fetched.json()["id"] == profile["id"]
    assert client.get("/api/profiles/9999").status_code == 404
    assert client.post("/api/profiles", json={"name": " "}).status_code == 422
    assert client.post("/api/profiles", json={"name": "Ada", "github_url": "not-a-url"}).status_code == 422


def test_technology_endpoints_and_validation(client):
    created = client.post(
        "/api/technologies",
        json={"name": "Python", "description": "Linguagem de programação"},
    )
    assert created.status_code == 201
    technology = created.json()
    assert technology["name"] == "Python"

    listed = client.get("/api/technologies")
    assert listed.status_code == 200
    assert any(item["id"] == technology["id"] for item in listed.json())
    assert client.post("/api/technologies", json={"name": ""}).status_code == 422
    assert client.post("/api/technologies", json={"name": "Python"}).status_code == 409


def test_project_endpoints_and_validation(client):
    profile_id = client.post("/api/profiles", json={"name": "Grace Hopper"}).json()["id"]
    technology_id = client.post("/api/technologies", json={"name": "FastAPI"}).json()["id"]

    created = client.post(
        "/api/projects",
        json={
            "title": "DevShowcase",
            "description": "Portfólio de projetos",
            "repository_url": "https://github.com/example/devshowcase",
            "demo_url": "https://example.com/demo",
            "profile_id": profile_id,
            "technology_ids": [technology_id],
        },
    )
    assert created.status_code == 201
    project = created.json()
    assert project["title"] == "DevShowcase"
    assert pro