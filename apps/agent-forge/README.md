# Zynx Agent Forge

Independent orchestration control plane inside the ZynxAGI monorepo. It has its own API process, database, environment and deployment lifecycle; it does not replace ZynxAGI's existing MCPDispatcher or move Deeja.

## Components
- FastAPI orchestration API with durable run/project/approval/audit records (SQLite for local development; PostgreSQL-compatible deployment path documented).
- Specialist registry and HTTP adapter for existing ZynxAGI endpoints.
- Hybrid model router for OpenAI-compatible, Anthropic, Google Gemini and local OpenAI-compatible endpoints.
- MCP server exposing scoped project/run/approval tools.
- React operations dashboard.

## Local development
```bash
cd apps/agent-forge
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn agent_forge.api:app --reload --port 8090
```
In another terminal:
```bash
cd apps/agent-forge/dashboard
npm install && npm run dev
```
Set `VITE_API_URL=http://localhost:8090` if needed.

## Safety defaults
- No arbitrary shell, filesystem, deploy or external side-effect tool is exposed.
- High-impact actions require an approval record; approval is a state transition, not automatic execution.
- API binds to localhost by default. Configure authentication and TLS at the deployment boundary before exposing it.
- Provider keys are read from environment variables and never returned by API endpoints.

## ZynxAGI integration
Set `ZYNXAGI_BASE_URL` to the existing ZynxAGI API. The adapter is deliberately isolated; agent availability is reported as unavailable until the configured endpoint responds. Confirm the actual agent API contract before enabling production dispatch.

## Deployment
Use `Dockerfile` and `docker-compose.yml` for an independent service. Mount `/data` persistently. SQLite is suitable for local/single-instance development; use PostgreSQL and migrations before multi-replica production.
