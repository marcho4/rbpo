# SecDev Course Template

Стартовый шаблон для студенческого репозитория (HSE SecDev 2025).

## Быстрый старт
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt -r requirements-dev.txt
pre-commit install
uvicorn app.main:app --reload
```

## Ритуал перед PR
```bash
ruff check --fix .
black .
isort .
pytest -q
pre-commit run --all-files
```

## Тесты
```bash
pytest -q
```

## CI
В репозитории настроен workflow **CI** (GitHub Actions) — required check для `main`.
Badge добавится автоматически после загрузки шаблона в GitHub.

## Контейнеры
```bash
docker build -t secdev-app .
docker run --rm -p 8000:8000 secdev-app
# или
docker compose up --build
```

## Эндпойнты
- `GET /health` → `{"status": "ok"}`
- `POST /register` — регистрация нового пользователя
- `POST /token` — аутентификация пользователя и получение JWT токена

### Компании (`/companies`)
- `POST /` — создать новую компанию
- `GET /` — получить список компаний
- `GET /{company_id}` — получить компанию по ID
- `PUT /{company_id}` — обновить компанию по ID
- `DELETE /{company_id}` — удалить компанию по ID

### Лиды (`/leads`)
- `POST /` — создать новый лид
- `GET /?status=` — получить список лидов (с возможностью фильтрации по статусу)
- `GET /{lead_id}` — получить лид по ID
- `PUT /{lead_id}` — обновить лид по ID
- `DELETE /{lead_id}` — удалить лид по ID

Возможные статусы для лидов: `new`, `qualified`, `proposal`, `won`, `lost`.

## Формат ошибок
Все ошибки — JSON-обёртка:
```json
{
  "error": {"code": "not_found", "message": "item not found"}
}
```

См. также: `SECURITY.md`, `.pre-commit-config.yaml`, `.github/workflows/ci.yml`.
