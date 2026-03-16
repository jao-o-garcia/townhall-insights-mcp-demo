# Build from repo root: docker build -f mcp_server/Dockerfile .
FROM python:3.11-slim
WORKDIR /app
COPY mcp_server/requirements.txt ./mcp_server/
RUN pip install --no-cache-dir -r mcp_server/requirements.txt
COPY mcp_server/ ./mcp_server/
WORKDIR /app/mcp_server
EXPOSE 8002
CMD ["python", "server.py"]
