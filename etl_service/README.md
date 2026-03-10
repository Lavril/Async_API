## ETL Service (PostgreSQL → Elasticsearch)

Сервис `etl_service` переносит данные из PostgreSQL в Elasticsearch (пакетная загрузка с хранением состояния).

---

## Запуск через Docker Compose (рекомендуется)

ETL поднимается **из корня репозитория** вместе с `theatre-db` и `elasticsearch`:

```bash
cd ..
cp .env.example .env
docker compose up --build
```

ETL запускается в контейнере командой `python /opt/app/main.py` и работает в цикле (периодичность задаётся настройками).

---

## Что важно

- Для корректной работы нужны доступные:
  - PostgreSQL (`theatre-db`),
  - Elasticsearch.
- Перед первым запуском обычно инициализируется БД дампом `database_dump.sql` (подключён в compose в корне).

