.PHONY: sync
sync:
	uv sync

.PHONY: migrate
migrate:
	uv run python -m core.manage migrate

.PHONY: migrations
migrations:
	uv run python -m core.manage makemigrations

.PHONY: run-server
run-server:
	uv run python -m core.manage runserver

.PHONY: superuser
superuser:
	uv run python -m core.manage createsuperuser

.PHONY: update
update: sync migrate;

.PHONY: lint
lint:
	uv run ruff check .

.PHONY: lint-fix
lint-fix:
	uv run ruff check . --fix

.PHONY: format-fix
format-fix:
	uv run ruff format .

.PHONY: typecheck
typecheck:
	uv run mypy .

.PHONY: typecheck-strict
typecheck-strict:
	uv run mypy . --strict

.PHONY: check
check:
	make lint && make format-check && make typecheck