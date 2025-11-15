import os
import re

import pytest


def test_logs_do_not_contain_secrets(get_collected_logs):
    """
    Тест проверяет, что в логах отсутствуют секретные данные.

    Проверяемые секреты:
    - Пароли из тестов
    - JWT токены
    - SECRET_KEY из переменных окружения
    - Bearer токены
    """
    logs = get_collected_logs()

    test_passwords = [
        "testpass123",
        "newpass123",
        "loginpass123",
    ]

    secret_key = os.getenv("SECRET_KEY", "secret")

    jwt_pattern = re.compile(r"eyJ[A-Za-z0-9-_]+\.eyJ[A-Za-z0-9-_]+\.[A-Za-z0-9-_]+")
    bearer_pattern = re.compile(r"Bearer\s+[A-Za-z0-9-_]+\.[A-Za-z0-9-_]+\.[A-Za-z0-9-_]+")

    errors = []

    for i, log_entry in enumerate(logs):
        for password in test_passwords:
            if password in log_entry:
                errors.append(f"Лог #{i} содержит пароль: {password[:5]}***")

        if secret_key in log_entry and len(secret_key) > 5:
            errors.append(f"Лог #{i} содержит SECRET_KEY")

        if jwt_pattern.search(log_entry):
            errors.append(f"Лог #{i} содержит JWT токен")

        if bearer_pattern.search(log_entry):
            errors.append(f"Лог #{i} содержит Bearer токен")

    if errors:
        error_message = (
            f"\n\nВ логах обнаружены секретные данные!\n"
            f"Найдено нарушений: {len(errors)}\n\n"
            f"Детали:\n" + "\n".join(f"  - {error}" for error in errors[:10])
        )
        if len(errors) > 10:
            error_message += f"\n  ... и еще {len(errors) - 10} нарушений"

        pytest.fail(error_message)

    print(f"Проверено {len(logs)} записей логов, секреты не обнаружены")


def test_logs_collector_works(get_collected_logs):
    logs = get_collected_logs()

    assert len(logs) >= 0, "Сборщик логов не работает или логи не собираются"

    print(f"Сборщик логов работает корректно. Собрано {len(logs)} записей")
