# daily-update.Dockerfile
FROM python:3.8-slim

WORKDIR /app


# 스크립트 복사
COPY initial-es-index.py /app/initial-es-index.py
COPY daily-update.py /app/daily-update.py
COPY daily-update-requirements.txt requirements.txt

# 크론탭 설치 및 설정
RUN apt-get update && apt-get install -y cron

RUN pip install --no-cache-dir -r requirements.txt
# 크론 작업 추가
RUN echo "0 2 * * * python /app/initial-es-index.py && python /app/daily-update.py" > /etc/cron.d/daily-update-cron
RUN chmod 0644 /etc/cron.d/daily-update-cron
RUN crontab /etc/cron.d/daily-update-cron

# 크론 서비스 실행
CMD ["cron", "-f"]
