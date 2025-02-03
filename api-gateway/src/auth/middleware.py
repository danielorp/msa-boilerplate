import logging

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger()

WHITELIST_PATHS = {
    '/health': 'GET',
    '/auth/token': 'POST'
}

class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Pre-processing logic
        path = request.url.path
        method = request.method
        if path in WHITELIST_PATHS.keys() and WHITELIST_PATHS.get(path) == method:
            logger.info(f"No authentication required")
            return await call_next(request)

        response = await call_next(request)
        # Post-processing logic
        logger.info(f"Did authentication!!")
        
        return response