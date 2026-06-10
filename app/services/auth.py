from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import Unauthorized
from app.models.user import User
from app.utils.security import (
    create_jwt, decode_jwt, hash_token, verify_password
)


class AuthService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def authenticate(self, email: str, password: str) -> str:
        result = await self.session.execute(
            select(User).where(User.email == email)
        )
        user = result.scalar_one_or_none()

        if not user or not verify_password(password, user.password_hash):
            raise Unauthorized("Invalid email or password")

        token = create_jwt(user.id, user.is_admin)
        user.token_hash = hash_token(token)
        await self.session.flush()

        return token

    async def logout(self, user: User) -> None:
        user.token_hash = None
        await self.session.flush()

    async def get_user_by_token(self, token: str) -> User:
        payload = decode_jwt(token)
        if payload is None:
            raise Unauthorized("Invalid token")

        user_id = payload.get("user_id")
        if user_id is None:
            raise Unauthorized("Invalid token payload")

        result = await self.session.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        if user is None:
            raise Unauthorized("User not found")

        if user.token_hash is None or user.token_hash != hash_token(token):
            raise Unauthorized("Token has been revoked")

        return user
