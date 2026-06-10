from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.database import get_session
from app.models.user import User
from app.schemas.account import AccountResponse
from app.schemas.user import UserResponse
from app.services.user import UserService

router = APIRouter(prefix="/api/v1/users", tags=["users"])


@router.get("/me", response_model=UserResponse)
async def get_my_profile(current_user: User = Depends(get_current_user)):
    return UserResponse.model_validate(current_user)


@router.get("/me/accounts", response_model=list[AccountResponse])
async def get_my_accounts(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    accounts = await UserService(session).get_accounts(current_user.id)
    return [AccountResponse.model_validate(a) for a in accounts]


@router.get("/me/transactions")
async def get_my_transactions(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    transactions = await UserService(session).get_transactions(current_user.id)
    return [
        {
            "id": t.id,
            "transaction_id": t.transaction_id,
            "account_id": t.account_id,
            "amount": float(t.amount),
            "created_at": t.created_at.isoformat(),
        }
        for t in transactions
    ]
