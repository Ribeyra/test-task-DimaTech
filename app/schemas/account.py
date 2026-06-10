from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, field_serializer


class AccountResponse(BaseModel):
    id: int
    user_id: int
    balance: Decimal
    created_at: datetime

    @field_serializer("balance")
    def serialize_balance(self, v: Decimal) -> float:
        return float(v)

    model_config = {"from_attributes": True}
