import requests
import base64
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from jose.exceptions import JWTError
from constants import KEYCLOAK_SERVER_URL, REALM_NAME, CLIENT_ID

from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Cache for the public key
cached_public_key = None

def get_public_key():
    global cached_public_key
    if cached_public_key:
        return cached_public_key

    # Fetch JWKS
    jwks_url = f"{KEYCLOAK_SERVER_URL}/realms/{REALM_NAME}/protocol/openid-connect/certs"
    jwks_response = requests.get(jwks_url)
    jwks_response.raise_for_status()  # Raise an error if the request fails

    jwks = jwks_response.json()
    key_data = jwks["keys"][1]  # Assuming the first key is the correct one

    # Construct the public key
    n = int.from_bytes(base64.urlsafe_b64decode(key_data["n"] + "=="), "big")
    e = int.from_bytes(base64.urlsafe_b64decode(key_data["e"] + "=="), "big")
    public_numbers = rsa.RSAPublicNumbers(e, n)
    public_key = public_numbers.public_key(default_backend())
    cached_public_key = public_key.public_bytes(
        serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo
    )
    return cached_public_key

def verify_token(token: str = Depends(oauth2_scheme)):
    try:
        # Fetch the public key from Keycloak (cached or dynamically)
        # Replace with logic to fetch and cache Keycloak's public key
        public_key = get_public_key()

        # Decode and validate the token
        payload = jwt.decode(
            token, public_key, algorithms=["RS256"], audience=CLIENT_ID
        )
        return payload  # You can return roles or user info from the token
    except JWTError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {e}")
