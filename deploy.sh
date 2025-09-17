#!/bin/bash

# Zynx AGI Core Foundation - Deployment Script
# Single-run script to build containers, run migrations, and smoke tests

set -e  # Exit on any error

echo "🚀 Zynx AGI Core Foundation - Deployment Script"
echo "================================================"

# Check if .env exists, if not copy from example
if [ ! -f .env ]; then
    echo "📋 Creating .env file from .env.example..."
    echo "⚠️  Please edit .env with your configuration before continuing!"
    cp .env.example .env
    echo "✅ .env file created. Please review and update the configuration."
    read -p "Press Enter to continue after editing .env, or Ctrl+C to exit..."
fi

echo "🔧 Building containers..."
make build

echo "🚦 Starting services..."
make up

echo "⏳ Waiting for services to be ready..."
sleep 15

echo "🗄️  Running database migrations..."
make migrate

echo "🏥 Running health checks..."
echo "Testing web service health..."
curl -f http://localhost:8000/health || echo "❌ Web service health check failed"

echo "Testing LLM proxy ping..."
curl -f http://localhost:8000/api/v1/llm/ping || echo "❌ LLM service health check failed"

echo "📊 Service status:"
make status

echo ""
echo "✅ Deployment completed!"
echo ""
echo "🌐 Application URLs:"
echo "   - Main App:       http://localhost:8000"
echo "   - API Docs:       http://localhost:8000/docs"
echo "   - MinIO Console:  http://localhost:9001"
echo "   - PostgreSQL:     localhost:5432"
echo ""
echo "🔑 Default Credentials:"
echo "   - MinIO:          minioadmin / minioadmin"
echo "   - PostgreSQL:     zynxuser / zynxpass"
echo ""
echo "📝 Next Steps:"
echo "   1. Configure your API keys in .env"
echo "   2. Test LLM endpoints: curl http://localhost:8000/api/v1/llm/models"
echo "   3. Create users: curl -X POST http://localhost:8000/api/v1/users/"
echo ""
echo "📚 Commands:"
echo "   - View logs:      make logs"
echo "   - Stop services:  make down"
echo "   - Full cleanup:   make clean"