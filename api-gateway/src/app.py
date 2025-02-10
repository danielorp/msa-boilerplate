from fastapi import FastAPI, status
from auth import endpoints as auth_endpoints, middleware as auth_middleware

app = FastAPI()


@app.get("/health", status_code=status.HTTP_200_OK)
async def health_probes():
    return

app.include_router(auth_endpoints.router)
app.add_middleware(auth_middleware.AuthMiddleware)
