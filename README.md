## Async API (микросервисы кинотеатра)

Репозиторий содержит несколько сервисов для учебного проекта «онлайн‑кинотеатр»:

- **`fast_api/`** — публичное API для каталога (FastAPI).
- **`etl_service/`** — ETL, который забирает данные из Postgres и грузит в Elasticsearch.
- **`movies_admin/`** — админка (Django + uWSGI), отдаёт статику через nginx.
- **`auth-service/`** — отдельный сервис аутентификации/авторизации (FastAPI + Postgres + Redis). Поднимается *отдельным* `docker-compose.yaml` внутри `auth-service`.

Если вам нужно запускать только один подпроект — смотрите README внутри папки сервиса.

---

## Быстрый старт (основной стек: API + админка + ETL)

### 1) Подготовить окружение

В корне проекта создайте файл `.env` на основе шаблона:

```bash
cp .env.example .env
```

Откорректируйте значения (порты, хосты и т.д.). Эти переменные используются в `docker-compose.yml` и сервисами.

### 2) Запуск через Docker Compose

Из корня репозитория:

```bash
docker compose up --build
```

В `docker-compose.yml` поднимаются:
- `fastapi` (публичное API, порт 8000),
- `movies-admin` (админка),
- `etl` (ETL сервис),
- инфраструктура: `theatre-db` (PostgreSQL), `elasticsearch`, `redis`, `nginx`.

Остановка:

```bash
docker compose down
```

---

## Локальный запуск FastAPI (без Docker)

В корне есть `Makefile` с командой:

```bash
make run
```

Она запускает dev‑сервер FastAPI из `fast_api/main.py` (используется `fastapi dev ...`).

---

## Запуск тестов

Тесты запускаются отдельным compose‑файлом:

```bash
docker compose -f docker-compose.test.yml up --build
```

### Если нужно тестировать тот же образ

Сначала соберите образ API:

```bash
docker compose build fastapi
```

Затем можно перезапускать тестовый контейнер (без пересборки остальных сервисов).

Важно: `docker-compose.test.yml` ожидает переменные окружения из `./.env.test`.  
Если у вас нет `.env.test`, создайте его на основе `.env.example` и задайте тестовые значения.

---

## Документация по подпроектам

- **Auth Service**: `auth-service/README.md`
- **FastAPI (публичное API)**: `fast_api/README.md`
- **ETL сервис**: `etl_service/README.md`
- **Movies Admin (Django)**: `movies_admin/README.md`