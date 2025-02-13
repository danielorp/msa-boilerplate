from typing import Annotated
from fastapi import Depends, APIRouter
from fastapi.security import OAuth2PasswordRequestForm
from auth.models import User
from auth import controller

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/token")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    response = await controller.AuthController().generate_token(form_data.username, form_data.password)
    return {"access_token": response["access_token"], "token_type": response["token_type"]}

@router.get("/users/me")
async def read_users_me(
    current_user: Annotated[User, Depends(controller.get_current_active_user)],
):
    return current_user