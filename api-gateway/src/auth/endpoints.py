from fastapi import WebSocket, status, Depends, APIRouter
from src.auth.jwt import verify_token

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/token")
async def generate_token(username, password):
    return


# @router.websocket("/ws")
# async def websocket_endpoint(websocket: WebSocket):
#     await websocket.accept()
#     while True:
#         data = await websocket.receive_text()
#         await websocket.send_text(f"Message text was: {data}")
