FROM python:3.11-slim AS base

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential && \
    apt-get clean && rm -rf /var/lib/apt/lists/*


COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
ENV PYTHONPATH="/app/src/main/python"

EXPOSE 8080

CMD ["uvicorn", "src.main.python.main:app", "--host", "0.0.0.0", "--port", "8080"]
