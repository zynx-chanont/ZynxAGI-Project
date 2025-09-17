# Zynx AGI Core Foundation - Runbook

This runbook provides quick 1-line commands to build, run, migrate, seed, and test the Zynx AGI Core Foundation.

## Quick Commands

### Build and Run
```bash
# Build all containers
make build

# Start all services
make up

# Build and start (combined)
make dev

# Stop services
make down
```

### Database Operations
```bash
# Run migrations
make migrate

# Create new migration
make migrate-create name="your_migration_name"

# Rollback last migration
make migrate-rollback

# Backup database
make backup-db
```

### Development
```bash
# View logs
make logs

# Open shell in web container
make shell

# Run tests
make test

# Check service status
make status

# Health check
make health
```

### One-Line Setup
```bash
# Complete setup: build + start + migrate
make dev
```

## Environment Setup

### Initial Setup
```bash
# 1. Copy environment template
cp .env.example .env

# 2. Edit configuration (update API keys, passwords)
nano .env

# 3. Deploy everything
./deploy.sh
```

### API Keys Configuration
Edit `.env` and add your API keys:
```bash
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here
```

## Testing Endpoints

### Health Checks
```bash
# Basic health check
curl http://localhost:8000/health

# LLM service ping
curl http://localhost:8000/api/v1/llm/ping

# Get available models
curl http://localhost:8000/api/v1/llm/models
```

### User Management
```bash
# Create a user
curl -X POST http://localhost:8000/api/v1/users/ \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"test@example.com","password":"testpass123"}'

# Get user by ID
curl http://localhost:8000/api/v1/users/1
```

### LLM Generation
```bash
# Test LLM generation (requires API key)
curl -X POST http://localhost:8000/api/v1/llm/generate \
  -H "Content-Type: application/json" \
  -d '{
    "provider": "openai",
    "model": "gpt-3.5-turbo",
    "messages": [{"role": "user", "content": "Hello, world!"}],
    "max_tokens": 100
  }'
```

### ZPDL Metadata
```bash
# Get metadata template
curl http://localhost:8000/metadata/template

# Hash an artifact
curl -X POST http://localhost:8000/artifact/hash \
  -H "Content-Type: application/json" \
  -d '{"content": "Sample content", "type": "test"}'
```

## Artifact Management

### Export Prompts
```bash
# Export OpenAI conversations
./export_prompts.sh conversations.json

# Direct Python usage
python export_prompts_parser.py input.json output_dir/
```

### Ingest Artifacts
```bash
# Ingest specific files
python ingest_artifacts.py file1.txt file2.json

# Ingest default foundation files
python ingest_artifacts.py
```

## GitHub Actions Setup

### Required Secrets
Set these secrets in your GitHub repository settings:

**For Social Media Dissemination:**
- `LINKEDIN_ACCESS_TOKEN` - LinkedIn API access token
- `LINKEDIN_USER_ID` - Your LinkedIn user ID
- `TWITTER_API_KEY` - Twitter API key
- `TWITTER_API_SECRET` - Twitter API secret
- `TWITTER_ACCESS_TOKEN` - Twitter access token
- `TWITTER_ACCESS_SECRET` - Twitter access secret

### Manual Workflow Trigger
The dissemination workflow is set to manual trigger (`workflow_dispatch`):

1. Go to GitHub Actions tab
2. Select "Disseminate IP Declaration" workflow
3. Click "Run workflow"
4. Choose platforms (LinkedIn, Twitter, or both)

## Troubleshooting

### Service Issues
```bash
# Check all service status
make status

# Restart services
make restart

# View detailed logs
make logs

# Clean and rebuild
make clean && make build && make up
```

### Database Issues
```bash
# Check database connection
docker-compose exec postgres psql -U zynxuser -d zynxagi -c "SELECT version();"

# Reset database (WARNING: destroys data)
make down
docker volume rm zynxagi-project_postgres_data
make up && make migrate
```

### MinIO Issues
```bash
# Access MinIO console
open http://localhost:9001
# Login: minioadmin / minioadmin

# Check MinIO connectivity
curl http://localhost:9000/minio/health/live
```

## Production Deployment

### Security Checklist
- [ ] Change all default passwords in `.env`
- [ ] Set strong `APP_SECRET_KEY`
- [ ] Configure proper CORS origins
- [ ] Set up SSL/TLS certificates
- [ ] Configure firewall rules
- [ ] Set up monitoring and logging

### Environment Variables
```bash
# Production environment variables (don't commit .env to git!)
APP_SECRET_KEY=your-production-secret-key
DATABASE_URL=postgresql://user:pass@prod-db:5432/zynxagi
MINIO_ENDPOINT=your-minio-server.com:9000
OPENAI_API_KEY=your-production-openai-key
ANTHROPIC_API_KEY=your-production-claude-key
```

## Support

**Created by:** Chanont Wankaew  
**Project:** Zynx AGI Core Foundation  
**Repository:** https://github.com/zynx-chanont/ZynxAGI-Project  

For issues and support, please refer to the project repository.