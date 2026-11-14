FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY agent_forge ./agent_forge
ENV AGENT_FORGE_HOST=0.0.0.0 AGENT_FORGE_PORT=8090 AGENT_FORGE_DB=/data/agent-forge.db
RUN useradd --create-home app && mkdir -p /data && chown -R app:app /app /data
USER app
EXPOSE 8090
CMD ["uvicorn","agent_forge.api:app","--host","0.0.0.0","--port","8090"]
