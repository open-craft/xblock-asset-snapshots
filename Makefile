.DEFAULT_GOAL := help

.PHONY: help format quality upgrade

help:
	@perl -nle'print $& if m{^[\.a-zA-Z_-]+:.*?## .*$$}' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m  %-25s\033[0m %s\n", $$1, $$2}'

quality.python:
	uv run ruff check .
	uv run ruff format . --check
    mypy .

quality.js:
	pnpm run lint

quality: quality.python quality.js

format:
	uv run ruff check --fix .
	uv run ruff format .

upgrade:
	uv lock --upgrade
	pnpm upgrade

