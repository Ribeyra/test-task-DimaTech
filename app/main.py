from fastapi import FastAPI
from fastapi.responses import JSONResponse

from app.api.v1.routes import admin, auth, users, webhook
from app.exceptions import AppException

app = FastAPI(title="Test Task API", version="0.1.0")


@app.exception_handler(AppException)
async def app_exception_handler(request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code, content={"detail": exc.message}
    )


app.include_router(auth.router)
app.include_router(users.router)
app.include_router(admin.router)
app.include_router(webhook.router)
