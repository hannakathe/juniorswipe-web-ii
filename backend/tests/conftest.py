import os
import sys

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

os.environ["FLASK_CONFIG"] = "test"

from app import create_app  # noqa: E402
from app.extensions import db as _db  # noqa: E402
from app.seed import seed as _seed  # noqa: E402


@pytest.fixture()
def app():
    app = create_app("test")
    with app.app_context():
        _db.create_all()
        _seed(app)
    yield app
    with app.app_context():
        _db.session.remove()
        _db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


def _register(client, email, password="Password123!", role="developer", name="Test User"):
    return client.post("/api/auth/register", json={
        "email": email, "password": password, "role": role, "full_name": name,
    })


@pytest.fixture()
def dev_token(client):
    r = client.post("/api/auth/login",
                    json={"email": "dev@local.test", "password": "Password123!"})
    return r.get_json()["token"]


@pytest.fixture()
def company_token(client):
    r = client.post("/api/auth/login",
                    json={"email": "company@local.test", "password": "Password123!"})
    return r.get_json()["token"]


@pytest.fixture()
def auth(dev_token):
    return {"Authorization": f"Bearer {dev_token}"}


@pytest.fixture()
def register():
    return _register
