from typing import Union, Optional, List

from pydantic import BaseModel, Field


class User(BaseModel):
    username: str
    email: Union[str, None] = None
    full_name: Union[str, None] = None
    disabled: Union[bool, None] = None


class RealmAccess(BaseModel):
    roles: List[str]


class ResourceRoles(BaseModel):
    roles: List[str]


class ResourceAccess(BaseModel):
    account: Optional[ResourceRoles]


class KeycloakToken(BaseModel):
    acr: str
    allowed_origins: List[str] = Field(alias="allowed-origins")
    aud: List[str]
    azp: str
    email_verified: bool
    exp: int
    iat: int
    iss: str
    jti: str
    preferred_username: str
    realm_access: RealmAccess
    resource_access: ResourceAccess
    scope: str
    sid: str
    sub: str
    typ: str

    def to_user(self) -> "User":
        return User(
            username=self.preferred_username,
            email=None,
            full_name=None,
            disabled=False,
        )