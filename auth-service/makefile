run:
	fastapi dev src/main.py

init:
	@docker compose exec fastapi alembic revision --autogenerate -m "init"

migrate:
	@docker compose exec fastapi alembic upgrade head

roles-init:
	@docker compose exec fastapi python -m cli listroles