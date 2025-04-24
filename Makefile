help:
	@cat Makefile

install:
	@pip install -r requirements.txt

lint:
	@flake8

run:
	@fastapi dev main.py

clean:
	@rm -rf .pytest_cache/ .mypy_cache/ junit/ build/ dist/
	@find . -not -path './.venv*' -path '*/__pycache__*' -delete
	@find . -not -path './.venv*' -path '*/*.egg-info*' -delete

pre-commit-install:
	@pre-commit install