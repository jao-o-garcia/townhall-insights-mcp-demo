# Build from repo root: docker build -f insights_api/Dockerfile .
FROM python:3.11-slim
WORKDIR /app
COPY insights_api/requirements.txt ./insights_api/
RUN pip install --no-cache-dir -r insights_api/requirements.txt
COPY insights_api/ ./insights_api/
ENV PYTHONPATH=/app
EXPOSE 8001
CMD ["uvicorn", "insights_api.main:app", "--host", "0.0.0.0", "--port", "8001"]
