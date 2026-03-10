## FastAPI (публичное API каталога)

Сервис `fast_api` — публичное API «онлайн‑кинотеатра» для получения информации о:
- кинопроизведениях (films),
- жанрах (genres),
- персонах (persons).

Документация FastAPI:
- Swagger UI: `http://localhost/api/openapi`
- ReDoc: `http://localhost/api/redoc`
- OpenAPI JSON: `http://localhost/api/openapi.json`

---

## Запуск через Docker Compose (рекомендуется)

Этот сервис поднимается **из корня репозитория** вместе с инфраструктурой:

```bash
cd ..
cp .env.example .env
docker compose up --build
```

---

## Локальный запуск без Docker

Из корня репозитория доступна команда:

```bash
make run
```

Она запускает dev‑сервер FastAPI из `fast_api/main.py`.

