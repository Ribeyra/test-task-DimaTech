import pytest

from app.exceptions import Unauthorized
from app.models.user import User
from app.services.auth import AuthService
from app.utils.security import create_jwt, hash_token


class TestAuthService:
    async def test_authenticate_success(self, session):
        token = await AuthService(session).authenticate("user@test.com", "user123")
        assert isinstance(token, str)
        assert len(token) > 0

    async def test_authenticate_wrong_password(self, session):
        with pytest.raises(Unauthorized, match="Invalid email or password"):
            await AuthService(session).authenticate("user@test.com", "wrong")

    async def test_authenticate_unknown_email(self, session):
        with pytest.raises(Unauthorized, match="Invalid email or password"):
            await AuthService(session).authenticate("noone@test.com", "user123")

    async def test_logout_clears_token_hash(self, session):
        service = AuthService(session)
        token = await service.authenticate("user@test.com", "user123")
        assert token is not None

        result = await session.execute(
            __import__("sqlalchemy").select(User).where(User.email == "user@test.com")
        )
        user = result.scalar_one()
        assert user.token_hash is not None

        await service.logout(user)
        assert user.token_hash is None

    async def test_get_user_by_token_valid(self, session):
        service = AuthService(session)
        token = await service.authenticate("user@test.com", "user123")

        user = await service.get_user_by_token(token)
        assert user.email == "user@test.com"
        assert user.is_admin is False

    async def test_get_user_by_token_revoked(self, session):
        service = AuthService(session)
        token = await service.authenticate("user@test.com", "user123")

        result = await session.execute(
            __import__("sqlalchemy").select(User).where(User.email == "user@test.com")
        )
        user = result.scalar_one()
        await service.logout(user)

        with pytest.raises(Unauthorized, match="Token has been revoked"):
            await service.get_user_by_token(token)

    async def test_get_user_by_token_invalid(self, session):
        with pytest.raises(Unauthorized, match="Invalid token"):
            await AuthService(session).get_user_by_token("garbage-token")

    async def test_get_user_by_token_expired(self, session):
        service = AuthService(session)
        token = await service.authenticate("user@test.com", "user123")
        assert token is not None

        long_token = create_jwt(999, False)
        with pytest.raises(Unauthorized, match="User not found"):
            await service.get_user_by_token(long_token)
