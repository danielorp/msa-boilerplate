from decouple import config

KEYCLOAK_SERVER_URL = config("KEYCLOAK_SERVER_URL", default="http://msa-services-keycloak.msa-services.svc.cluster.local")
REALM_NAME = config("REALM_NAME", default="tms-realm")
CLIENT_ID = config("CLIENT_ID", default="fastapi-app")
CLIENT_SECRET = config("CLIENT_SECRET", default="q42ynHIOrQZYxSHysRXIxCzWkmD5P3i9")