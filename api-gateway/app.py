# File: app.py
from fastapi import FastAPI, WebSocket, status

app = FastAPI()

@app.get("/health", status_code=status.HTTP_200_OK)
async def health_probes():
    return

@app.get("/api")
async def read_root():
    return {"message": "Hello from REST API!"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Message text was: {data}")
