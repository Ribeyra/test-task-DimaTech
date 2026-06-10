from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import Conflict
from app.models.account import Account
from app.models.transaction import Transaction


class WebhookService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def process_payment(
        self,
        transaction_id: str,
        account_id: int,
        user_id: int,
        amount: Decimal,
    ) -> dict:
        result = await self.session.execute(
            select(Transaction).where(
                Transaction.transaction_id == transaction_id
            )
        )
        if result.scalar_one_or_none():
            raise Conflict("Transaction already processed")

        result = await self.session.execute(
            select(Account).where(
                Account.id == account_id,
                Account.user_id == user_id,
            )
        )
        account = result.scalar_one_or_none()

        if not account:
            account = Account(
                id=account_id, user_id=user_id, balance=Decimal(0)
            )
            self.session.add(account)

        transaction = Transaction(
            transaction_id=transaction_id,
            account_id=account.id,
            user_id=user_id,
            amount=amount,
        )
        self.session.add(transaction)

        account.balance += amount

        try:
            await self.session.flush()
        except IntegrityError:
            await self.session.rollback()
            raise Conflict("Transaction already processed")

        return {"status": "success", "message": "Payment processed"}
