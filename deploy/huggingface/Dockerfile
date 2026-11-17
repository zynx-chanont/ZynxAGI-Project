# Hugging Face Spaces (Docker SDK) image for the ZYNX AGI FastAPI backend.
# Built from the Space repo produced by scripts/deploy_hf_space.sh.
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=7860 \
    DEBUG=false

# Spaces run containers as UID 1000.
RUN useradd -m -u 1000 user
WORKDIR /home/user/app

COPY --chown=user zynx_agi/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY --chown=user zynx_agi ./zynx_agi

USER user
EXPOSE 7860
CMD ["sh", "-c", "uvicorn zynx_agi.main:app --host 0.0.0.0 --port ${PORT:-7860}"]
