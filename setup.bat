@echo off
REM Setup script for DevOps Automation SaaS (Windows)

setlocal enabledelayedexpansion

echo.
echo 🚀 Setting up DevOps Automation SaaS Platform...
echo.

REM Create virtual environment
if not exist "venv" (
    echo 📦 Creating Python virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install dependencies
echo 📥 Installing dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt

REM Create .env file if it doesn't exist
if not exist ".env" (
    echo 📝 Creating .env file...
    copy .env.example .env
    echo ⚠️  Update .env with your configuration before running
)

REM Start Docker services
echo 🐳 Starting Docker services...
docker-compose up -d postgres redis

REM Wait for database
echo ⏳ Waiting for database...
timeout /t 5 /nobreak

echo.
echo ✅ Setup complete!
echo.
echo 📖 Next steps:
echo 1. Update .env with your GitHub OAuth credentials
echo 2. Update .env with your AWS credentials
echo 3. Run: docker-compose up -d
echo 4. Run: uvicorn control_plane.main:app --reload
echo.
echo 🌐 API will be available at: http://localhost:8000
echo 📊 Prometheus: http://localhost:9090
echo 📈 Grafana: http://localhost:3001
echo 🔍 Kibana: http://localhost:5601
echo.
