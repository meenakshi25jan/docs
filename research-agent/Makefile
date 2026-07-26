# Research Agent - Makefile (Linux/macOS)
# Run 'make help' to see all commands

.PHONY: help setup test serve docker-up docker-down health backup clean

help:
	@echo "Research Agent - Available Commands"
	@echo "===================================="
	@echo "  make setup      Install dependencies and run tests"
	@echo "  make test       Run unit tests"
	@echo "  make serve      Start API server on port 8000"
	@echo "  make docker-up  Start with Docker Compose"
	@echo "  make docker-down Stop Docker containers"
	@echo "  make health     Check API health"
	@echo "  make backup     Backup database and reports"
	@echo "  make clean      Remove cache and temp files"

setup:
	chmod +x scripts/*.sh
	./scripts/setup-linux.sh

test:
	. .venv/bin/activate && pytest -v

serve:
	./scripts/start-api.sh

docker-up:
	docker compose up --build -d
	@echo "API running at http://localhost:8000"

docker-down:
	docker compose down

health:
	./scripts/health-check.sh

backup:
	./scripts/backup-data.sh

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	@echo "Cache cleaned"
