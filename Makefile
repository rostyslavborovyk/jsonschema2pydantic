.PHONY: lint
lint:
	uv run black src
	uv run ruff check --fix src

.PHONY: test
test:
	pytest . --cov src --cov-report term
