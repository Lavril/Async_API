## Auth-service (JWT аутентификация и роли)

Auth‑service — это отдельный микросервис аутентификации и авторизации на базе **FastAPI**, **PostgreSQL** и **Redis**.  
Сервис отвечает за:

- **регистрацию и аутентификацию пользователей** (JWT access/refresh токены),
- **хранение истории логинов**,
- **ролевую модель и права доступа** (битовые маски),
- **управление типами ролей и назначением ролей пользователям**.

HTTP‑API документировано через встроенную документацию FastAPI:

- Swagger UI: `http://localhost/api/openapi`
- ReDoc: `http://localhost/api/redoc`

Маршруты сервиса:

- `users` — операции с пользователем и его ролями,
- `roles` — справочник типов ролей и их прав.

---

## Стек

- **Язык**: Python 3.12
- **Web‑фреймворк**: FastAPI
- **БД**: PostgreSQL
- **Кэш/хранилище токенов**: Redis
- **ORM**: SQLAlchemy (async)
- **JWT**: `async-fastapi-jwt-auth`
- **HTTP‑сервер**: Uvicorn
- **Reverse‑proxy**: Nginx (в Docker‑компоузе)

---

## Структура проекта (упрощённо)

- `src/main.py` — точка входа FastAPI‑приложения, конфигурация CORS, OpenAPI, lifespan (инициализация БД и дефолтных ролей).
- `src/routes/users.py` — маршруты для регистрации, логина, смены логина/пароля, работы с ролями пользователя, проверки прав.
- `src/routes/role_types.py` — CRUD по типам ролей, получение доступных прав и иерархии.
- `src/services/auth.py` — бизнес‑логика аутентификации, выдачи/обновления/отзыва токенов, история логинов.
- `src/services/role_service.py` — бизнес‑логика по типам ролей и назначению ролей пользователям.
- `src/services/permission_service.py` — проверки прав, иерархии ролей, расшифровка битовых масок.
- `src/db/postgres.py` — подключение к PostgreSQL, `async_session`, `Base`.
- `src/db/redis_db.py` — функции работы с Redis (хранение/отзыв refresh/access‑токенов).
- `src/db/repository.py` — репозитории пользователей и истории логинов.
- `src/db/role_repository.py` — репозитории типов ролей и связей пользователь‑роль.
- `src/models/entity.py` — SQLAlchemy‑модели `User`, `RoleType`, `Role`, `History`.
- `src/schemas/entity.py` — Pydantic‑схемы пользователей, ролей, прав.
- `src/schemas/token.py` — схема ответа с токенами.
- `src/constants/permissions.py` — перечисление прав (`RolePermissions`) и приоритетов (`RolePriority`, `InitialRoles`).

---

## Переменные окружения

Все переменные перечислены в `.env.template`. Для локальной разработки создайте `.env`:

```bash
cp .env.template .env
```

Ключевые параметры:

- **Общие/проект:**
  - `PROJECT_NAME` — имя проекта (используется в заголовках/документации).
  - `PROJECT_DESCRIPTION` — описание проекта.
- **PostgreSQL:**
  - `POSTGRES_USER` — пользователь БД.
  - `POSTGRES_PASSWORD` — пароль пользователя БД.
  - `POSTGRES_DB` — имя БД.
  - `POSTGRES_HOST` — хост БД (в Docker‑компоузе: `auth-db`).
  - `POSTGRES_PORT` — порт БД (по умолчанию `5432`).
- **Redis:**
  - `REDIS_HOST` — хост Redis (в Docker‑компоузе: `redis`).
  - `REDIS_PORT` — порт Redis (по умолчанию `6379`).

При необходимости добавьте сюда параметры JWT (секрет, времена жизни токенов и т.п.), если они используются в `core/config.py` и настройке `AuthJWT`.

---

## Локальный запуск через Docker Compose

### Предварительные шаги

1. Установите **Docker** и **Docker Compose**.
2. В корне `auth-service` создайте файл окружения:

```bash
cp .env.template .env
```

При необходимости отредактируйте значения (логины/пароли БД и т.д.).

### Запуск

Из каталога `auth-service` выполните:

```bash
docker compose up --build
```

Будут подняты сервисы:

- `fastapi` — само приложение `auth-service` (порт `8000` внутри контейнера),
- `auth-db` — PostgreSQL,
- `redis` — Redis,
- `nginx` — reverse‑proxy, который пробрасывает HTTP на FastAPI.

После успешного старта:

- API будет доступен по адресу `http://localhost`,
- документация Swagger — `http://localhost/api/openapi`,
- документация ReDoc — `http://localhost/api/redoc`.

Остановка сервисов:

```bash
docker compose down
```

При необходимости удалить тома (данные БД и Redis):

```bash
docker compose down -v
```

---

## Локальный запуск без Docker

