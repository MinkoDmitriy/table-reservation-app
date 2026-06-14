from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from src.core.security import decode_token, FullPayload, get_token_from_request


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Soft middleware: initialize defaults for all requests
        request.state.user_id = None
        request.state.scopes = []

        token = get_token_from_request(request)
        if token:
            try:
                payload = FullPayload(**decode_token(token))
                if payload.type == "access":
                    request.state.user_id = int(payload.sub)
                    request.state.scopes = payload.scopes or []
            except Exception:
                # Soft middleware does not raise 401/403 for public routes.
                # Security dependencies will enforce authentication where required.
                pass

        response = await call_next(request)
        return response
