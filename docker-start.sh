#!/bin/bash
# Quick start script for Docker setup

echo "🚀 Starting Kouekam Portfolio with Docker..."

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating from .env.example..."
    if [ -f .env.example ]; then
        cp .env.example .env
        echo "✅ Created .env file. Please edit it with your configuration."
        echo "   At minimum, set SECRET_KEY to a random string."
        read -p "Press Enter to continue after editing .env, or Ctrl+C to exit..."
    else
        echo "❌ .env.example not found. Please create .env manually."
        exit 1
    fi
fi

# Build and start
echo "🔨 Building and starting containers..."
docker-compose up --build -d

echo "✅ Services started!"
echo ""
echo "📋 Container status:"
docker-compose ps
echo ""
echo "📝 View logs with: docker-compose logs -f"
echo "🌐 Access application at: http://localhost:8000"
echo "🛑 Stop services with: docker-compose down"






