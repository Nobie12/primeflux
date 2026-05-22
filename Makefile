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