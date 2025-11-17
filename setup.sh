#!/bin/bash
# Setup script for DevOps Automation SaaS

set -e

echo "🚀 Setting up DevOps Automation SaaS Platform..."

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "📦 Creating Python virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file..."
    cp .env.example .env
    echo "⚠️  Update .env with your configuration before running"
fi

# Initialize database
echo "🗄️  Setting up database..."
docker-compose up -d postgres redis

# Wait for database to be ready
echo "⏳ Waiting for database..."
sleep 5

# Run migrations
echo "🔄 Running database migrations..."
python -c "
import asyncio
from control_plane.database.migrations import create_database, run_migrations, seed_database

async def setup():
    dsn = 'postgresql://postgres:postgres@localhost:5432/cloud_deploy'
    await create_database(dsn)
    await run_migrations(dsn)
    await seed_database(dsn)

asyncio.run(setup())
"

echo "✅ Setup complete!"
echo ""
echo "📖 Next steps:"
echo "1. Update .env with your GitHub OAuth credentials"
echo "2. Update .env with your AWS credentials"
echo "3. Run: docker-compose up -d"
echo "4. Run: uvicorn control_plane.main:app --reload"
echo ""
echo "🌐 API will be available at: http://localhost:8000"
echo "📊 Prometheus: http://localhost:9090"
echo "📈 Grafana: http://localhost:3001"
echo "🔍 Kibana: http://localhost:5601"
