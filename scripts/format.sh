#!/bin/bash

echo "🎨 Formatting code..."

# Activate virtual environment
source venv/bin/activate

echo "Running Black..."
black app/ tests/

echo "Running isort..."
isort app/ tests/

echo "✅ Code formatting complete!"