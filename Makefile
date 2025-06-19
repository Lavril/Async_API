help:
	@cat Makefile

install:
	@pip install -r requirements.txt

lint:
	@flake8

run:
	@fastapi dev fast_api/main.py

clean:
	@rm -rf .pytest_cache/ .mypy_cache/ junit/ build/ dist/
	@find . -not -path './.venv*' -path '*/__pycache__*' -delete
	@find . -not -path './.venv*' -path '*/*.egg-info*' -delete

pre-commit-install:
	@pre-commit install

test-space:
	@docker-compose -f docker-compose.test.yml up --build

docker:
	@docker compose up --build

docker-api:
	@docker compose build fastapi

tests:
	@docker-compose -f docker-compose.test.yml up tests --build

tests-restart:
	@docker-compose -f docker-compose.test.yml restart tests
