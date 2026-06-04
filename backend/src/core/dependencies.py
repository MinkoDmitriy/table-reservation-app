from typing import Annotated
from fastapi import Depends, HTTPException, Request, status

from src.core.database import db_dep, get_db
from src.core.security import decode_token, FullPayload, get_token_from_request
from src.models import User

async def get_actual_user_id(request: Request) -> int:
    # Retrieve user_id set by AuthMiddleware if present
    user_id = getattr(request.state, "user_id", None)
    if user_id is not None:
        return user_id
    
    # Fallback logic if middleware was bypassed (e.g. for specific routes)
    token = get_token_from_request(request)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization header"
        )
    try:
        payload = FullPayload(**decode_token(token))
        if payload.type != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type"
            )
        return int(payload.sub)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access token is invalid or expired"
        )


def only_authenticated(user_id: Annotated[int, Depends(get_actual_user_id)]) -> bool:
    return True


async def only_admin(user_id: Annotated[int, Depends(get_actual_user_id)], session: db_dep) -> int:
    user = await session.get(User, user_id)
    if not user or not getattr(user, "is_admin", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden. This route is available only for admins."
        )
    return user_id


only_authenticated_dep = Annotated[bool, Depends(only_authenticated)]
actual_user_id_dep = Annotated[int, Depends(get_actual_user_id)]
only_admin_dep = Annotated[int, Depends(only_admin)]
