# Ручное тестирование

## 1. Авторизация

```bash
# Успешный логин user
curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@test.com","password":"user123"}'

# Успешный логин admin
curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@test.com","password":"admin123"}'

# Неуспешный логин
curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@test.com","password":"wrong"}'
```

## 2. Профиль и данные пользователя

```bash
TOKEN="eyJ..."

# GET /users/me
curl -s http://localhost:8000/api/v1/users/me \
  -H "Authorization: Bearer $TOKEN"

# GET /users/me/accounts
curl -s http://localhost:8000/api/v1/users/me/accounts \
  -H "Authorization: Bearer $TOKEN"

# GET /users/me/transactions
curl -s http://localhost:8000/api/v1/users/me/transactions \
  -H "Authorization: Bearer $TOKEN"
```

## 3. Logout

```bash
TOKEN="eyJ..."

curl -s -X POST http://localhost:8000/api/v1/auth/logout \
  -H "Authorization: Bearer $TOKEN"

# После logout токен перестаёт работать
curl -s http://localhost:8000/api/v1/users/me \
  -H "Authorization: Bearer $TOKEN"
```

## 4. Админка

```bash
ADMIN_TOKEN="eyJ..."

# Список пользователей
curl -s http://localhost:8000/api/v1/admin/users \
  -H "Authorization: Bearer $ADMIN_TOKEN"

# Создать пользователя
curl -s -X POST http://localhost:8000/api/v1/admin/users \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"pass123","full_name":"Test"}' | jq

# Обновить пользователя
curl -s -X PUT http://localhost:8000/api/v1/admin/users/3 \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"full_name":"Updated","is_admin":true}' | jq

# Удалить пользователя
curl -s -X DELETE http://localhost:8000/api/v1/admin/users/3 \
  -H "Authorization: Bearer $ADMIN_TOKEN"

# Счета пользователя
curl -s http://localhost:8000/api/v1/admin/users/1/accounts \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

## 5. Webhook

```bash
SECRET_KEY="super-secret-key-change-in-production"
TRANSACTION_ID="5eae174f-7cd0-472c-bd36-35660f00132b"
USER_ID=1
ACCOUNT_ID=1
AMOUNT=100

RAW="${ACCOUNT_ID}${AMOUNT}${TRANSACTION_ID}${USER_ID}${SECRET_KEY}"
SIGNATURE=$(echo -n "$RAW" | sha256sum | cut -d' ' -f1)

curl -X POST http://localhost:8000/api/v1/webhook/payment \
  -H "Content-Type: application/json" \
  -d "{
    \"transaction_id\": \"$TRANSACTION_ID\",
    \"user_id\": $USER_ID,
    \"account_id\": $ACCOUNT_ID,
    \"amount\": $AMOUNT,
    \"signature\": \"$SIGNATURE\"
  }"
```

```python
# Python version
import hashlib
import requests

data = {
    "transaction_id": "5eae174f-7cd0-472c-bd36-35660f00132b",
    "user_id": 1,
    "account_id": 1,
    "amount": 100,
}
secret_key = "super-secret-key-change-in-production"

raw = "".join(str(data[k]) for k in sorted(data)) + secret_key
data["signature"] = hashlib.sha256(raw.encode()).hexdigest()

resp = requests.post("http://localhost:8000/api/v1/webhook/payment", json=data)
print(resp.json())
```

## 6. Проверка доступа: user не может зайти в админку

```bash
TOKEN="eyJ..."  # токен обычного пользователя

curl -s http://localhost:8000/api/v1/admin/users \
  -H "Authorization: Bearer $TOKEN"
# Ожидается 403 Forbidden
```
