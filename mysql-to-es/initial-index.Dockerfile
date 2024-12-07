# initial-index.Dockerfile
FROM python:3.8-slim

WORKDIR /app
COPY initial-es-requirements.txt initial-es-requirements.txt
COPY initial-es-index.py initial-es-index.py

RUN pip install --no-cache-dir -r initial-es-requirements.txt

ENTRYPOINT ["python3", "initial-es-index.py"]

