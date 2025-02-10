import responses
import json

from http import HTTPStatus
from unittest.mock import Mock

from fastapi.testclient import TestClient
from pytest import fixture

from src.app import app
from src.auth import jwt, keycloak_client


@fixture
def mock_app():
    test_client = TestClient(app=app)
    app.user_middleware.clear()
    app.middleware_stack = app.build_middleware_stack()
    yield test_client


@fixture
def load_jwks_response():
    with open("src/tests/resources/get_jwks_response.json", "r", encoding="utf-8") as file:
        yield json.load(file)


@fixture
def mock_jwks_response(load_jwks_response):
    responses.add(
        responses.GET,
        keycloak_client.KeycloakClient().jwks_url,
        json=load_jwks_response,
        status=200,
    )
    yield


class TestJWT:
    @responses.activate
    def test_get_public_keys(self, mock_jwks_response):
        public_key = jwt.get_public_key(keycloak_client.KeycloakClient())


class TestRoutes:
    def test_get_health(self, mock_app):
        response = mock_app.get("/health")
        assert response.status_code == HTTPStatus.OK

    def test_generate_token_success(self, mock_app):
        response = mock_app.post(
            "/auth/token", data={"username": "danielorp", "password": "orp9613"}
        )
        assert "access_token" in response.json()

    def test_get_user(self, mock_app):
        response = mock_app.post(
            "/auth/token",
            data={"username": "", "password": ""},
        )
        assert response.status_code == 200
        access_token = response.json()["access_token"]

        response = mock_app.get(
            "/auth/users/me", headers={"Authorization": f"Bearer {access_token}"}
        )
        assert response.status_code == 200
        assert "username" in response.json()
