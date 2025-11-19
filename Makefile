POETRY ?= poetry
DOCKER_COMPOSE ?= docker compose

.PHONY: install run api lock help
.PHONY: docker-build docker-up docker-down

install:
	$(POETRY) install

lock:
	$(POETRY) lock
run:
	$(POETRY) run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

api:
	curl -s http://localhost:8000/docs

docker-build:
	$(DOCKER_COMPOSE) build

docker-up:
	$(DOCKER_COMPOSE) up

docker-up-d:
	$(DOCKER_COMPOSE) up -d

docker-down:
	$(DOCKER_COMPOSE) down

help:
	@echo "Available targets:"
	@echo "  make install      # poetry install project dependencies"
	@echo "  make lock         # refresh poetry.lock"
	@echo "  make run          # start FastAPI dev server with uvicorn"
	@echo "  make api          # curl OpenAPI docs endpoint"
	@echo "  make docker-build # build Docker images via compose"
	@echo "  make docker-up    # start services with docker compose up"
	@echo "  make docker-down  # stop services with docker compose down"