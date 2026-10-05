.DEFAULT_GOAL := help

.PHONY: help format.python format.js quality.python quality.js

help:
	@perl -nle'print $& if m{^[\.a-zA-Z_-]+:.*?## .*$$}' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m  %-25s\033[0m %s\n", $$1, $$2}'

quality.python:
	uv run ruff check .
	uv run ruff format . --check
	uv run mypy .

quality.js:
	pnpm run lint

quality: quality.python quality.js

format.python:
	uv run ruff check --fix .
	uv run ruff format .

format.js:
	pnpm run lint:fix

format: format.js format.python

upgrade:
	uv lock --upgrade
	pnpm upgrade

