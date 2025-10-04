FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y gcc curl git && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY . /app

ENV PYTHONPATH=/app

EXPOSE 8501
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8501/_stcore/health || exit 1

CMD ["python","-m","streamlit","run","interfaces/chat_app_client.py","--server.port=8501","--server.address=0.0.0.0","--server.headless=true","--server.fileWatcherType=auto"]


