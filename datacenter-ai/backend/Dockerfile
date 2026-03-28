FROM python:3.11-slim

WORKDIR /app

# Install system deps for prophet/sklearn
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source
COPY backend/app/ ./app/

# Copy ML artifacts (copy from ml/artifacts in monorepo root)
COPY ml/artifacts/ ./ml/artifacts/
COPY ml/model_registry.json ./ml/ 2>/dev/null || true

# Create ml/data/raw dir (even if empty)
RUN mkdir -p ml/data/raw

ENV PYTHONPATH=/app
ENV DATABASE_URL=sqlite:///./datacenter.db

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
