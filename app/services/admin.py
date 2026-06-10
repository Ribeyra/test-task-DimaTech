from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import Conflict, NotFound
from app.models.account import Account
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.utils.security import hash_password


class AdminService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def list_users(self) -> list[User]:
        result = await self.session.execute(select(User))
        return list(result.scalars().all())

    async def create_user(self, data: UserCreate) -> User:
        existing = await self.session.execute(
            select(User).where(User.email == data.email)
        )
        if existing.scalar_one_or_none():
            raise Conflict("Email already exists")

        user = User(
            email=data.email,
            password_hash=hash_password(data.password),
            full_name=data.full_name,
            is_admin=data.is_admin,
        )
        self.session.add(user)
        await self.session.flush()
        await self.session.refresh(user)
        return user

    async def update_user(self, user_id: int, data: UserUpdate) -> User:
        result = await self.session.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        if not user:
            raise NotFound("User", user_id)

        if data.email is not None:
            existing = await self.session.execute(
                select(User).where(
                    User.email == data.email, User.id != user_id
                )
            )
            if existing.scalar_one_or_none():
                raise Conflict("Email already exists")
            user.email = data.email
        if data.password is not None:
            user.password_hash = hash_password(data.password)
        if data.full_name is not None:
            user.full_name = data.full_name
        if data.is_admin is not None:
            user.is_admin = data.is_admin

        await self.session.flush()
        await self.session.refresh(user)
        return user

    async def delete_user(self, user_id: int) -> None:
        result = await self.session.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        if not user:
            raise NotFound("User", user_id)

        await self.session.delete(user)
        await self.session.flush()

    async def get_user_accounts(self, user_id: int) -> list[Account]:
        result = await self.session.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        if not user:
            raise NotFound("User", user_id)

        accounts_result = await self.session.execute(
            select(Account).where(Account.user_id == user_id)
        )
        return list(accounts_result.scalars().all())