Если у вас установлен Python 3.12 и локально доступны PostgreSQL и Redis:

1. Активируйте виртуальное окружение (пример для `venv`):

```bash
python -m venv venv
source venv/bin/activate
```

1. Установите зависимости:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

1. Настройте `.env` (аналогично Docker‑варианту), но:
  - `POSTGRES_HOST` укажите как `localhost` (или адрес вашей БД),
  - `REDIS_HOST` укажите как `localhost` (или адрес вашего Redis).
2. Запустите приложение:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

API будет доступно по адресу `http://localhost:8000`, документация:

- Swagger UI: `http://localhost:8000/api/openapi`
- ReDoc: `http://localhost:8000/api/redoc`

---

## Основные сущности и модель прав

### Сущности

- `User` — пользователь с полями:
  - `id`, `login`, `email`, `password`, `first_name`, `last_name`, `created_at`,
  - связи: `roles` (список назначенных ролей), `history` (история логинов).
- `RoleType` — тип роли:
  - `name` — системное имя роли (строчные буквы и подчёркивания),
  - `description` — описание,
  - `permissions` — битовая маска прав,
  - `priority` — приоритет в иерархии (чем выше число, тем «сильнее» роль),
  - `created_at`.
- `Role` — связь пользователь ↔ тип роли:
  - `user_id`, `role_type_id`, `assigned_at`.
- `History` — запись об успешном входе:
  - `user_id`, `user_agent`, `login_info`, `created_at`.

### Права и приоритеты

В `constants/permissions.py` определены:

- `RolePermissions` — отдельные флаги прав (например, `CREATE_ROLES`, `EDIT_ROLES`, `ASSIGN_ROLES`, `DELETE_ROLES`, `VIEW_PERMISSIONS`, `MANAGE_PERMISSIONS` и др.), которые комбинируются побитовыми операциями.
- `RolePriority` — приоритеты ролей и правила, можно ли назначать/изменять роли с тем или иным приоритетом (`can_assign_role`).
- `InitialRoles` — базовые роли, которые инициализируются при старте приложения (`initialize_default_roles` в `RoleService`/`lifespan`).

### Список ролей (InitialRoles)

Начальные роли, создаваемые автоматически:

- **`user`**
  - **Описание**: Обычный пользователь.
  - **Права**: нет (0).
  - **Приоритет**: `RolePriority.USER` (1).

- **`subscriber`**
  - **Описание**: Подписчик с доступом к премиум‑функциям.
  - **Права**: нет (0).
  - **Приоритет**: `RolePriority.SUBSCRIBER` (2).

- **`admin`**
  - **Описание**: Администратор — управление ролями и пользователями.
  - **Права**:
    - `EDIT_ROLES` — редактировать существующие роли,
    - `ASSIGN_ROLES` — назначать роли пользователям,
    - `VIEW_PERMISSIONS` — просматривать права ролей.
  - **Приоритет**: `RolePriority.ADMIN` (5).

- **`superuser`**
  - **Описание**: Суперпользователь — полный доступ ко всем функциям.
  - **Права**: все права (`RolePermissions.get_all_permissions()`):
    - `CREATE_ROLES` — создавать новые роли,
    - `EDIT_ROLES` — редактировать роли,
    - `ASSIGN_ROLES` — назначать роли пользователям,
    - `DELETE_ROLES` — удалять роли,
    - `VIEW_PERMISSIONS` — просматривать права ролей,
    - `MANAGE_PERMISSIONS` — управлять правами.
  - **Приоритет**: `RolePriority.SUPERUSER` (10).

### Список прав (RolePermissions)

Битовые флаги прав доступа:

- **`CREATE_ROLES`** (`1 << 0` = **1**) — создавать новые роли.
- **`EDIT_ROLES`** (`1 << 1` = **2**) — редактировать существующие роли.
- **`ASSIGN_ROLES`** (`1 << 2` = **4**) — назначать роли пользователям.
- **`DELETE_ROLES`** (`1 << 3` = **8**) — удалять роли.
- **`VIEW_PERMISSIONS`** (`1 << 4` = **16**) — просматривать права ролей.
- **`MANAGE_PERMISSIONS`** (`1 << 5` = **32**) — управлять правами (высокоуровневое администрирование).

Дополнительно:

- **Базовые права** (`RolePermissions.get_basic_permissions()`): `CREATE_ROLES | EDIT_ROLES | ASSIGN_ROLES`.
- **Все права** (`RolePermissions.get_all_permissions()`): комбинация всех флагов выше.

Комбинирование прав пользователя происходит через все его роли:

- суммарная маска прав определяется побитовым `OR` всех `role_type.permissions`,
- `highest_role_priority` — максимальный приоритет среди всех ролей пользователя.

---

## Основные эндпоинты

Ниже краткое описание ключевых маршрутов (подробности и точные схемы запросов/ответов смотрите в Swagger‑документации).

