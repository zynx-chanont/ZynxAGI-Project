# Zynx Agent Forge

Independent orchestration control plane inside the ZynxAGI monorepo. It has its own API process, database, environment and deployment lifecycle; it does not replace ZynxAGI's existing MCPDispatcher or move Deeja.

## Components
- FastAPI orchestration API with durable run/project/approval/audit records (SQLite for local development; PostgreSQL-compatible deployment path documented).
- Specialist registry and HTTP adapter for existing ZynxAGI endpoints.
- Hybrid model router for OpenAI-compatible, Anthropic, Google Gemini and local OpenAI-compatible endpoints.
- MCP server exposing scoped project/run/approval tools.
- React operations dashboard.

## ZynxAGI bridge configuration
Enable the bridge in the ZynxAGI service environment with `ZYNXAGI_ENABLE_AGENT_BRIDGE=true`. Set the same high-entropy `ZYNXAGI_AGENT_API_TOKEN` in both services. Also set `ZYNXAGI_AGENT_STORAGE_KEY` only on ZynxAGI to a separate high-entropy secret; the bridge derives a Fernet-compatible encryption key from it. Restart ZynxAGI and confirm `GET /api/v1/agents/status` reports all three initialized agents before submitting tasks. Keep both services on a private network and do not expose the bridge directly to the public internet.

Agent dispatch uses ZynxAGI's existing `EcosystemManager.process_request()` → `MCPDispatcher.dispatch_request()` path. Slash-command payloads are parsed into the actual specialist message before capability execution.

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

## Security defaults
- All `/api/*` routes fail closed: if `AGENT_FORGE_API_TOKEN` is missing, requests return HTTP 503; an invalid or missing request token returns HTTP 401.
- CORS requires explicit origins; wildcard origins are rejected.
- The dashboard's operator token is entered at runtime and held in React memory only. Never put `AGENT_FORGE_API_TOKEN` or `ZYNXAGI_AGENT_API_TOKEN` in a `VITE_*` variable or client bundle.
- `ZYNXAGI_BASE_URL` must be explicitly configured. The adapter no longer assumes ZynxAGI is on localhost.
- Compose binds the API to host loopback, runs as a non-root user, drops Linux capabilities, enables read-only root filesystem and no-new-privileges, and includes a health check.
- Provider keys are read from backend environment variables and never returned by API endpoints.
- Cloudflare Access should protect both the Vercel Preview dashboard and the API hostname. Keep the ZynxAGI Agent Bridge on a private origin; allow only Agent Forge to reach it.

## Hybrid Cloud Staging (not deployed by this repository)
Target layout:
- **Vercel Preview:** static React dashboard only. Configure the project root as `apps/agent-forge/dashboard`, framework as Vite, build command `npm run build`, and output directory `dist`.
- **Oracle Cloud VM (separate staging VM):** Agent Forge API and ZynxAGI run as separate services. Keep the Agent Forge host port bound to `127.0.0.1:8090`; publish it through a Cloudflare Tunnel hostname protected by Cloudflare Access. Do not open TCP/8090 to the public internet.
- **ZynxAGI Bridge:** use a private service address for `ZYNXAGI_BASE_URL` (for example, a private Docker network service name only if both containers are attached to that same network). Do not use `localhost` unless both processes share the same network namespace.
- **Browser API URL:** set the non-secret `VITE_API_URL` to the protected HTTPS API hostname at Vercel Preview build time. Set `AGENT_FORGE_CORS` to the exact Preview origin; avoid wildcard CORS. A changing Preview URL requires updating the allowlist or using a stable protected preview hostname.
- **Credentials:** provision `AGENT_FORGE_API_TOKEN` as an operator credential on the Agent Forge backend; provision `ZYNXAGI_AGENT_API_TOKEN` on both backend services; provision `ZYNXAGI_AGENT_STORAGE_KEY` only on ZynxAGI. Use the cloud secret store or VM secret injection, not Git, Vercel client variables, shell history, or chat messages. Rotate credentials independently.
- **Storage:** retain the named Docker volume for single-instance staging. Take a backup before replacing/recreating the VM. Do not scale SQLite-backed Agent Forge horizontally.

## Staging acceptance sequence
1. Confirm Oracle VM network, OS updates, firewall, disk, memory, and Docker/Compose versions.
2. Provision the VM and Cloudflare Tunnel without publishing the API port publicly.
3. Configure backend secrets out-of-band; never paste their values into tickets or source.
4. Deploy the two backend services to the staging VM only and verify their health endpoints.
5. Verify Cloudflare Access blocks unauthenticated browser access.
6. Verify API authentication returns 401 for invalid tokens and 503 when the server credential is absent.
7. Verify Agent Forge reaches the authenticated ZynxAGI bridge over the private network.
8. Verify dispatch for Zynx Main, Deeja, and Zynx Metadata; inspect audit records and persistence.
9. Verify Vercel Preview dashboard loads the protected API and that CORS permits only the exact Preview origin.
10. Run negative tests (missing token, invalid token, disallowed Origin, unavailable bridge, timeout) before any production decision.

## Deployment boundaries
This repository change only prepares code and configuration. It does not create a Cloud resource, configure a DNS record, provision secrets, deploy a Vercel Preview, or change Production. SQLite is suitable for local/single-instance staging; use PostgreSQL and migrations before multi-replica production.
