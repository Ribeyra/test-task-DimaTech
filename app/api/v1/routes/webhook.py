import hmac

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_session
from app.schemas.webhook import PaymentResponse, PaymentWebhook
from app.services.webhook import WebhookService
from app.utils.security import compute_signature

router = APIRouter(prefix="/api/v1/webhook", tags=["webhook"])


@router.post("/payment", response_model=PaymentResponse)
async def payment_webhook(
    request: Request,
    session: AsyncSession = Depends(get_session),
):
    body = PaymentWebhook.model_validate(await request.json())

    data = body.model_dump(exclude={"signature"})
    expected_sig = compute_signature(data, settings.webhook_secret_key)

    if not hmac.compare_digest(body.signature, expected_sig):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid signature"
        )

    result = await WebhookService(session).process_payment(
        transaction_id=body.transaction_id,
        account_id=body.account_id,
        user_id=body.user_id,
        amount=body.amount,
    )

    return PaymentResponse(status="success", message=result["message"])
