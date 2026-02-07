.PHONY: help setup install dev test lint format clean docker-build docker-up docker-down deploy ui-install ui-dev ui-build dev-all

help:
	@echo "EduStart - Available Commands:"
	@echo ""
	@echo "Backend:"
	@echo "  make setup        - Setup development environment"
	@echo "  make install      - Install Python dependencies"
	@echo "  make dev          - Run backend development server (port 8000)"
	@echo "  make test         - Run tests"
	@echo "  make lint         - Run code quality checks"
	@echo "  make format       - Format code"
	@echo "  make clean        - Clean temporary files"
	@echo ""
	@echo "Frontend:"
	@echo "  make ui-install   - Install frontend dependencies"
	@echo "  make ui-dev       - Run frontend dev server (port 5173)"
	@echo "  make ui-build     - Build frontend for production"
	@echo ""
	@echo "Combined:"
	@echo "  make dev-all      - Run both backend and frontend dev servers"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-build - Build Docker images"
	@echo "  make docker-up    - Start Docker containers"
	@echo "  make docker-down  - Stop Docker containers"
	@echo ""
	@echo "  make deploy       - Deploy to production"

setup:
	@bash scripts/setup_dev.sh

install:
	uv pip install -r requirements.txt
	uv pip install -r requirements-dev.txt

dev:
	./venv/bin/python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Frontend targets
ui-install:
	cd ui && npm install

ui-dev:
	cd ui && npm run dev

ui-build:
	cd ui && npm run build

# Run both backend and frontend dev servers
dev-all:
	@echo "Starting backend and frontend dev servers..."
	@echo "Backend: http://localhost:8000"
	@echo "Frontend: http://localhost:5173"
	@make -j2 dev ui-dev

test:
	@bash scripts/run_tests.sh

lint:
	@bash scripts/lint.sh

format:
	@bash scripts/format.sh

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.log" -delete
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .coverage
	rm -rf dist
	rm -rf build
	rm -rf *.egg-info
	rm -rf ui/dist
	rm -rf ui/node_modules

docker-build:
	docker-compose build

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f

deploy:
	@bash scripts/deploy.sh