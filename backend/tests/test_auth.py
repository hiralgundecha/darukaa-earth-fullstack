import pytest

from app import create_app
from app.config import Config
from app.models import db


class TestConfig(Config):
    SQLALCHEMY_DATABASE_URI = "postgresql://darukaa:darukaa@localhost:5432/darukaa_test"
    TESTING = True


@pytest.fixture
def client():
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.session.remove()
        db.drop_all()


def test_register_then_login(client):
    payload = {"email": "a@b.com", "password": "password123", "full_name": "Test User"}
    res = client.post("/api/auth/register", json=payload)
    assert res.status_code == 201
    assert "access_token" in res.get_json()

    res = client.post("/api/auth/login", json={"email": "a@b.com", "password": "password123"})
    assert res.status_code == 200


def test_short_password_is_rejected(client):
    res = client.post(
        "/api/auth/register",
        json={"email": "c@d.com", "password": "short", "full_name": "Test"},
    )
    assert res.status_code == 400


def test_projects_require_a_token(client):
    assert client.get("/api/projects").status_code == 401
