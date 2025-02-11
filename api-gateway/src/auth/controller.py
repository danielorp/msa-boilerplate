import base64

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from auth.models import User
from auth.keycloak_client import KeycloakClient
from auth.models import KeycloakToken
from jose import jwt, JWTError
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

cached_public_key = None


class AuthController:
    def __init__(self, keycloak_client = None):
        self.keycloak_client = keycloak_client or KeycloakClient()

    async def get_current_user(self, token: Annotated[str, Depends(oauth2_scheme)]):
        verified_token = await self.verify_token(token, self.keycloak_client)
        user = verified_token.to_user()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user

    async def get_current_active_user(
        self,
        current_user: Annotated[User, Depends(get_current_user)],
    ):
        if current_user.disabled:
            raise HTTPException(status_code=400, detail="Inactive user")
        return current_user

    async def generate_token(self, username: str, password: str):
        return await self.keycloak_client.generate_token(username, password)

    async def get_public_key(self):
        """
        Fetch the public key from Keycloak JWKS.
        """
        global cached_public_key
        if cached_public_key:
            return cached_public_key

        key_data = await self.keycloak_client.get_jwks_key()
        n = int.from_bytes(base64.urlsafe_b64decode(key_data["n"] + "=="), "big")
        e = int.from_bytes(base64.urlsafe_b64decode(key_data["e"] + "=="), "big")
        public_numbers = rsa.RSAPublicNumbers(e, n)
        public_key = public_numbers.public_key(default_backend())
        cached_public_key = public_key.public_bytes(
            serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo
        )
        return cached_public_key

    async def verify_token(self, token: str):
        try:
            public_key = await self.get_public_key()
            payload = jwt.decode(
                token,
                public_key,
                algorithms=["RS256"],
                audience=self.keycloak_client.client_id,
            )
            return KeycloakToken(**payload)
        except JWTError as e:
            raise HTTPException(status_code=401, detail=f"Invalid token: {e}")
