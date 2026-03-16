# Build from repo root: docker build -f agent/Dockerfile .
FROM python:3.11-slim
WORKDIR /app
COPY agent/requirements.txt ./agent/
RUN pip install --no-cache-dir -r agent/requirements.txt
COPY agent/ ./agent/
WORKDIR /app/agent
# Agent is interactive; run with: docker-compose run agent python agent.py
CMD ["python", "agent.py"]
