import httpx
from fastapi import HTTPException
from constants import KEYCLOAK_SERVER_URL, REALM_NAME, CLIENT_ID, CLIENT_SECRET

class KeycloakClient:
    def __init__(self):
        self.server_url = KEYCLOAK_SERVER_URL
        self.realm_name = REALM_NAME
        self.client_id = CLIENT_ID
        self.client_secret = CLIENT_SECRET
        self.jwks_url = f"{self.server_url}/realms/{self.realm_name}/protocol/openid-connect/certs"
        self.token_url = f"{self.server_url}/realms/{self.realm_name}/protocol/openid-connect/token"

    async def get_jwks_key(self) -> dict:
        """
        Asynchronously fetch the JSON Web Key Set (JWKS) from Keycloak.
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(self.jwks_url)
            response.raise_for_status()
            jwks = response.json()
            return jwks["keys"][1]  # Assuming the second key is the correct one

    async def generate_token(self, username: str, password: str) -> dict:
        """
        Asynchronously generate an access token from Keycloak using username and password.
        """
        payload = {
            "client_id": self.client_id,
            "grant_type": "password",
            "username": username,
            "password": password,
        }
        if self.client_secret:
            payload["client_secret"] = self.client_secret

        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(self.token_url, data=payload, headers=headers)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Failed to obtain token: {response.text}"
                )
