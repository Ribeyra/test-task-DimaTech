from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import NotFound
from app.models.account import Account
from app.models.transaction import Transaction
from app.models.user import User


class UserService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_profile(self, user_id: int) -> User:
        result = await self.session.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        if not user:
            raise NotFound("User", user_id)
        return user

    async def get_accounts(self, user_id: int) -> list[Account]:
        result = await self.session.execute(
            select(Account).where(Account.user_id == user_id)
        )
        return list(result.scalars().all())

    async def get_transactions(self, user_id: int) -> list[Transaction]:
        result = await self.session.execute(
            select(Transaction).where(Transaction.user_id == user_id)
        )
        return list(result.scalars().all())
