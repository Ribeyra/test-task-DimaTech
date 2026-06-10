from typing import AsyncGenerator

import asyncpg
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.database import Base, get_session
from app.main import app
from app.models.account import Account
from app.models.user import User
from app.utils.security import hash_password

TEST_DB_URL = "postgresql+asyncpg:///test_task_test"


@pytest_asyncio.fixture(scope="session")
async def db_engine():
    conn = await asyncpg.connect(database="postgres")
    try:
        await conn.execute("CREATE DATABASE test_task_test")
    except asyncpg.DuplicateDatabaseError:
        pass
    await conn.close()

    engine = create_async_engine(TEST_DB_URL)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


async def seed_test_data(session: AsyncSession):
    result = await session.execute(select(User).where(User.email == "user@test.com"))
    if result.scalar_one_or_none() is not None:
        return

    user = User(
        email="user@test.com",
        password_hash=hash_password("user123"),
        full_name="Test User",
        is_admin=False,
    )
    session.add(user)
    await session.flush()

    admin = User(
        email="admin@test.com",
        password_hash=hash_password("admin123"),
        full_name="Admin User",
        is_admin=True,
    )
    session.add(admin)
    await session.flush()

    account = Account(user_id=user.id, balance=0)
    session.add(account)
    await session.flush()

    await session.commit()


@pytest_asyncio.fixture
async def session(db_engine) -> AsyncGenerator[AsyncSession, None]:
    factory = async_sessionmaker(db_engine, expire_on_commit=False)
    async with factory() as s:
        await seed_test_data(s)
        yield s
        await s.rollback()


@pytest_asyncio.fixture
async def client(session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    async def override_get_session():
        yield session

    app.dependency_overrides[get_session] = override_get_session
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
    app.dependency_overrides.clear()
