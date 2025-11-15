import pytest
from fastapi.testclient import TestClient


def test_string_length_validation(client: TestClient):
    """Тест валидации длины строк."""
    # Создаем пользователя для аутентификации
    user_data = {"username": "testuser", "email": "test@example.com", "password": "password123"}
    client.post("/register", json=user_data)
    login_response = client.post("/token", data={"username": "testuser", "password": "password123"})
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Проверяем минимальную длину имени компании (min=1)
    response = client.post("/companies/", json={"name": "", "sector": "IT"}, headers=headers)
    assert response.status_code == 422

    # Проверяем максимальную длину имени компании (max=255)
    response = client.post("/companies/", json={"name": "A" * 256, "sector": "IT"}, headers=headers)
    assert response.status_code == 422

    # Проверяем корректную длину
    response = client.post(
        "/companies/", json={"name": "Valid Company", "sector": "IT"}, headers=headers
    )
    assert response.status_code == 201


def test_email_validation(client: TestClient):
    """Тест валидации формата email."""
    # Невалидный email без @
    response = client.post(
        "/register",
        json={"username": "testuser1", "email": "invalid-email", "password": "password123"},
    )
    assert response.status_code == 422

    # Невалидный email без домена
    response = client.post(
        "/register", json={"username": "testuser2", "email": "test@", "password": "password123"}
    )
    assert response.status_code == 422

    # Валидный email
    response = client.post(
        "/register",
        json={"username": "testuser3", "email": "valid@example.com", "password": "password123"},
    )
    assert response.status_code == 201


def test_enum_status_validation(client: TestClient):
    """Тест валидации enum статуса лида."""
    # Создаем пользователя и компанию
    user_data = {"username": "testuser", "email": "test@example.com", "password": "password123"}
    client.post("/register", json=user_data)
    login_response = client.post("/token", data={"username": "testuser", "password": "password123"})
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    company_response = client.post(
        "/companies/", json={"name": "Test Company", "sector": "IT"}, headers=headers
    )
    company_id = company_response.json()["id"]

    # Невалидный статус
    response = client.post(
        "/leads/",
        json={"title": "Test Lead", "status": "invalid_status", "company_id": company_id},
        headers=headers,
    )
    assert response.status_code == 422

    # Валидные статусы
    valid_statuses = ["new", "qualified", "proposal", "won", "lost"]
    for status in valid_statuses:
        response = client.post(
            "/leads/",
            json={"title": f"Lead with {status}", "status": status, "company_id": company_id},
            headers=headers,
        )
        assert response.status_code == 201
        assert response.json()["status"] == status


def test_required_fields_validation(client: TestClient):
    """Тест обязательных полей."""
    # Регистрация без обязательного поля username
    response = client.post(
        "/register", json={"email": "test@example.com", "password": "password123"}
    )
    assert response.status_code == 422

    # Регистрация без обязательного поля password
    response = client.post("/register", json={"username": "testuser", "email": "test@example.com"})
    assert response.status_code == 422

    # Создание компании без обязательного поля sector
    user_data = {"username": "testuser", "email": "test@example.com", "password": "password123"}
    client.post("/register", json=user_data)
    login_response = client.post("/token", data={"username": "testuser", "password": "password123"})
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = client.post("/companies/", json={"name": "Test Company"}, headers=headers)
    assert response.status_code == 422


def test_datetime_utc_format(client: TestClient):
    """Тест формата datetime (UTC) в ответах."""
    # Создаем пользователя
    user_data = {"username": "testuser", "email": "test@example.com", "password": "password123"}
    response = client.post("/register", json=user_data)
    assert response.status_code == 201

    data = response.json()

    # Проверяем наличие datetime полей
    assert "created_at" in data
    assert "updated_at" in data

    # Проверяем формат ISO 8601
    from datetime import datetime

    try:
        created_at = datetime.fromisoformat(data["created_at"].replace("Z", "+00:00"))
        updated_at = datetime.fromisoformat(data["updated_at"].replace("Z", "+00:00"))
        assert created_at is not None
        assert updated_at is not None
    except ValueError:
        pytest.fail("Datetime не в ISO 8601 формате")


def test_type_validation(client: TestClient):
    """Тест валидации типов данных."""
    # Создаем пользователя
    user_data = {"username": "testuser", "email": "test@example.com", "password": "password123"}
    client.post("/register", json=user_data)
    login_response = client.post("/token", data={"username": "testuser", "password": "password123"})
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    company_response = client.post(
        "/companies/", json={"name": "Test Company", "sector": "IT"}, headers=headers
    )
    company_id = company_response.json()["id"]

    # Проверяем, что company_id должен быть int
    response = client.post(
        "/leads/", json={"title": "Test Lead", "company_id": "not_an_integer"}, headers=headers
    )
    assert response.status_code == 422

    # Проверяем корректный тип
    response = client.post(
        "/leads/", json={"title": "Test Lead", "company_id": company_id}, headers=headers
    )
    assert response.status_code == 201
