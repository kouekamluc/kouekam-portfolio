@echo off
REM Quick start script for Docker setup on Windows

echo 🚀 Starting Kouekam Portfolio with Docker...

REM Check if .env exists
if not exist .env (
    echo ⚠️  .env file not found. Creating from .env.example...
    if exist .env.example (
        copy .env.example .env
        echo ✅ Created .env file. Please edit it with your configuration.
        echo    At minimum, set SECRET_KEY to a random string.
        pause
    ) else (
        echo ❌ .env.example not found. Please create .env manually.
        exit /b 1
    )
)

REM Build and start
echo 🔨 Building and starting containers...
docker-compose up --build -d

echo ✅ Services started!
echo.
echo 📋 Container status:
docker-compose ps
echo.
echo 📝 View logs with: docker-compose logs -f
echo 🌐 Access application at: http://localhost:8000
echo 🛑 Stop services with: docker-compose down

pause






