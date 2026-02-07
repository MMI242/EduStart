#!/bin/bash

echo "🧪 Running EduStart Backend Tests..."

# Activate virtual environment
source venv/bin/activate

# Run tests with coverage
pytest tests/ \
    --cov=app \
    --cov-report=html \
    --cov-report=term \
    --verbose \
    --color=yes

echo ""
echo "✅ Tests complete!"
echo "📊 Coverage report: htmlcov/index.html"