from sqlalchemy import select

from app.models.account import Account
from app.models.user import User
from app.services.user import UserService


class TestUserService:
    async def test_get_profile(self, session):
        result = await session.execute(
            select(User).where(User.email == "user@test.com")
        )
        user_id = result.scalar_one().id

        profile = await UserService(session).get_profile(user_id)
        assert profile.email == "user@test.com"
        assert profile.full_name == "Test User"
        assert profile.is_admin is False

    async def test_get_accounts(self, session):
        result = await session.execute(
            select(User).where(User.email == "user@test.com")
        )
        user_id = result.scalar_one().id

        accounts = await UserService(session).get_accounts(user_id)
        assert len(accounts) >= 1
        assert isinstance(accounts[0], Account)
        assert accounts[0].user_id == user_id

    async def test_get_transactions_empty(self, session):
        result = await session.execute(
            select(User).where(User.email == "user@test.com")
        )
        user_id = result.scalar_one().id

        transactions = await UserService(session).get_transactions(user_id)
        assert transactions == []
