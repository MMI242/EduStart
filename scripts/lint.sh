#!/bin/bash

echo "🔍 Running code quality checks..."

# Activate virtual environment
source venv/bin/activate

echo "Running Black..."
black app/ tests/ --check

echo "Running isort..."
isort app/ tests/ --check-only

echo "Running flake8..."
flake8 app/ tests/

echo "Running mypy..."
mypy app/

echo "✅ Code quality checks complete!"