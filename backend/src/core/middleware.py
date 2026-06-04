from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from jwt import ExpiredSignatureError, InvalidTokenError

from src.core.security import decode_token, FullPayload, get_token_from_request


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        exceptional_prefixes = ("/docs", "/openapi.json", "/redoc", "/login", "/register", "/refresh")
        path = request.url.path
        
        # Strip roots to extract endpoint path
        for root in ("/api/auth", "/api/planner", "/api/admin"):
            if path.startswith(root):
                path = path[len(root):]
                break

        if any(path.startswith(p) for p in exceptional_prefixes):
            return await call_next(request)
        else:
            token = get_token_from_request(request)
            if not token:
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={"detail": "Missing Authorization header"}
                )

            try:
                payload = FullPayload(**decode_token(token))
                if payload.type != "access":
                    return JSONResponse(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        content={"detail": "Invalid token type"}
                    )
            except ExpiredSignatureError:
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={"detail": "Access token has expired"}
                )
            except InvalidTokenError:
                 return JSONResponse(
                     status_code=status.HTTP_401_UNAUTHORIZED,
                     content={"detail": "Access token is invalid"}
                 )
                 
            request.state.user_id = int(payload.sub)
            response = await call_next(request)
            return response
