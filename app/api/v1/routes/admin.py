from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_admin
from app.database import get_session
from app.models.user import User
from app.schemas.account import AccountResponse
from app.schemas.user import UserCreate, UserResponse, UserUpdate
from app.services.admin import AdminService

router = APIRouter(prefix="/api/v1/admin", tags=["admin"])


@router.get("/users", response_model=list[UserResponse])
async def list_users(
    admin: User = Depends(get_current_admin),
    session: AsyncSession = Depends(get_session),
):
    users = await AdminService(session).list_users()
    return [UserResponse.model_validate(u) for u in users]


@router.post(
    "/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def create_user(
    body: UserCreate,
    admin: User = Depends(get_current_admin),
    session: AsyncSession = Depends(get_session),
):
    user = await AdminService(session).create_user(body)
    return UserResponse.model_validate(user)


@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    body: UserUpdate,
    admin: User = Depends(get_current_admin),
    session: AsyncSession = Depends(get_session),
):
    user = await AdminService(session).update_user(user_id, body)
    return UserResponse.model_validate(user)


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    admin: User = Depends(get_current_admin),
    session: AsyncSession = Depends(get_session),
):
    await AdminService(session).delete_user(user_id)


@router.get("/users/{user_id}/accounts", response_model=list[AccountResponse])
async def get_user_accounts(
    user_id: int,
    admin: User = Depends(get_current_admin),
    session: AsyncSession = Depends(get_session),
):
    accounts = await AdminService(session).get_user_accounts(user_id)
    return [AccountResponse.model_validate(a) for a in accounts]
