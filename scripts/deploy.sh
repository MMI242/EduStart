#!/bin/bash

echo "🚀 Deploying EduStart Backend..."

# Check if environment is production
if [ "$ENVIRONMENT" != "production" ]; then
    echo "⚠️  Warning: Not in production environment"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Build Docker image
echo "🐳 Building Docker image..."
docker-compose -f docker-compose.prod.yml build

# Stop existing containers
echo "🛑 Stopping existing containers..."
docker-compose -f docker-compose.prod.yml down

# Start new containers
echo "▶️  Starting new containers..."
docker-compose -f docker-compose.prod.yml up -d

# Wait for services to be healthy
echo "⏳ Waiting for services to be healthy..."
sleep 10

# Check health
echo "🏥 Checking service health..."
curl -f http://localhost:8000/health || exit 1

echo "✅ Deployment complete!"
echo "📊 View logs: docker-compose -f docker-compose.prod.yml logs -f"