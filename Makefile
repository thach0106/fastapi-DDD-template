.PHONY: test lint format check clean install migrate dev ci

install:
	poetry install
	poetry run pre-commit install

test:
	poetry run pytest

lint:
	poetry run ruff check src
	poetry run mypy src
	poetry run black --check src

format:
	poetry run ruff check --fix src
	poetry run black src

check: lint test

migrate:
	poetry run alembic upgrade head

dev:
	poetry run uvicorn src.main:app --reload

ci: check

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf .ruff_cache
