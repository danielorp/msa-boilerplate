import respx
import json
import pytest

from http import HTTPStatus

from fastapi.testclient import TestClient
from pytest import fixture

from src.app import app
from src.auth import keycloak_client
from src.auth.controller import AuthController

pytest_plugins = ("pytest_asyncio",)


@fixture
def mock_app():
    test_client = TestClient(app=app)
    app.user_middleware.clear()
    app.middleware_stack = app.build_middleware_stack()
    yield test_client


@fixture
def load_jwks_response():
    with open(
        "src/tests/resources/get_jwks_response.json", "r", encoding="utf-8"
    ) as file:
        yield json.load(file)


@fixture
def mock_jwks_response(load_jwks_response):
    respx.get(keycloak_client.KeycloakClient().jwks_url).respond(
        json=load_jwks_response, status_code=HTTPStatus.OK
    )
    yield


@fixture
def load_token_response():
    with open(
        "src/tests/resources/get_token_response.json", "r", encoding="utf-8"
    ) as file:
        yield json.load(file)


@fixture
def mock_token_response(load_token_response):
    respx.post(keycloak_client.KeycloakClient().token_url).respond(
        json=load_token_response, status_code=HTTPStatus.OK
    )
    yield


class TestAuthController:

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_public_keys(self, mock_jwks_response):
        with open("src/tests/resources/jwks_key.txt", "r") as key_file:
            expected_public_key = key_file.read().encode()
        controller = AuthController()
        public_key = await controller.get_public_key()
        assert public_key == expected_public_key

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_token(self, mock_token_response, load_token_response):
        controller = AuthController()
        token = await controller.generate_token(
            username="dummy-username", password="dummy-password"
        )
        assert token == load_token_response


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
