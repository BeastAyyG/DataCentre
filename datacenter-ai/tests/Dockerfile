FROM python:3.11-slim

WORKDIR /app

# No dependencies needed — uses only stdlib (urllib, json, sys)
COPY tests/test_api.py /app/test_api.py

CMD ["python", "test_api.py"]
