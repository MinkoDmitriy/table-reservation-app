from typing import Annotated
from fastapi import Depends, HTTPException, Request, status, Security
from fastapi.security import SecurityScopes

from src.core.database import db_dep, get_db


async def get_actual_user_id(request: Request) -> int:
    user_id = getattr(request.state, "user_id", None)
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Не авторизован"
        )
    return user_id


async def check_permissions(security_scopes: SecurityScopes, request: Request) -> None:
    user_id = getattr(request.state, "user_id", None)
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Не авторизован"
        )
    
    user_scopes = getattr(request.state, "scopes", [])
    
    # System administrator wildcard check
    if "admin:all" in user_scopes:
        return
        
    for scope in security_scopes.scopes:
        if scope not in user_scopes:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Недостаточно прав. Требуется разрешение: {scope}"
            )


# Simplified helper dependency for checking a specific scope in routes
def requires(scope: str) -> Security:
    """Convenience helper to enforce a scope on a route.
    Usage: dependencies=[requires("tables:write")]
    """
    return Security(check_permissions, scopes=[scope])


# Type aliases for clean dependency injection and backwards-compatibility
actual_user_id_dep = Annotated[int, Depends(get_actual_user_id)]
only_authenticated_dep = Annotated[None, Security(check_permissions)]
only_admin_dep = Annotated[None, Security(check_permissions, scopes=["admin:all"])]
