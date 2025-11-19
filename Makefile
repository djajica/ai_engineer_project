POETRY ?= poetry
DOCKER_COMPOSE ?= docker compose

.PHONY: install fmt lint unit integration test run api lock help
.PHONY: docker-build docker-up docker-down

install:
	$(POETRY) install

lock:
	$(POETRY) lock

fmt:
	$(POETRY) run ruff check app app/tests --select I --fix

lint:
	$(POETRY) run ruff check app app/tests
	$(POETRY) run mypy app
	test -f pyproject.toml && $(POETRY) run python -m compileall app

unit:
	$(POETRY) run pytest app/tests/unit

integration:
	$(POETRY) run pytest app/tests/integration

test:
	$(POETRY) run pytest

run:
	$(POETRY) run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

api:
	curl -s http://localhost:8000/docs

docker-build:
	$(DOCKER_COMPOSE) build

docker-up:
	$(DOCKER_COMPOSE) up

docker-down:
	$(DOCKER_COMPOSE) down

help:
	@echo "Available targets:"
	@echo "  make install      # poetry install project dependencies"
	@echo "  make lock         # refresh poetry.lock"
	@echo "  make fmt          # auto-format imports via Ruff"
	@echo "  make lint         # Ruff + mypy + bytecode compilation"
	@echo "  make unit         # run unit tests"
	@echo "  make integration  # run integration tests"
	@echo "  make test         # run full pytest suite"
	@echo "  make run          # start FastAPI dev server with uvicorn"
	@echo "  make api          # curl OpenAPI docs endpoint"
	@echo "  make docker-build # build Docker images via compose"
	@echo "  make docker-up    # start services with docker compose up"
	@echo "  make docker-down  # stop services with docker compose down"