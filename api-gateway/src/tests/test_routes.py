from http import HTTPStatus

from fastapi.testclient import TestClient
from pytest import fixture

from src.app import app


@fixture
def mock_app():
    yield TestClient(app=app)


def test_get_health(mock_app):
    response = mock_app.get("/health")
    assert response.status_code == HTTPStatus.OK


def test_generate_token_success(mock_app):
    response = mock_app.post(
        "/auth/token", data={"username": "", "password": ""}
    )
