import pytest
from sqlalchemy import select

from app.exceptions import Conflict, NotFound
from app.models.account import Account
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.services.admin import AdminService


class TestAdminService:
    async def test_list_users(self, session):
        users = await AdminService(session).list_users()
        assert len(users) >= 2
        emails = [u.email for u in users]
        assert "user@test.com" in emails
        assert "admin@test.com" in emails

    async def test_create_user(self, session):
        data = UserCreate(
            email="new@test.com", password="pass123", full_name="New User"
        )
        user = await AdminService(session).create_user(data)
        assert user.id is not None
        assert user.email == "new@test.com"
        assert user.full_name == "New User"
        assert user.is_admin is False

        result = await session.execute(
            select(User).where(User.id == user.id)
        )
        saved = result.scalar_one()
        assert saved.full_name == "New User"

    async def test_create_duplicate_email(self, session):
        data = UserCreate(
            email="user@test.com", password="pass123", full_name="Dup"
        )
        with pytest.raises(Conflict, match="Email already exists"):
            await AdminService(session).create_user(data)

    async def test_update_user_fields(self, session):
        result = await session.execute(
            select(User).where(User.email == "user@test.com")
        )
        user_id = result.scalar_one().id

        data = UserUpdate(full_name="Updated Name", is_admin=True)
        updated = await AdminService(session).update_user(user_id, data)
        assert updated.full_name == "Updated Name"
        assert updated.is_admin is True

    async def test_update_user_email(self, session):
        result = await session.execute(
            select(User).where(User.email == "user@test.com")
        )
        user_id = result.scalar_one().id

        data = UserUpdate(email="newemail@test.com")
        updated = await AdminService(session).update_user(user_id, data)
        assert updated.email == "newemail@test.com"

    async def test_update_user_email_conflict(self, session):
        result = await session.execute(
            select(User).where(User.email == "admin@test.com")
        )
        admin_id = result.scalar_one().id

        data = UserUpdate(email="user@test.com")
        with pytest.raises(Conflict, match="Email already exists"):
            await AdminService(session).update_user(admin_id, data)

    async def test_update_user_not_found(self, session):
        data = UserUpdate(full_name="Nobody")
        with pytest.raises(NotFound, match="User with id 9999 not found"):
            await AdminService(session).update_user(9999, data)

    async def test_delete_user(self, session):
        data = UserCreate(email="todelete@test.com", password="pass123", full_name="Delete Me")
        user = await AdminService(session).create_user(data)
        user_id = user.id

        await AdminService(session).delete_user(user_id)

        result = await session.execute(select(User).where(User.id == user_id))
        assert result.scalar_one_or_none() is None

    async def test_delete_user_not_found(self, session):
        with pytest.raises(NotFound, match="User with id 9999 not found"):
            await AdminService(session).delete_user(9999)

    async def test_get_user_accounts(self, session):
        result = await session.execute(
            select(User).where(User.email == "user@test.com")
        )
        user_id = result.scalar_one().id

        accounts = await AdminService(session).get_user_accounts(user_id)
        assert len(accounts) >= 1
        assert all(a.user_id == user_id for a in accounts)

    async def test_get_user_accounts_not_found(self, session):
        with pytest.raises(NotFound, match="User with id 9999 not found"):
            await AdminService(session).get_user_accounts(9999)
