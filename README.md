# Zynx AGI Core Foundation

**Zynx AGI** is an empathy-first AI platform focused on Thai cultural intelligence and emotional understanding. This repository contains the core foundation with IP provenance tracking, database schema, LLM proxy, and automation infrastructure.

## Quick Start

1. **Clone and setup environment:**
   ```bash
   git clone https://github.com/zynx-chanont/ZynxAGI-Project.git
   cd ZynxAGI-Project
   cp .env.example .env
   # Edit .env with your configuration
   ```

2. **Build and run with Docker:**
   ```bash
   make build
   make up
   make migrate
   ```

3. **Test the API:**
   ```bash
   curl http://localhost:8000/health
   curl http://localhost:8000/api/v1/llm/ping
   ```

## Core Components

- **FastAPI Application**: Modern async web framework
- **PostgreSQL + Alembic**: Database with migration support  
- **MinIO**: S3-compatible object storage for artifacts
- **Redis**: Caching and session management
- **LLM Proxy**: Unified interface for OpenAI, Claude, Ollama
- **IP Provenance**: ZPDL metadata tracking with SHA256 hashing

## Architecture

```
app/
├── Dockerfile              # Application container
├── requirements.txt        # Python dependencies  
├── alembic.ini            # Database migration config
├── alembic/               # Migration scripts
│   ├── env.py
│   └── versions/
└── app/                   # Application code
    ├── main.py            # FastAPI entry point
    ├── models.py          # SQLAlchemy models
    ├── core/              # Core utilities
    ├── services/          # Business logic
    └── api/v1/            # API endpoints
```

## Development

See [README.run.md](README.run.md) for detailed development commands and deployment instructions.

## License

© 2025 Chanont Wankaew. All rights reserved. | AaaP™ & Zynx AGI 