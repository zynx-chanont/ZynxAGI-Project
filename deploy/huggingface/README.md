---
title: ZYNX AGI API
emoji: 🧠
colorFrom: indigo
colorTo: purple
sdk: docker
app_port: 7860
pinned: false
short_description: FastAPI backend for ZYNX AGI
---

# ZYNX AGI API (Hugging Face Space)

FastAPI backend for https://zynx-agi.netlify.app.

Endpoints: `GET /api/v1/health`, `POST /api/v1/chat/message`, `POST /api/v1/cultural/analyze`.

Configure in **Settings → Variables and secrets**:

| Name | Type | Example |
| --- | --- | --- |
| `ALLOWED_ORIGINS` | Variable | `https://zynx-agi.netlify.app` |
| `AI_PROVIDER` | Variable | `google` |
| `GOOGLE_API_KEY` | Secret | free key from https://aistudio.google.com/apikey |
| `SECRET_KEY` | Secret | any long random string |

Without an AI key the API runs in clearly-labelled mock mode (`"mode": "mock"`, `"isMock": true`).

Source of truth: https://github.com/zynx-chanont/ZynxAGI-Project
