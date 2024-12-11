FROM python:3.8-slim

WORKDIR /app

COPY daily-update.py daily-update.py
COPY daily-update-requirements.txt requirements.txt

RUN pip3 install -r requirements.txt

ENTRYPOINT ["python3", "daily-update.py"]
