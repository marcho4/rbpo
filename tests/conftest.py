# tests/conftest.py

import logging

import pytest
from dotenv import load_dotenv
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.database import Base, get_db
from app.main import app

load_dotenv()

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


# Список для хранения всех логов из тестов
collected_logs = []


class LogCollectorHandler(logging.Handler):
    """Хэндлер для сбора всех логов во время выполнения тестов."""

    def emit(self, record):
        log_entry = self.format(record)
        collected_logs.append(log_entry)


@pytest.fixture(scope="session", autouse=True)
def setup_log_collector():
    """Фикстура для настройки сборщика логов на весь сеанс тестирования."""
    # Настраиваем логгер для приложения
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    # Создаем и добавляем наш хэндлер
    handler = LogCollectorHandler()
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    yield

    # После завершения всех тестов, хэндлер остается и мы можем получить логи
    logger.removeHandler(handler)


@pytest.fixture(scope="function")
def client():
    Base.metadata.create_all(bind=engine)
    yield TestClient(app)
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="session")
def get_collected_logs():
    """Фикстура для получения всех собранных логов."""

    def _get_logs():
        return collected_logs.copy()

    return _get_logs
