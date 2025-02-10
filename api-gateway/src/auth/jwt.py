import base64
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from auth.models import KeycloakToken
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from auth.keycloak_client import KeycloakClient

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

cached_public_key = None

def get_public_key(keycloak_client: KeycloakClient = Depends()):
    """
    Fetch the public key from Keycloak JWKS.
    """
    global cached_public_key
    if cached_public_key:
        return cached_public_key

    key_data = keycloak_client.get_jwks_key()
    n = int.from_bytes(base64.urlsafe_b64decode(key_data["n"] + "=="), "big")
    e = int.from_bytes(base64.urlsafe_b64decode(key_data["e"] + "=="), "big")
    public_numbers = rsa.RSAPublicNumbers(e, n)
    public_key = public_numbers.public_key(default_backend())
    cached_public_key = public_key.public_bytes(
        serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo
    )
    return cached_public_key

def verify_token(
    token: str = Depends(oauth2_scheme),
    keycloak_client: KeycloakClient = Depends()
):
    try:
        public_key = get_public_key(keycloak_client)
        payload = jwt.decode(
            token, public_key, algorithms=["RS256"], audience=keycloak_client.client_id
        )
        return KeycloakToken(**payload)
    except JWTError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {e}")
