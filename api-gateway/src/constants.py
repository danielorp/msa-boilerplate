from decouple import config
import sys

if "pytest" in sys.modules:
    KEYCLOAK_SERVER_URL = config("KEYCLOAK_SERVER_URL", default="http://localhost:8080")
else:
    KEYCLOAK_SERVER_URL = config("KEYCLOAK_SERVER_URL", default="http://localhost:8080")
    #KEYCLOAK_SERVER_URL = config("KEYCLOAK_SERVER_URL", default="http://keycloak.msa-services.svc.cluster.local")
REALM_NAME = config("REALM_NAME", default="msa-realm")
CLIENT_ID = config("CLIENT_ID", default="msa-app")
CLIENT_SECRET = config("CLIENT_SECRET", default="y9F9laHCLzY9rMKVVEu0U52Gh2Ev3d1j")