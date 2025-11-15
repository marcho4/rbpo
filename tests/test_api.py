import pytest
from fastapi.testclient import TestClient

from app.db.models import LeadStatus


@pytest.fixture(scope="function")
def test_user(client: TestClient):
    """Фикстура для создания тестового пользователя и получения токена авторизации."""
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpass123",
    }
    response = client.post("/register", json=user_data)
    assert response.status_code == 201

    login_data = {"username": "testuser", "password": "testpass123"}
    response = client.post("/token", data=login_data)
    assert response.status_code == 200
    token = response.json()["access_token"]

    return {"Authorization": f"Bearer {token}"}


def test_health(client: TestClient):
    """Тест для проверки работоспособности сервиса."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_register_user(client: TestClient):
    """Тест для регистрации нового пользователя."""
    user_data = {
        "username": "newuser",
        "email": "newuser@example.com",
        "password": "newpass123",
    }
    response = client.post("/register", json=user_data)
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "newuser"
    assert data["email"] == "newuser@example.com"
    assert "id" in data


def test_login(client: TestClient):
    """Тест для входа пользователя в систему и получения токена."""
    user_data = {
        "username": "loginuser",
        "email": "loginuser@example.com",
        "password": "loginpass123",
    }
    client.post("/register", json=user_data)

    login_data = {"username": "loginuser", "password": "loginpass123"}
    response = client.post("/token", data=login_data)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_create_company(client: TestClient, test_user):
    """Тест для создания новой компании."""
    company_data = {"name": "Test Company", "sector": "Technology"}
    response = client.post("/companies/", json=company_data, headers=test_user)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Company"
    assert data["sector"] == "Technology"
    assert "id" in data


def test_get_companies(client: TestClient, test_user):
    """Тест для получения списка компаний."""
    company_data = {"name": "Test Company 2", "sector": "Finance"}
    client.post("/companies/", json=company_data, headers=test_user)

    response = client.get("/companies/", headers=test_user)
    assert response.status_code == 200
    companies = response.json()
    assert len(companies) >= 1
    assert any(company["name"] == "Test Company 2" for company in companies)


def test_update_company(client: TestClient, test_user):
    """Тест для обновления данных компании."""
    company_data = {"name": "Original Company", "sector": "Healthcare"}
    response = client.post("/companies/", json=company_data, headers=test_user)
    company_id = response.json()["id"]

    update_data = {"name": "Updated Company", "sector": "Technology"}
    response = client.put(f"/companies/{company_id}", json=update_data, headers=test_user)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Company"
    assert data["sector"] == "Technology"


def test_delete_company(client: TestClient, test_user):
    """Тест для удаления компании."""
    company_data = {"name": "Company to Delete", "sector": "Retail"}
    response = client.post("/companies/", json=company_data, headers=test_user)
    company_id = response.json()["id"]

    response = client.delete(f"/companies/{company_id}", headers=test_user)
    assert response.status_code == 204

    response = client.get(f"/companies/{company_id}", headers=test_user)
    assert response.status_code == 404


def test_create_lead(client: TestClient, test_user):
    """Тест для создания нового лида."""
    company_data = {"name": "Lead Company", "sector": "Education"}
    response = client.post("/companies/", json=company_data, headers=test_user)
    company_id = response.json()["id"]

    lead_data = {
        "title": "Test Lead",
        "description": "A test lead description",
        "status": LeadStatus.NEW.value,
        "company_id": company_id,
    }
    response = client.post("/leads/", json=lead_data, headers=test_user)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Lead"
    assert data["status"] == LeadStatus.NEW.value
    assert data["company_id"] == company_id


def test_get_leads_with_filter(client: TestClient, test_user):
    """Тест для получения списка лидов с фильтрацией по статусу."""
    company_data = {"name": "Filter Company", "sector": "Manufacturing"}
    response = client.post("/companies/", json=company_data, headers=test_user)
    company_id = response.json()["id"]

    lead1_data = {
        "title": "New Lead",
        "status": LeadStatus.NEW.value,
        "company_id": company_id,
    }
    lead2_data = {
        "title": "Qualified Lead",
        "status": LeadStatus.QUALIFIED.value,
        "company_id": company_id,
    }

    client.post("/leads/", json=lead1_data, headers=test_user)
    client.post("/leads/", json=lead2_data, headers=test_user)

    response = client.get(f"/leads/?status={LeadStatus.NEW.value}", headers=test_user)
    assert response.status_code == 200
    leads = response.json()
    assert all(lead["status"] == LeadStatus.NEW.value for lead in leads)


def test_unauthorized_access(client: TestClient):
    """Тест для проверки неавторизованного доступа к защищенным эндпоинтам."""
    response = client.get("/companies/")
    assert response.status_code == 401

    response = client.get("/leads/")
    assert response.status_code == 401


def test_pagination(client: TestClient, test_user):
    """Тест для проверки большими строками данных."""
    company_data = {"name": "Large Company", "sector": "Retail"}
    response = client.post("/companies/", json=company_data, headers=test_user)
    company_id = response.json()["id"]

    lead_data = {
        "title": "Large Lead" * 100,
        "description": "A large lead description" * 100,
        "status": LeadStatus.NEW.value,
        "company_id": company_id,
    }
    response = client.post("/leads/", json=lead_data, headers=test_user)

    assert response.status_code == 422
