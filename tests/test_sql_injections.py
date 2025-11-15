import pytest
from fastapi.testclient import TestClient

from app.db.models import LeadStatus


@pytest.fixture(scope="function")
def test_user(client: TestClient):
    """Фикстура для создания тестового пользователя и получения токена авторизации."""
    user_data = {
        "username": "testuser_sql",
        "email": "testsql@example.com",
        "password": "testpass123",
    }
    response = client.post("/register", json=user_data)
    assert response.status_code == 201

    login_data = {"username": "testuser_sql", "password": "testpass123"}
    response = client.post("/token", data=login_data)
    assert response.status_code == 200
    token = response.json()["access_token"]

    return {"Authorization": f"Bearer {token}"}


class TestSQLInjectionProtection:
    # Список типичных SQL инъекций для тестирования
    SQL_INJECTION_PAYLOADS = [
        "' OR '1'='1",
        "'; DROP TABLE users; --",
        "' UNION SELECT * FROM users --",
        "admin'--",
        "1' OR '1' = '1' /*",
        "' OR 1=1--",
        "1; DROP TABLE companies;--",
    ]

    def test_register_username_sql_injection(self, client: TestClient):
        for idx, payload in enumerate(self.SQL_INJECTION_PAYLOADS):
            user_data = {
                "username": payload,
                "email": f"test{idx}@example.com",
                "password": "password123",
            }
            response = client.post("/register", json=user_data)

            assert response.status_code in [
                201,
                401,
                422,
            ], f"Неожиданный статус код {response.status_code} для payload: {payload}"

            # Если регистрация прошла, убеждаемся что username сохранен как есть (экранирован)
            if response.status_code == 201:
                data = response.json()
                # Username должен быть сохранен безопасно, без выполнения SQL
                assert "username" in data

    def test_login_username_sql_injection(self, client: TestClient):
        # Сначала создаем легитимного пользователя
        user_data = {
            "username": "legituser",
            "email": "legit@example.com",
            "password": "password123",
        }
        client.post("/register", json=user_data)

        # Пытаемся войти с SQL инъекцией
        for payload in self.SQL_INJECTION_PAYLOADS:
            login_data = {
                "username": payload,
                "password": "password123",
            }
            response = client.post("/token", data=login_data)

            # Должен вернуться 401 (неавторизован), так как пользователя с таким username нет
            # или SQL инъекция не должна сработать
            assert (
                response.status_code == 401
            ), f"SQL инъекция могла сработать! Статус: {response.status_code}, payload: {payload}"

    def test_company_id_path_sql_injection(self, client: TestClient, test_user):
        # Сначала создаем компанию
        company_data = {"name": "Test Company", "sector": "Technology"}
        response = client.post("/companies/", json=company_data, headers=test_user)
        assert response.status_code == 201

        # Пытаемся получить компанию с SQL инъекцией в ID
        sql_payloads_for_int = [
            "1' OR '1'='1",
            "1; DROP TABLE companies;--",
            "1 UNION SELECT * FROM users",
        ]

        for payload in sql_payloads_for_int:
            response = client.get(f"/companies/{payload}", headers=test_user)

            # FastAPI должен вернуть 422 (validation error), так как ожидается int
            assert response.status_code == 422, f"Неожиданный статус для payload: {payload}"

            # Проверяем, что в ответе есть информация об ошибке валидации
            data = response.json()
            assert "detail" in data

    def test_leads_status_query_sql_injection(self, client: TestClient, test_user):
        # Создаем компанию и лид
        company_data = {"name": "Lead Company", "sector": "Tech"}
        response = client.post("/companies/", json=company_data, headers=test_user)
        company_id = response.json()["id"]

        lead_data = {
            "title": "Test Lead",
            "status": LeadStatus.NEW.value,
            "company_id": company_id,
        }
        client.post("/leads/", json=lead_data, headers=test_user)

        # Пытаемся получить лиды с SQL инъекцией в фильтре статуса
        for payload in self.SQL_INJECTION_PAYLOADS:
            response = client.get(f"/leads/?status={payload}", headers=test_user)

            # FastAPI должен вернуть 422, так как status должен быть из enum LeadStatus
            assert response.status_code == 422, (
                f"SQL инъекция могла сработать в query параметре! "
                f"Статус: {response.status_code}, payload: {payload}"
            )

            # Проверяем наличие деталей ошибки
            data = response.json()
            assert "detail" in data

    def test_company_update_field_sql_injection(self, client: TestClient, test_user):
        # Создаем компанию
        company_data = {"name": "Original Company", "sector": "Technology"}
        response = client.post("/companies/", json=company_data, headers=test_user)
        company_id = response.json()["id"]

        # Пытаемся обновить с SQL инъекцией
        for payload in self.SQL_INJECTION_PAYLOADS:
            update_data = {
                "name": payload,
                "sector": f"Sector {payload}",
            }
            response = client.put(f"/companies/{company_id}", json=update_data, headers=test_user)

            # Обновление должно либо пройти успешно (200) с экранированными данными,
            # либо быть отвергнуто валидацией (422)
            assert response.status_code in [
                200,
                422,
            ], f"Неожиданный статус код {response.status_code} для payload: {payload}"

            if response.status_code == 200:
                data = response.json()
                # Проверяем, что данные сохранены как строки, а не выполнены как SQL
                assert data["name"] == payload, "Данные должны быть сохранены как есть"

                # Проверяем, что компания все еще существует (не удалена SQL инъекцией)
                response = client.get(f"/companies/{company_id}", headers=test_user)
                assert response.status_code == 200

    def test_pagination_parameters_sql_injection(self, client: TestClient, test_user):
        # Создаем компанию для теста
        company_data = {"name": "Pagination Test", "sector": "Tech"}
        client.post("/companies/", json=company_data, headers=test_user)

        # Пытаемся использовать SQL инъекции в параметрах пагинации
        injection_params = [
            ("skip", "0' OR '1'='1"),
            ("limit", "10; DROP TABLE companies;--"),
            ("skip", "0 UNION SELECT * FROM users"),
        ]

        for param_name, payload in injection_params:
            response = client.get(f"/companies/?{param_name}={payload}", headers=test_user)

            # должен вернуть 422, так как ожидается int
            assert response.status_code == 422, f"Неожиданный статус для {param_name}={payload}"

    def test_email_sql_injection_registration(self, client: TestClient):
        """
        Дополнительный тест: Проверка SQL инъекции в поле email.

        Пытаемся зарегистрировать пользователя с SQL инъекцией в email.
        Pydantic EmailStr валидатор должен отвергнуть невалидные email.
        """
        for payload in self.SQL_INJECTION_PAYLOADS:
            user_data = {
                "username": "testuser123",
                "email": payload,
                "password": "password123",
            }
            response = client.post("/register", json=user_data)

            # EmailStr валидатор должен отвергнуть невалидный email (422)
            # или обработать как строку безопасно (201)
            assert response.status_code in [
                201,
                422,
            ], f"Неожиданный статус для email payload: {payload}"
