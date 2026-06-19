import logging

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.exceptions import AppException
from app.models.user import User
from app.services.auth import AuthService

logger = logging.getLogger(__name__)

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: AsyncSession = Depends(get_session),
) -> User:
    try:
        return await AuthService(session).get_user_by_token(
            credentials.credentials
        )
    except (HTTPException, AppException):
        raise
    except Exception:
        logger.exception("Unexpected error in get_current_user")
        raise HTTPException(status_code=500, detail="Internal server error")


async def get_current_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user
