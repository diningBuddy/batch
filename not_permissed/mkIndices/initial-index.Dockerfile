# initial-index.Dockerfile
FROM python:3.8-slim

WORKDIR /app
COPY initial-es-requirements.txt requirements.txt
COPY initial-es-index.py app.py
COPY wait-for-it.sh /app/wait-for-it.sh

RUN chmod +x /app/wait-for-it.sh

RUN pip install --no-cache-dir -r requirements.txt

# wait-for-it 스크립트를 사용하여 DB 삽입이 완료될 때까지 대기
CMD ["/app/wait-for-it.sh", "restaurant-db-manager:3306", "--", "python", "app.py"]

