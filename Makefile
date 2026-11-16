.PHONY: install up down logs test lint fmt

install:
	pip install -e "./nlp[dev]" -e "./api[dev]"
	cd web && npm ci

up:
	docker compose up --build -d

down:
	docker compose down

logs:
	docker compose logs -f

test:
	pytest nlp/tests
	pytest api/tests
	cd web && npm test --if-present

lint:
	ruff check nlp api
	cd web && npm run lint

fmt:
	ruff format nlp api