# initial-index.Dockerfile
FROM python:3.8-slim

WORKDIR /app
COPY initial-es-requirements.txt requirements.txt
COPY initial-es-index.py app.py

RUN pip install --no-cache-dir -r requirements.txt

ENTRYPOINT ["python", "app.py"]
