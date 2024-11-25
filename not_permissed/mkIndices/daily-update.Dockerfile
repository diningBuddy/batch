FROM python:3.8-slim

WORKDIR /app

# 스크립트 복사
COPY initial-es-index.py /app/initial-es-index.py
COPY daily-update.py /app/daily-update.py
COPY daily-update-requirements.txt requirements.txt

# 필요한 패키지 설치
RUN apt-get update && apt-get install -y cron python3 python3-pip
RUN pip3 install --no-cache-dir -r requirements.txt

# 환경 변수 설정
RUN echo "PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin" > /etc/environment

# 크론 작업 추가
RUN echo "0 2 * * * PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin /usr/local/bin/python3 /app/initial-es-index.py && /usr/local/bin/python3 /app/daily-update.py >> /var/log/daily-update.log 2>&1" > /etc/cron.d/daily-update-cron
RUN chmod 0644 /etc/cron.d/daily-update-cron
RUN crontab /etc/cron.d/daily-update-cron

# 로그 파일 생성 및 권한 설정
RUN touch /var/log/daily-update.log && chmod 0666 /var/log/daily-update.log

# 크론 서비스 실행
CMD ["cron", "-f"]
