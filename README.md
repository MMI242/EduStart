# EduStart
![Logo](ui/public/logo.png)

[![CI Pipeline](https://github.com/MMI242/EduStart/actions/workflows/ci.yml/badge.svg)](https://github.com/MMI242/EduStart/actions/workflows/ci.yml)
[![CD Pipeline](https://github.com/MMI242/EduStart/actions/workflows/cd.yml/badge.svg)](https://github.com/MMI242/EduStart/actions/workflows/cd.yml)
[![Deploy UI to GitHub Pages](https://github.com/MMI242/EduStart/actions/workflows/deploy-pages.yml/badge.svg)](https://github.com/MMI242/EduStart/actions/workflows/deploy-pages.yml)

EduStart is an adaptive learning platform for children aged 4–10. It offers gamified reading, counting, and cognitive modules with AI-powered recommendations and real-time progress tracking. Parents manage child profiles and monitor learning, while educators create and curate learning content through a dedicated dashboard.

## Features

### Learning
- Interactive learning modules (reading, counting, cognitive)
- Multiple question types: multiple choice, drag & drop, audio guess, coloring, matching
- Adaptive difficulty powered by machine learning
- AI-driven module recommendations based on learner progress
- Offline module download support

### Parent & Educator
- Role-based access (parent and educator)
- Child profile management with multi-child support
- Progress reports and learning analytics
- Educator dashboard for creating, editing, and managing modules

### Platform
- Supabase-backed authentication with JWT
- REST API under `/api/v1` with automatic OpenAPI docs
- React SPA with client-side routing
- Docker Compose orchestration with nginx reverse proxy
- CI/CD via GitHub Actions (build, test, deploy to GitHub Pages)

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
