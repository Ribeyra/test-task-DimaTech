import pytest
from httpx import AsyncClient

from app.config import settings
from app.utils.security import compute_signature


def login_payload(email: str, password: str) -> dict:
    return {"email": email, "password": password}


async def get_user_token(client: AsyncClient) -> str:
    resp = await client.post("/api/v1/auth/login", json=login_payload("user@test.com", "user123"))
    return resp.json()["access_token"]


async def get_admin_token(client: AsyncClient) -> str:
    resp = await client.post("/api/v1/auth/login", json=login_payload("admin@test.com", "admin123"))
    return resp.json()["access_token"]


class TestAuthAPI:
    async def test_login_user(self, client: AsyncClient):
        resp = await client.post("/api/v1/auth/login", json=login_payload("user@test.com", "user123"))
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    async def test_login_wrong_password(self, client: AsyncClient):
        resp = await client.post("/api/v1/auth/login", json=login_payload("user@test.com", "wrong1"))
        assert resp.status_code == 401
        assert resp.json()["detail"] == "Invalid email or password"

    async def test_login_wrong_email(self, client: AsyncClient):
        resp = await client.post("/api/v1/auth/login", json=login_payload("noone@test.com", "user123"))
        assert resp.status_code == 401

    async def test_logout_then_me_fails(self, client: AsyncClient):
        token = await get_user_token(client)
        resp = await client.post("/api/v1/auth/logout", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200

        resp = await client.get("/api/v1/users/me", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 401
        assert resp.json()["detail"] == "Token has been revoked"


class TestAdminAPI:
    async def test_list_users(self, client: AsyncClient):
        token = await get_admin_token(client)
        resp = await client.get("/api/v1/admin/users", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) >= 2
        emails = [u["email"] for u in data]
        assert "user@test.com" in emails
        assert "admin@test.com" in emails

    async def test_create_user(self, client: AsyncClient):
        token = await get_admin_token(client)
        resp = await client.post(
            "/api/v1/admin/users",
            headers={"Authorization": f"Bearer {token}"},
            json={"email": "newbie@test.com", "password": "pass123", "full_name": "Newbie"},
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["email"] == "newbie@test.com"
        assert data["full_name"] == "Newbie"

    async def test_create_duplicate_email(self, client: AsyncClient):
        token = await get_admin_token(client)
        resp = await client.post(
            "/api/v1/admin/users",
            headers={"Authorization": f"Bearer {token}"},
            json={"email": "user@test.com", "password": "pass123", "full_name": "Dup"},
        )
        assert resp.status_code == 409
        assert resp.json()["detail"] == "Email already exists"

    async def test_update_user(self, client: AsyncClient):
        token = await get_admin_token(client)
        resp = await client.put(
            "/api/v1/admin/users/1",
            headers={"Authorization": f"Bearer {token}"},
            json={"full_name": "Updated User"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["full_name"] == "Updated User"

    async def test_update_user_not_found(self, client: AsyncClient):
        token = await get_admin_token(client)
        resp = await client.put(
            "/api/v1/admin/users/9999",
            headers={"Authorization": f"Bearer {token}"},
            json={"full_name": "Ghost"},
        )
        assert resp.status_code == 404

    async def test_delete_user(self, client: AsyncClient):
        token = await get_admin_token(client)

        create_resp = await client.post(
            "/api/v1/admin/users",
            headers={"Authorization": f"Bearer {token}"},
            json={"email": "delete_me@test.com", "password": "pass123", "full_name": "Delete Me"},
        )
        user_id = create_resp.json()["id"]

        resp = await client.delete(
            f"/api/v1/admin/users/{user_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 204

    async def test_delete_user_not_found(self, client: AsyncClient):
        token = await get_admin_token(client)
        resp = await client.delete(
            "/api/v1/admin/users/9999",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 404

    async def test_get_user_accounts(self, client: AsyncClient):
        token = await get_admin_token(client)
        resp = await client.get(
            "/api/v1/admin/users/1/accounts",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) >= 1
        assert data[0]["user_id"] == 1

    async def test_get_user_accounts_not_found(self, client: AsyncClient):
        token = await get_admin_token(client)
        resp = await client.get(
            "/api/v1/admin/users/9999/accounts",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 404

    async def test_user_forbidden_admin(self, client: AsyncClient):
        token = await get_user_token(client)
        resp = await client.get(
            "/api/v1/admin/users",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 403


class TestWebhookAPI:
    async def test_webhook_payment_success(self, client: AsyncClient):
        secret = settings.webhook_secret_key
        transaction_id = "wh-test-001"
        account_id = 1
        user_id = 1
        amount = 100

        data = {
            "account_id": account_id,
            "amount": amount,
            "transaction_id": transaction_id,
            "user_id": user_id,
        }
        signature = compute_signature(data, secret)

        resp = await client.post(
            "/api/v1/webhook/payment",
            json={
                "transaction_id": transaction_id,
                "user_id": user_id,
                "account_id": account_id,
                "amount": amount,
                "signature": signature,
            },
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == "success"

    async def test_webhook_invalid_signature(self, client: AsyncClient):
        resp = await client.post(
            "/api/v1/webhook/payment",
            json={
                "transaction_id": "wh-test-002",
                "user_id": 1,
                "account_id": 1,
                "amount": 100,
                "signature": "deadbeef" * 8,
            },
        )
        assert resp.status_code == 400
        assert resp.json()["detail"] == "Invalid signature"

    async def test_webhook_duplicate_transaction(self, client: AsyncClient):
        secret = settings.webhook_secret_key
        transaction_id = "wh-test-003"

        data = {
            "account_id": 1,
            "amount": 100,
            "transaction_id": transaction_id,
            "user_id": 1,
        }
        signature = compute_signature(data, secret)

        payload = {
            "transaction_id": transaction_id,
            "user_id": 1,
            "account_id": 1,
            "amount": 100,
            "signature": signature,
        }

        resp1 = await client.post("/api/v1/webhook/payment", json=payload)
        assert resp1.status_code == 200

        resp2 = await client.post("/api/v1/webhook/payment", json=payload)
        assert resp2.status_code == 409
        assert resp2.json()["detail"] == "Transaction already processed"
