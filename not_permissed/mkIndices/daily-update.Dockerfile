FROM python:3.8-slim

WORKDIR /app

# 스크립트 복사
COPY initial-es-index.py initial-es-index.py
COPY daily-update.py daily-update.py
COPY daily-update-requirements.txt requirements.txt

RUN pip3 install -r requirements.txt

# 환경 변수 설정
RUN echo "PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin" > /etc/environment

ENTRYPOINT ["python3", "mysql-to-es.py"]
