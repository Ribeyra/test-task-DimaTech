from decimal import Decimal

from pydantic import BaseModel, field_validator


class PaymentWebhook(BaseModel):
    transaction_id: str
    user_id: int
    account_id: int
    amount: Decimal
    signature: str

    @field_validator("amount", mode="before")
    @classmethod
    def coerce_amount(cls, v):
        if isinstance(v, str):
            return Decimal(v)
        return Decimal(str(v))


class PaymentResponse(BaseModel):
    status: str = "success"
    message: str = "Payment processed"
