# EduStart
![Logo](ui/public/logo.png)

[![npm test](https://github.com/MMI242/EduStart/actions/workflows/node.js.yml/badge.svg?branch=main)](https://github.com/MMI242/EduStart/actions/workflows/node.js.yml)
[![pytest](https://github.com/MMI242/EduStart/actions/workflows/python.yml/badge.svg?branch=main)](https://github.com/MMI242/EduStart/actions/workflows/python.yml)
[![Deploy UI to GitHub Pages](https://github.com/MMI242/EduStart/actions/workflows/deploy-pages.yml/badge.svg)](https://github.com/MMI242/EduStart/actions/workflows/deploy-pages.yml)

Educational platform for interactive learning.

## Prerequisites

- Python 3.11+
- Node.js 18+
- Docker & Docker Compose (optional)

## Quick Start

```bash
# View all available commands
make help

# Setup development environment (creates venv, installs dependencies)
make setup
```

## Local Development

### Backend Only

```bash
# Install dependencies
make install

# Run backend dev server (http://localhost:8000)
make dev
```

### Frontend Only

```bash
# Install frontend dependencies
make ui-install

# Run frontend dev server (http://localhost:5173)
make ui-dev

# Build for production
make ui-build
```

### Full Stack Development

```bash
# Run both backend and frontend dev servers concurrently
make dev-all
```

## Code Quality

```bash
# Run linting checks
make lint

# Format code
make format

# Run tests
make test
```

## Docker

```bash
# Build Docker images
make docker-build

# Start containers
make docker-up

# Stop containers
make docker-down

# View logs
docker-compose logs -f
```

## Cleanup

```bash
# Remove temp files, caches, and build artifacts
make clean
```

## Deployment

```bash
make deploy
```