### Пользователи (`/users`)

- **POST `/users/signup`**  
Регистрация пользователя.  
Тело запроса: `UserCreate` (логин, email, пароль, имя/фамилия, опционально `role_name`).  
Возвращает данные пользователя с его первичной ролью и списком ролей.
- **POST `/users/login`**  
Аутентификация по логину/паролю.  
Тело: `LoginSchema`.  
Ответ: `TokenResponse` (access + refresh JWT).  
В claims токена включаются:
  - `user_id`, `roles`, `permissions`, `highest_role_priority`, `primary_role`, `email`.
- **POST `/users/refresh`**  
Обновление access‑токена по refresh‑токену (JWT в заголовке).  
Возвращает новый `TokenResponse`.
- **POST `/users/logout`**  
Отзыв текущего access‑ и (по возможности) refresh‑токена (через Redis).
- **POST `/users/change-login`**  
Смена логина текущего пользователя (требуется валидный access‑токен).
- **POST `/users/change-password`**  
Смена пароля текущего пользователя (требуется валидный access‑токен и текущий пароль).
- **GET `/users/login-history`**  
История логинов текущего пользователя (лимит/offset через query‑параметры).

#### Роли пользователя и права

- **POST `/users/roles/assign`**  
Назначить роль пользователю. Требует JWT и соответствующие права.  
Тело: `UserRoleAssign` (`user_id`, `role_name`).  
Проверки:
  - право `ASSIGN_ROLES`,
  - иерархия ролей (`RolePriority`).
- **DELETE `/users/roles/remove/{user_id}/{role_name}`**  
Удалить роль у пользователя (аналогичные проверки прав и иерархии).
- **GET `/users/permissions/{user_id}`**  
Получить детальную информацию по ролям и правам пользователя (`UserPermissionsInfo`).  
Если вызывающий не имеет права `VIEW_PERMISSIONS`, он может запрашивать только свои собственные права.
- **POST `/users/permissions/check`**  
Проверка, есть ли у пользователя конкретное право.  
Тело: `PermissionCheckRequest` (`user_id`, `permission` — строковый ключ).  
Ответ: `PermissionCheckResponse` (`has_permission`, список названий прав пользователя).
- **POST `/users/hierarchy/check`**  
Проверка, может ли пользователь назначить конкретную роль (с учётом иерархии и прав).
- **GET `/users/roles`**  
Получить все связи пользователь‑роль (только для администраторов с правом `MANAGE_PERMISSIONS`).
- **DELETE `/users/roles/{user_id}`**  
Очистить все роли пользователя (также требует `MANAGE_PERMISSIONS`).

### Типы ролей (`/roles`)

- **POST `/roles/`**  
Создать новый тип роли (`RoleTypeCreate`).  
Требует право `CREATE_ROLES` и корректный приоритет (нельзя создать роль с приоритетом не ниже своего).
- **GET `/roles/`**  
Список всех типов ролей (`List[RoleTypeInDB]`).  
Требует право `VIEW_PERMISSIONS`.
- **GET `/roles/{role_name}`**  
Получить конкретный тип роли по имени.
- **PUT `/roles/{role_id}`**  
Обновить тип роли (`RoleTypeUpdate`).  
Требует право `EDIT_ROLES` и соблюдение иерархии приоритетов.
- **DELETE `/roles/{role_id}`**  
Удалить тип роли.  
Нельзя удалять системные роли (`user`, `superuser` и т.п.). Требует `DELETE_ROLES`.
- **POST `/roles/initialize`**  
Инициализировать дефолтные роли из `InitialRoles`.  
Требует `CREATE_ROLES`.  
На старте приложения эта логика уже вызывается в `lifespan`, так что эндпоинт нужен в основном для ручного восстановления.
- **GET `/roles/permissions/available`**  
Список всех доступных прав и их битовых значений.
- **GET `/roles/hierarchy/levels`**  
Карта приоритетов ролей.

---

## Обработка JWT‑ошибок

В `main.py` настроены обработчики исключений из `async_fastapi_jwt_auth`:

- `RevokedTokenError`,
- `MissingTokenError`,
- `RefreshTokenRequired`,
- `AccessTokenRequired`.

Все они возвращают ответы со статусом `401` и понятными сообщениями в поле `detail`.

---

## Консольные команды

1. Создание суперпользователя

```bash
docker compose exec fastapi python -m cli createsuperuser\
  --email admin@example.com \
  --password secret123 \
  --login secret123 \
  --first-name secret123 \
  --last-name secret123
```

1. Создание пользователя

```bash
docker compose exec fastapi python -m cli createuser\
  --email admin@example.com \
  --password secret123 \
  --login secret123 \
  --first-name secret123 \
  --last-name secret123 \
  --role user
```

1. Список ролей

```bash
docker compose exec fastapi python -m cli listroles
```

