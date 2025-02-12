from unittest.mock import Mock, patch
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
def load_jwks_response_200():
    """
    Response to -> await client.get(self.jwks_url)
    in          -> KeycloakClient:get_jwks_key

    """
    with open(
        "src/tests/resources/response_200_get_jwks.json", "r", encoding="utf-8"
    ) as file:
        yield json.load(file)


@fixture
def mock_jwks_response_200(load_jwks_response_200):
    respx.get(keycloak_client.KeycloakClient().jwks_url).respond(
        json=load_jwks_response_200, status_code=HTTPStatus.OK
    )
    yield


@fixture
def load_token_response_200():
    """
    Response to -> await client.post(self.token_url, data=payload, headers=headers)
    in          -> KeycloakClient:generate_token

    """
    with open(
        "src/tests/resources/response_200_get_token.json", "r", encoding="utf-8"
    ) as file:
        yield json.load(file)


@fixture
def mock_token_response(load_token_response_200):
    respx.post(keycloak_client.KeycloakClient().token_url).respond(
        json=load_token_response_200, status_code=HTTPStatus.OK
    )
    yield


@fixture
def jwt_decode_response_success():
    """
    Response to -> jose.jwt.decode()
    """
    with patch("jose.jwt.decode", Mock()) as decode_mock:
        with open(
            "src/tests/resources/response_success_jwt_success.json",
            "r",
            encoding="utf-8",
        ) as file:
            decode_mock.return_value = json.load(file)
        yield decode_mock


class TestAuthController:

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_public_keys(self, mock_jwks_response_200):
        with open("src/tests/resources/jwks_key.txt", "r") as key_file:
            expected_public_key = key_file.read().encode()
        controller = AuthController()
        public_key = await controller.get_public_key()
        assert public_key == expected_public_key

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_token(self, mock_token_response, load_token_response_200):
        controller = AuthController()
        token = await controller.generate_token(
            username="dummy-username", password="dummy-password"
        )
        assert token == load_token_response_200


class TestRoutes:
    def test_get_health(self, mock_app):
        response = mock_app.get("/health")
        assert response.status_code == HTTPStatus.OK

    @respx.mock
    def test_generate_token_success(self, mock_app, load_token_response_200):
        response = mock_app.post(
            "/auth/token", data={"username": "danielorp", "password": "orp9613"}
        )
        assert response.json()["access_token"] == load_token_response_200["access_token"]

    @respx.mock
    def test_get_user(
        self, mock_app, load_token_response_200, mock_jwks_response_200, jwt_decode_response_success
    ):
        expected_output = {
            "username": "danielorp",
            "email": None,
            "full_name": None,
            "disabled": False,
        }
        response = mock_app.get(
            "/auth/users/me",
            headers={"Authorization": f"Bearer {load_token_response_200['access_token']}"},
        )
        assert response.json() == expected_output
